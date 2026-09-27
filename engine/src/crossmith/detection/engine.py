"""Detection engine -- runs every registered adapter against a project and
ranks the results. Deterministic and adapter-driven by default; an
optional local AI assist (see crossmith.ai) can add one extra low-priority
guess when every adapter came back empty or unsure, but never replaces or
outranks a deterministic match. See docs/DECISIONS.md's AI & privacy
section.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from crossmith.adapters.base import DetectionResult
from crossmith.adapters.registry import discover_adapters

if TYPE_CHECKING:
    from crossmith.ai.base import AIEngine

CONFIDENCE_THRESHOLD = 0.6
"""Below this, the UI must show a manual-override screen instead of
silently acting on the top guess. See docs/DECISIONS.md's key risks."""

_MANIFEST_FILES = (
    "pyproject.toml",
    "setup.py",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "Gemfile",
    "composer.json",
)
_EVIDENCE_MAX_CHARS = 4000
_EVIDENCE_MAX_ENTRIES = 200
_MANIFEST_EXCERPT_CHARS = 1500


def scan_project(project_path: Path, ai_engine: AIEngine | None = None) -> list[DetectionResult]:
    """Run every installed adapter against project_path.

    Returns matches, best confidence first. An empty list means no
    installed adapter recognized this project -- not an error.

    If ai_engine is given and every deterministic adapter came back empty
    or unsure, one extra AI-assisted guess is appended (never inserted
    ahead of a confident deterministic match) when the model itself is
    confident enough. ai_engine is entirely optional: pass None (the
    default) to get the exact pre-Phase-4 behavior.
    """
    results = [
        result
        for adapter in discover_adapters()
        if (result := adapter.detect(project_path)).matched
    ]
    results.sort(key=lambda r: r.confidence, reverse=True)

    if ai_engine is not None and needs_manual_review(results):
        hint = ai_engine.assist_detection(project_path, _evidence_text(project_path))
        if hint is not None:
            reasons = [f"AI-assisted guess (Needle, confidence {hint.confidence:.2f})"]
            if hint.reasoning:
                reasons.append(hint.reasoning)
            results.append(
                DetectionResult(
                    matched=True,
                    confidence=hint.confidence,
                    language=hint.language,
                    framework=hint.framework,
                    entry_point=hint.entry_point,
                    dependencies=hint.dependencies,
                    reasons=reasons,
                    metadata={"source": "ai-assist"},
                )
            )
            results.sort(key=lambda r: r.confidence, reverse=True)

    return results


def needs_manual_review(results: list[DetectionResult]) -> bool:
    """True when there's no match, or the best match isn't confident enough
    to act on without asking the user first."""
    return not results or results[0].confidence < CONFIDENCE_THRESHOLD


def _evidence_text(project_path: Path, max_chars: int = _EVIDENCE_MAX_CHARS) -> str:
    """Cheap, human-readable snapshot of a project for the AI hint: a
    top-level file listing plus the contents of any common manifest file
    that's present. Deliberately small and shallow -- this is a nudge for
    an already-ambiguous case, not a code review, and it's the only thing
    about the project that ever reaches the AI engine."""
    lines = ["Files:"]
    try:
        entries = sorted(p.name + ("/" if p.is_dir() else "") for p in project_path.iterdir())
    except OSError:
        entries = []
    lines.extend(f"  {entry}" for entry in entries[:_EVIDENCE_MAX_ENTRIES])

    for manifest in _MANIFEST_FILES:
        manifest_path = project_path / manifest
        if manifest_path.is_file():
            try:
                content = manifest_path.read_text(errors="replace")[:_MANIFEST_EXCERPT_CHARS]
            except OSError:
                continue
            lines.append(f"\n{manifest}:\n{content}")

    return "\n".join(lines)[:max_chars]
