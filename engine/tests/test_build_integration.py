"""Real, end-to-end build tests — these actually invoke Nuitka/PyInstaller
and run the resulting binary. Slow (30-60s+ each), so excluded from the
default test run; opt in with `pytest -m slow`.
"""

import subprocess
from pathlib import Path

import pytest

from crossmith.build.orchestrator import run_build

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


@pytest.mark.slow
def test_real_build_produces_a_working_binary(tmp_path):
    project = EXAMPLES_DIR / "python-cli"
    assert project.is_dir(), f"expected example project at {project}"

    result = run_build(project, target_platform="linux")

    assert result.test_result.success, result.test_result.logs
    assert result.build_result.success, result.build_result.logs
    assert len(result.build_result.artifact_paths) == 1

    artifact = result.build_result.artifact_paths[0]
    assert artifact.exists()
    assert artifact.stat().st_mode & 0o111, "artifact should be executable"

    proc = subprocess.run(
        [str(artifact), "Integration"], capture_output=True, text=True, check=False
    )
    assert proc.returncode == 0
    assert "Hello, Integration!" in proc.stdout


@pytest.mark.slow
def test_real_build_falls_back_to_pyinstaller_without_patchelf(monkeypatch, tmp_path):
    """Simulates Nuitka's Linux onefile mode missing its 'patchelf' system
    dependency, without actually uninstalling it from the machine running
    the tests. See python_adapter.py's fallback logic — this exact
    scenario was found by running a real build in a container without
    patchelf, not written speculatively."""
    from crossmith.packaging import BACKENDS

    project = EXAMPLES_DIR / "python-cli"
    original_package = BACKENDS["nuitka"].package

    def fake_nuitka_failure(*args, **kwargs):
        from crossmith.packaging.base import PackageResult

        return PackageResult(
            success=False,
            logs="FATAL: Error, standalone mode on Linux requires 'patchelf' to be installed.",
            error="Nuitka failed",
        )

    monkeypatch.setattr(BACKENDS["nuitka"], "package", fake_nuitka_failure)
    try:
        result = run_build(project, target_platform="linux")
    finally:
        monkeypatch.setattr(BACKENDS["nuitka"], "package", original_package)

    assert result.build_result.success
    assert "patchelf" in result.build_result.logs
    assert "PyInstaller instead" in result.build_result.logs
