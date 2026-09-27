"""PyInstaller packaging backend — fast, widely compatible, the fallback
to Nuitka's default. See docs/DECISIONS.md."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from crossmith.packaging.base import PackageResult, PackagingBackend


class PyInstallerBackend(PackagingBackend):
    name = "pyinstaller"

    def is_available(self) -> bool:
        return True  # installed on demand into the build venv by the adapter

    def package(
        self,
        entry_point: Path,
        env_python: Path,
        output_dir: Path,
        *,
        app_name: str,
        icon: Path | None = None,
    ) -> PackageResult:
        output_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as tmp:
            args = [
                str(env_python),
                "-m",
                "PyInstaller",
                "--onefile",
                "--name",
                app_name,
                "--distpath",
                str(output_dir),
                "--workpath",
                tmp,
                "--specpath",
                tmp,
            ]
            if icon is not None:
                args += ["--icon", str(icon)]
            args.append(str(entry_point))

            result = subprocess.run(
                args,
                cwd=entry_point.parent,
                capture_output=True,
                text=True,
                check=False,
            )

        logs = result.stdout + result.stderr
        if result.returncode != 0:
            return PackageResult(success=False, logs=logs, error="PyInstaller failed")

        suffix = ".exe" if sys.platform == "win32" else ""
        artifact = output_dir / f"{app_name}{suffix}"
        if not artifact.exists():
            return PackageResult(
                success=False,
                logs=logs,
                error="PyInstaller reported success but no artifact was found",
            )
        return PackageResult(success=True, artifact_path=artifact, logs=logs)
