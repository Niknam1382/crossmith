"""Needle-backed AIEngine.

Uses the `cactus-needle` package — a 14MB local tool-calling model
(github.com/cactus-compute/needle) — an optional dependency; see
pyproject.toml's `ai` extra. `pip install crossmith-engine[ai]` to get it.

Import is lazy everywhere: importing *this module* is cheap even without
`cactus-needle` installed, and `import needle` itself only happens inside
a call that's already been gated by is_available(). A machine without
`cactus-needle` installed behaves identically to AI assist being off.

Privacy note, precisely stated (see docs/DECISIONS.md): the model weights
(~14MB) are fetched from Hugging Face and cached locally the first time
Needle is used — that is the one network call anywhere in this module,
and it carries no project data, only a request for the model itself. The
evidence text built from the user's project (a file listing / manifest
excerpt) is what gets passed to the model, and that inference is fully
local — nothing about the project is sent anywhere. On a machine with no
internet access at all, that one-time weights fetch fails fast (tested:
huggingface_hub raises LocalEntryNotFoundError in well under a second,
it does not hang) and assist_detection/explain_build_failure just return
None, same as if AI assist were disabled.
"""

from __future__ import annotations

import importlib.util
import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from crossmith.ai.base import AIDetectionHint, AIEngine

logger = logging.getLogger("crossmith.ai")

CONFIDENCE_THRESHOLD = 0.65
"""Below this, a Needle result is discarded outright rather than surfaced
as a low-confidence hint. Needle's own docs put it plainly: "pick a
threshold for your product, act at or above it, re-ask or route to a
bigger model below it" — here, "below it" means "fall back to the
deterministic-only result," since there is no bigger model to route to."""

INFERENCE_TIMEOUT_SECONDS = 20
"""Generous on purpose. Once weights are cached, Needle is meant to run in
well under a second; this timeout exists only to guarantee a scan or
build can never hang on a slow first-time weights download or an
unexpected stall — it must always be safe to just move on without AI."""


class _ProjectHint(BaseModel):
    """Extraction target for assist_detection — passed to Needle as its
    one declared tool, so its `arguments` are exactly this shape."""

    language: str
    framework: str | None = None
    entry_point: str | None = None
    dependencies: list[str] = []


class _FailureExplanation(BaseModel):
    """Extraction target for explain_build_failure."""

    plain_language_explanation: str
    suggested_fix: str | None = None


class NeedleEngine(AIEngine):
    """See ai/base.py:AIEngine for the contract every method here honors."""

    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="crossmith-ai")

    def is_available(self) -> bool:
        return importlib.util.find_spec("needle") is not None

    def assist_detection(self, project_path: Path, evidence: str) -> AIDetectionHint | None:
        del project_path  # not used directly; evidence is the caller-built summary
        response = self._run_guarded(self._complete_detection, evidence)
        if response is None:
            return None

        confidence = response.get("confidence")
        if (
            response.get("type") != "call"
            or not response.get("function_calls")
            or confidence is None
            or confidence < CONFIDENCE_THRESHOLD
        ):
            return None

        args = response["function_calls"][0]["arguments"]
        language = args.get("language")
        if not language:
            return None
        return AIDetectionHint(
            language=language,
            framework=args.get("framework"),
            entry_point=args.get("entry_point"),
            dependencies=args.get("dependencies") or [],
            confidence=confidence,
            reasoning=response.get("reasoning"),
        )

    def explain_build_failure(self, error_text: str) -> str | None:
        response = self._run_guarded(self._complete_explanation, error_text)
        if response is None:
            return None

        confidence = response.get("confidence")
        if response.get("type") != "call" or not response.get("function_calls"):
            return None
        if confidence is not None and confidence < CONFIDENCE_THRESHOLD:
            return None

        args = response["function_calls"][0]["arguments"]
        explanation = args.get("plain_language_explanation")
        if not explanation:
            return None
        fix = args.get("suggested_fix")
        return f"{explanation} {fix}" if fix else explanation

    # -- internals ---------------------------------------------------------

    def _run_guarded(self, fn: Any, arg: str) -> dict[str, Any] | None:
        """Runs fn(arg) with a hard timeout, catching *everything* — a
        missing package, no network for the first-time weights download,
        a malformed response, anything. This is the one place the
        "never load-bearing" rule is actually enforced."""
        if not self.is_available():
            return None
        try:
            future = self._executor.submit(fn, arg)
            return future.result(timeout=INFERENCE_TIMEOUT_SECONDS)
        except FutureTimeoutError:
            logger.warning("Needle call timed out after %ss; continuing without AI assist", INFERENCE_TIMEOUT_SECONDS)
            return None
        except Exception:
            logger.exception("Needle call failed; continuing without AI assist")
            return None

    @staticmethod
    def _complete_detection(evidence: str) -> dict[str, Any]:
        import needle

        agent = needle.Needle(tools=[_ProjectHint])
        return agent.complete(evidence, max_new_tokens=256)

    @staticmethod
    def _complete_explanation(error_text: str) -> dict[str, Any]:
        import needle

        agent = needle.Needle(tools=[_FailureExplanation])
        # Build error text/logs can be long; Needle's context window is
        # small (256 tokens) by design, so truncate well before that.
        return agent.complete(error_text[:2000], max_new_tokens=256)
