"""The first-party Python adapter: detection, dependency install, tests,
and build for plain Python projects. Registered under the
`crossmith.adapters` entry-point group — see pyproject.toml.
"""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

from crossmith.adapters.base import Adapter, BuildResult, DetectionResult
from crossmith.build.venv_manager import create_venv, pip_install, venv_python
from crossmith.packaging import BACKENDS
from crossmith.settings import Settings

ENTRY_POINT_CANDIDATES = ("main.py", "app.py", "run.py", "__main__.py", "cli.py")

_MISSING_SYSTEM_DEP_MARKERS = ("requires 'patchelf' to be installed",)


def _is_missing_system_dependency(logs: str) -> bool:
    return any(marker in logs for marker in _MISSING_SYSTEM_DEP_MARKERS)


def _missing_system_dependency_hint(logs: str) -> str:
    if "patchelf" in logs:
        return (
            "Nuitka's onefile mode on Linux needs the 'patchelf' system "
            "tool. Install it (e.g. `apt install patchelf`, "
            "`dnf install patchelf`) for full Nuitka support."
        )
    return "A required system tool is missing — check the log above for which one."


class PythonAdapter(Adapter):
    name = "python"
    packaging_backends = ("nuitka", "pyinstaller")

    def detect(self, project_path: Path) -> DetectionResult:
        entry_point, entry_reason = self._find_entry_point(project_path)
        if entry_point is None:
            return DetectionResult(matched=False, confidence=0.0, language="python")

        dependencies, req_file, dep_reason = self._find_dependencies(project_path)
        has_pyproject = (project_path / "pyproject.toml").is_file()

        confidence = 0.6
        if entry_point.name in ("main.py", "__main__.py"):
            confidence += 0.2
        if has_pyproject:
            confidence += 0.1
        if dependencies:
            confidence += 0.05
        confidence = min(confidence, 0.98)
        confidence = round(confidence, 2)

        reasons = [entry_reason, dep_reason]
        if has_pyproject:
            reasons.append("pyproject.toml present")

        return DetectionResult(
            matched=True,
            confidence=confidence,
            language="python",
            entry_point=str(entry_point.relative_to(project_path)),
            dependencies=dependencies,
            metadata={"requirements_file": str(req_file) if req_file else None},
            reasons=reasons,
        )

    def install_dependencies(self, project_path: Path, env_path: Path) -> None:
        create_venv(env_path)
        _, req_file, _ = self._find_dependencies(project_path)
        if req_file is not None:
            pip_install(env_path, requirements_file=req_file)
            return

        pyproject = project_path / "pyproject.toml"
        if pyproject.is_file():
            data = tomllib.loads(pyproject.read_text())
            deps = data.get("project", {}).get("dependencies", [])
            if deps:
                pip_install(env_path, *deps)

    def run_tests(self, project_path: Path, env_path: Path) -> BuildResult:
        has_tests = any(project_path.glob("test_*.py")) or (project_path / "tests").is_dir()
        if not has_tests:
            return BuildResult(success=True, logs="No tests found — skipping.")

        pip_install(env_path, "pytest")
        python = venv_python(env_path)
        result = subprocess.run(
            [str(python), "-m", "pytest", "-q"],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=False,
        )
        return BuildResult(
            success=result.returncode == 0,
            logs=result.stdout + result.stderr,
            error=None if result.returncode == 0 else "Tests failed",
        )

    def build(
        self,
        project_path: Path,
        env_path: Path,
        target_platform: str,
        output_dir: Path,
    ) -> BuildResult:
        entry_point, _ = self._find_entry_point(project_path)
        if entry_point is None:
            return BuildResult(success=False, error="No entry point found")

        backend_name = Settings.load().default_packaging_backend
        backend = BACKENDS.get(backend_name, BACKENDS["pyinstaller"])
        if not backend.is_available():
            backend = BACKENDS["pyinstaller"]

        pip_install(env_path, backend.name)
        result = backend.package(
            entry_point=entry_point,
            env_python=venv_python(env_path),
            output_dir=output_dir,
            app_name=project_path.name,
        )

        if not result.success and backend.name != "pyinstaller" and _is_missing_system_dependency(result.logs):
            # A packaging backend can need OS-level tooling that isn't
            # always installed (e.g. Nuitka's onefile mode needs patchelf
            # on Linux) — fall back to PyInstaller rather than failing the
            # whole build over one missing system package. Discovered by
            # actually running this against a real project, not assumed.
            fallback = BACKENDS["pyinstaller"]
            pip_install(env_path, fallback.name)
            fallback_result = fallback.package(
                entry_point=entry_point,
                env_python=venv_python(env_path),
                output_dir=output_dir,
                app_name=project_path.name,
            )
            if fallback_result.success:
                fallback_result.logs = (
                    f"Note: {backend.name} needs a system tool that isn't "
                    f"installed here, so Crossmith used PyInstaller instead. "
                    f"{_missing_system_dependency_hint(result.logs)}\n\n"
                    f"--- {backend.name} log ---\n{result.logs}\n\n"
                    f"--- pyinstaller log ---\n{fallback_result.logs}"
                )
            result = fallback_result

        return BuildResult(
            success=result.success,
            artifact_paths=[result.artifact_path] if result.artifact_path else [],
            logs=result.logs,
            error=result.error,
        )

    def suggest_fix(self, error: BuildResult) -> str | None:
        logs = error.logs or ""
        if _is_missing_system_dependency(logs):
            return _missing_system_dependency_hint(logs)
        if "ModuleNotFoundError" in logs or "No module named" in logs:
            return (
                "A dependency wasn't installed. Check that everything your "
                "code imports is listed in requirements.txt or "
                "pyproject.toml's dependencies."
            )
        return None

    @staticmethod
    def _find_entry_point(project_path: Path) -> tuple[Path | None, str]:
        for name in ENTRY_POINT_CANDIDATES:
            candidate = project_path / name
            if candidate.is_file():
                return candidate, f"found {name} at project root"

        py_files = [p for p in project_path.glob("*.py") if p.is_file()]
        if len(py_files) == 1:
            return py_files[0], f"only one .py file at project root ({py_files[0].name})"

        return None, "no recognizable Python entry point"

    @staticmethod
    def _find_dependencies(project_path: Path) -> tuple[list[str], Path | None, str]:
        requirements = project_path / "requirements.txt"
        if requirements.is_file():
            deps = [
                line.strip()
                for line in requirements.read_text().splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            return deps, requirements, f"requirements.txt found ({len(deps)} package(s))"

        pyproject = project_path / "pyproject.toml"
        if pyproject.is_file():
            data = tomllib.loads(pyproject.read_text())
            deps = data.get("project", {}).get("dependencies", [])
            if deps:
                return deps, None, f"pyproject.toml [project.dependencies] ({len(deps)} package(s))"

        return [], None, "no dependency file found"
