"""The interface the rest of the engine uses to talk to a local AI assist.

An AI backend is always optional and never load-bearing: every caller must
keep working exactly as it does today if no backend is installed, if the
user has it turned off, or if it errors or times out for any reason. See
docs/DECISIONS.md's "AI & privacy" section for the reasoning behind that
rule — it is a hard constraint, not a style preference.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AIDetectionHint:
    """One AI-assisted guess about an otherwise-ambiguous project.

    Always a *hint*: the detection engine decides whether it's confident
    enough to surface, and it is only ever asked for in the first place
    when every deterministic adapter already came back empty or unsure —
    see detection/engine.py. It never overrides a confident deterministic
    match.
    """

    language: str
    framework: str | None = None
    entry_point: str | None = None
    dependencies: list[str] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str | None = None


class AIEngine(ABC):
    """One local AI backend. Needle (needle_engine.NeedleEngine) is the
    only implementation today; the interface exists so a different local
    backend could be swapped in later without touching any caller.
    """

    @abstractmethod
    def is_available(self) -> bool:
        """Cheap, synchronous check — must not download or import anything
        heavy, and must never raise. False means every other method on
        this instance would also fail, so callers should skip calling
        them entirely rather than pay for a call that just returns None.
        """

    @abstractmethod
    def assist_detection(self, project_path: Path, evidence: str) -> AIDetectionHint | None:
        """Best-effort guess from a small amount of free-text evidence
        (a file listing, a manifest excerpt — see
        detection/engine.py's _evidence_text). Returns None on any
        failure, timeout, or low-confidence result. Must not raise.
        """

    @abstractmethod
    def explain_build_failure(self, error_text: str) -> str | None:
        """Best-effort plain-language explanation of a build failure, to
        show alongside (never instead of) the raw error. Returns None on
        any failure — the caller already has error_text as the fallback,
        this is purely additive. Must not raise.
        """
