"""Local AI assist (Phase 4 -- "Needle").

Everything here is optional and off by default; see base.py's AIEngine
for the contract and docs/DECISIONS.md for why. get_ai_engine() is the
one entry point callers (the API layer) need.
"""

from __future__ import annotations

from crossmith.ai.base import AIDetectionHint, AIEngine
from crossmith.ai.needle_engine import NeedleEngine
from crossmith.settings import Settings

__all__ = ["AIDetectionHint", "AIEngine", "NeedleEngine", "get_ai_engine"]


def get_ai_engine(settings: Settings) -> AIEngine | None:
    """None whenever AI assist shouldn't run: disabled in settings, or the
    `cactus-needle` optional dependency isn't installed. Callers pass the
    result straight through to scan_project()/run_build() -- both already
    treat a None engine as "behave exactly as if AI didn't exist."
    """
    if not settings.ai_assist_enabled:
        return None
    engine = NeedleEngine()
    return engine if engine.is_available() else None
