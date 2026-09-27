"""Tests for crossmith.ai. Everything here is mocked — no real network
call or model download happens in this suite. See test_build_integration.py
for the (marked slow, opt-in) tests that touch real external tools; there
is no equivalent for Needle because a real run needs Hugging Face access
this test environment intentionally doesn't have. See docs/DECISIONS.md's
AI & privacy section and docs/guides/ai-assist.md for what *was* verified
by hand: `pip install cactus-needle` and `import needle` succeed, and a
real `agent.complete(...)` call without network access to Hugging Face
raises `huggingface_hub.errors.LocalEntryNotFoundError` quickly rather
than hanging — exactly the failure mode `_run_guarded` below is built to
absorb.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from crossmith.ai import get_ai_engine
from crossmith.ai.needle_engine import NeedleEngine
from crossmith.detection.engine import scan_project
from crossmith.settings import Settings


def _response(confidence: float, **arguments: object) -> dict:
    return {
        "type": "call",
        "success": True,
        "function_calls": [{"name": "_ProjectHint", "arguments": arguments}],
        "reasoning": "test reasoning",
        "confidence": confidence,
    }


# -- get_ai_engine -----------------------------------------------------------


def test_get_ai_engine_none_when_disabled():
    assert get_ai_engine(Settings(ai_assist_enabled=False)) is None


def test_get_ai_engine_none_when_enabled_but_not_installed(monkeypatch):
    monkeypatch.setattr(NeedleEngine, "is_available", lambda self: False)
    assert get_ai_engine(Settings(ai_assist_enabled=True)) is None


def test_get_ai_engine_returns_engine_when_enabled_and_installed(monkeypatch):
    monkeypatch.setattr(NeedleEngine, "is_available", lambda self: True)
    engine = get_ai_engine(Settings(ai_assist_enabled=True))
    assert isinstance(engine, NeedleEngine)


# -- NeedleEngine.assist_detection -------------------------------------------


def test_assist_detection_returns_none_when_not_installed(monkeypatch):
    engine = NeedleEngine()
    monkeypatch.setattr(engine, "is_available", lambda: False)
    assert engine.assist_detection(Path("/tmp"), "evidence") is None


def test_assist_detection_returns_hint_above_threshold(monkeypatch):
    engine = NeedleEngine()
    monkeypatch.setattr(engine, "is_available", lambda: True)
    monkeypatch.setattr(
        NeedleEngine,
        "_complete_detection",
        staticmethod(lambda evidence: _response(0.9, language="rust", entry_point="src/main.rs")),
    )

    hint = engine.assist_detection(Path("/tmp"), "evidence")

    assert hint is not None
    assert hint.language == "rust"
    assert hint.entry_point == "src/main.rs"
    assert hint.confidence == 0.9


def test_assist_detection_discards_result_below_threshold(monkeypatch):
    engine = NeedleEngine()
    monkeypatch.setattr(engine, "is_available", lambda: True)
    monkeypatch.setattr(
        NeedleEngine,
        "_complete_detection",
        staticmethod(lambda evidence: _response(0.2, language="rust")),
    )

    assert engine.assist_detection(Path("/tmp"), "evidence") is None


def test_assist_detection_discards_empty_call(monkeypatch):
    """An empty function_calls list is Needle's documented way of saying
    "no declared tool fits" — must be treated the same as no result."""
    engine = NeedleEngine()
    monkeypatch.setattr(engine, "is_available", lambda: True)
    empty = {"type": "call", "function_calls": [], "confidence": 0.99}
    monkeypatch.setattr(NeedleEngine, "_complete_detection", staticmethod(lambda evidence: empty))

    assert engine.assist_detection(Path("/tmp"), "evidence") is None


def test_assist_detection_swallows_exceptions(monkeypatch):
    engine = NeedleEngine()
    monkeypatch.setattr(engine, "is_available", lambda: True)

    def boom(evidence: str) -> dict:
        raise RuntimeError("no internet, no cached weights")

    monkeypatch.setattr(NeedleEngine, "_complete_detection", staticmethod(boom))

    assert engine.assist_detection(Path("/tmp"), "evidence") is None


def test_assist_detection_times_out_instead_of_hanging(monkeypatch):
    engine = NeedleEngine()
    monkeypatch.setattr(engine, "is_available", lambda: True)
    monkeypatch.setattr("crossmith.ai.needle_engine.INFERENCE_TIMEOUT_SECONDS", 0.05)

    def slow(evidence: str) -> dict:
        time.sleep(1)
        return _response(0.9, language="rust")

    monkeypatch.setattr(NeedleEngine, "_complete_detection", staticmethod(slow))

    started = time.monotonic()
    assert engine.assist_detection(Path("/tmp"), "evidence") is None
    assert time.monotonic() - started < 1, "should return long before the slow call finishes"


# -- NeedleEngine.explain_build_failure --------------------------------------


def test_explain_build_failure_returns_text(monkeypatch):
    engine = NeedleEngine()
    monkeypatch.setattr(engine, "is_available", lambda: True)
    response = {
        "type": "call",
        "function_calls": [
            {
                "name": "_FailureExplanation",
                "arguments": {
                    "plain_language_explanation": "Nuitka needs patchelf on Linux.",
                    "suggested_fix": "sudo apt install patchelf",
                },
            }
        ],
        "confidence": 0.8,
    }
    monkeypatch.setattr(NeedleEngine, "_complete_explanation", staticmethod(lambda text: response))

    explanation = engine.explain_build_failure("FATAL: patchelf not found")

    assert explanation is not None
    assert "patchelf" in explanation
    assert "sudo apt install patchelf" in explanation


def test_explain_build_failure_none_when_not_installed(monkeypatch):
    engine = NeedleEngine()
    monkeypatch.setattr(engine, "is_available", lambda: False)
    assert engine.explain_build_failure("some error") is None


# -- wired into scan_project --------------------------------------------------


class _FakeAIEngine:
    def __init__(self, hint):
        self._hint = hint
        self.calls = 0

    def is_available(self) -> bool:
        return True

    def assist_detection(self, project_path, evidence):
        self.calls += 1
        return self._hint

    def explain_build_failure(self, error_text):
        return None


def test_scan_project_ignores_ai_hint_when_deterministic_match_is_confident(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hi')")
    from crossmith.ai.base import AIDetectionHint

    fake = _FakeAIEngine(AIDetectionHint(language="rust", confidence=0.99))

    results = scan_project(tmp_path, ai_engine=fake)

    assert fake.calls == 0, "AI must not be consulted when a deterministic adapter is confident"
    assert len(results) == 1
    assert results[0].language == "python"


def test_scan_project_appends_ai_hint_when_nothing_matched(tmp_path: Path):
    from crossmith.ai.base import AIDetectionHint

    fake = _FakeAIEngine(AIDetectionHint(language="rust", confidence=0.9, entry_point="src/main.rs"))

    results = scan_project(tmp_path, ai_engine=fake)

    assert fake.calls == 1
    assert len(results) == 1
    assert results[0].language == "rust"
    assert results[0].metadata == {"source": "ai-assist"}


def test_scan_project_low_confidence_ai_hint_still_needs_review(tmp_path: Path):
    from crossmith.ai.base import AIDetectionHint
    from crossmith.detection.engine import needs_manual_review

    fake = _FakeAIEngine(AIDetectionHint(language="rust", confidence=0.4))

    results = scan_project(tmp_path, ai_engine=fake)

    assert needs_manual_review(results) is True


def test_scan_project_none_engine_behaves_as_before(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hi')")
    results = scan_project(tmp_path, ai_engine=None)
    assert len(results) == 1
    assert results[0].language == "python"


# -- wired into run_build's error_explanation fallback ------------------------


def test_run_build_falls_back_to_ai_explanation_when_suggest_fix_has_none(monkeypatch, tmp_path):
    from crossmith.adapters.base import Adapter, BuildResult, DetectionResult
    from crossmith.build import orchestrator

    class _StubAdapter(Adapter):
        name = "stub"

        def detect(self, project_path):
            return DetectionResult(matched=True, confidence=1.0, language="stub")

        def install_dependencies(self, project_path, env_path):
            pass

        def run_tests(self, project_path, env_path):
            return BuildResult(success=True)

        def build(self, project_path, env_path, target_platform, output_dir):
            return BuildResult(success=False, error="boom", logs="raw failure log")

        def suggest_fix(self, error):
            return None

    monkeypatch.setattr(orchestrator, "discover_adapters", lambda: [_StubAdapter()])

    class _FakeAI:
        def explain_build_failure(self, error_text):
            assert error_text == "raw failure log"
            return "plain language explanation"

    result = orchestrator.run_build(tmp_path, run_tests=False, ai_engine=_FakeAI())

    assert result.build_result.error_explanation == "plain language explanation"


def test_run_build_prefers_adapter_suggest_fix_over_ai(monkeypatch, tmp_path):
    from crossmith.adapters.base import Adapter, BuildResult, DetectionResult
    from crossmith.build import orchestrator

    class _StubAdapter(Adapter):
        name = "stub"

        def detect(self, project_path):
            return DetectionResult(matched=True, confidence=1.0, language="stub")

        def install_dependencies(self, project_path, env_path):
            pass

        def run_tests(self, project_path, env_path):
            return BuildResult(success=True)

        def build(self, project_path, env_path, target_platform, output_dir):
            return BuildResult(success=False, error="boom", logs="raw failure log")

        def suggest_fix(self, error):
            return "adapter's own suggestion"

    monkeypatch.setattr(orchestrator, "discover_adapters", lambda: [_StubAdapter()])

    class _FakeAI:
        def explain_build_failure(self, error_text):
            pytest.fail("AI should not be consulted when suggest_fix already answered")

    result = orchestrator.run_build(tmp_path, run_tests=False, ai_engine=_FakeAI())

    assert result.build_result.error_explanation == "adapter's own suggestion"
