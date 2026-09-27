"""Nuitka packaging backend — the default (see docs/DECISIONS.md). Compiles
to real C, then native code, which avoids most of the antivirus
false-positive problems bytecode-bundling tools are known for."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from crossmith.packaging.base import PackageResult, PackagingBackend


class NuitkaBackend(PackagingBackend):
    name = "nuitka"

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
        is_windows = sys.platform == "win32"
        output_filename = f"{app_name}.exe" if is_windows else app_name

        args = [
            str(env_python),
            "-m",
            "nuitka",
            "--onefile",
            f"--output-dir={output_dir}",
            f"--output-filename={output_filename}",
            "--assume-yes-for-downloads",
        ]
        if icon is not None:
            flag = "--windows-icon-from-ico" if is_windows else "--linux-icon"
            args.append(f"{flag}={icon}")
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
            return PackageResult(success=False, logs=logs, error="Nuitka failed")

        artifact = output_dir / output_filename
        if not artifact.exists():
            return PackageResult(
                success=False,
                logs=logs,
                error="Nuitka reported success but no artifact was found",
            )
        return PackageResult(success=True, artifact_path=artifact, logs=logs)
