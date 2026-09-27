"""Build orchestrator — ties detection, dependency install, tests, and
packaging into the single flow the API exposes as POST /projects/build.
"""

from __future__ import annotations

import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from crossmith.adapters.base import Adapter, BuildResult
from crossmith.adapters.registry import discover_adapters

if TYPE_CHECKING:
    from crossmith.ai.base import AIEngine

BUILDS_ROOT = Path.home() / ".crossmith" / "builds"


@dataclass
class OrchestratedBuildResult:
    build_id: str
    adapter_name: str
    test_result: BuildResult
    build_result: BuildResult


def _select_adapter(project_path: Path, adapter_name: str | None) -> Adapter | None:
    for adapter in discover_adapters():
        if adapter_name is not None:
            if adapter.name == adapter_name:
                return adapter
            continue
        if adapter.detect(project_path).matched:
            return adapter
    return None


def _default_target_platform() -> str:
    return {"win32": "windows", "darwin": "macos"}.get(sys.platform, "linux")


def run_build(
    project_path: Path,
    *,
    adapter_name: str | None = None,
    target_platform: str | None = None,
    run_tests: bool = True,
    ai_engine: AIEngine | None = None,
) -> OrchestratedBuildResult:
    """Run a full build: install deps, optionally test, then package.

    Raises ValueError if no adapter recognizes the project — callers (the
    API layer) turn that into a 4xx, not a 500.

    ai_engine is entirely optional (default None, the pre-Phase-4
    behavior). It's only ever consulted as a last resort, after a failed
    build, and only if the adapter's own suggest_fix() had nothing to
    say — see adapters/base.py's Adapter.suggest_fix docstring.
    """
    adapter = _select_adapter(project_path, adapter_name)
    if adapter is None:
        raise ValueError(f"No adapter recognized {project_path}")

    build_id = uuid.uuid4().hex[:12]
    build_dir = BUILDS_ROOT / build_id
    env_path = build_dir / "env"
    output_dir = build_dir / "dist"

    adapter.install_dependencies(project_path, env_path)

    test_result = BuildResult(success=True, logs="Skipped.")
    if run_tests:
        test_result = adapter.run_tests(project_path, env_path)
        if not test_result.success:
            return OrchestratedBuildResult(
                build_id=build_id,
                adapter_name=adapter.name,
                test_result=test_result,
                build_result=BuildResult(success=False, error="Skipped — tests failed"),
            )

    build_result = adapter.build(
        project_path,
        env_path,
        target_platform or _default_target_platform(),
        output_dir,
    )
    if not build_result.success and build_result.error_explanation is None:
        build_result.error_explanation = adapter.suggest_fix(build_result)
        if build_result.error_explanation is None and ai_engine is not None:
            error_text = build_result.logs or build_result.error or ""
            build_result.error_explanation = ai_engine.explain_build_failure(error_text)

    return OrchestratedBuildResult(
        build_id=build_id,
        adapter_name=adapter.name,
        test_result=test_result,
        build_result=build_result,
    )
