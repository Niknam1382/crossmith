"""Detection engine — runs every registered adapter against a project and
ranks the results. Deterministic and adapter-driven; no AI required.
"""

from __future__ import annotations

from pathlib import Path

from crossmith.adapters.base import DetectionResult
from crossmith.adapters.registry import discover_adapters

CONFIDENCE_THRESHOLD = 0.6
"""Below this, the UI must show a manual-override screen instead of
silently acting on the top guess. See docs/DECISIONS.md's key risks."""


def scan_project(project_path: Path) -> list[DetectionResult]:
    """Run every installed adapter against project_path.

    Returns only matches, best confidence first. An empty list means no
    installed adapter recognized this project — not an error.
    """
    results = [
        result
        for adapter in discover_adapters()
        if (result := adapter.detect(project_path)).matched
    ]
    return sorted(results, key=lambda r: r.confidence, reverse=True)


def needs_manual_review(results: list[DetectionResult]) -> bool:
    """True when there's no match, or the best match isn't confident enough
    to act on without asking the user first."""
    return not results or results[0].confidence < CONFIDENCE_THRESHOLD
