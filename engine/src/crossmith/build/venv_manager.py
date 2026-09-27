"""Creates and manages the isolated virtualenv used for a single build.

Every build gets its own venv under a build-scoped directory — never the
engine's own environment — so one project's dependencies can never collide
with another's, or with Crossmith's. See docs/DECISIONS.md's sandboxing
decision.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def create_venv(env_path: Path) -> None:
    if env_path.exists():
        return  # already created for this build
    subprocess.run(
        [sys.executable, "-m", "venv", str(env_path)],
        check=True,
        capture_output=True,
        text=True,
    )


def venv_python(env_path: Path) -> Path:
    if sys.platform == "win32":
        return env_path / "Scripts" / "python.exe"
    return env_path / "bin" / "python"


def pip_install(
    env_path: Path,
    *packages: str,
    requirements_file: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Install packages and/or a requirements file into env_path.

    Raises CalledProcessError on failure — callers decide how to turn that
    into a BuildResult with a human-readable explanation.
    """
    python = venv_python(env_path)
    args = [str(python), "-m", "pip", "install", "--quiet"]
    if requirements_file is not None:
        args += ["-r", str(requirements_file)]
    args += list(packages)
    return subprocess.run(args, check=True, capture_output=True, text=True)
