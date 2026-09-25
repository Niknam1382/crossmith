#!/usr/bin/env python3
"""Freeze the Python engine into a real, standalone sidecar binary for a
release build.

Not needed for day-to-day development — scripts/dev.sh drops a thin wrapper
script for that. Run this before `npm run tauri build`, or let the release
CI workflow run it for every platform in the build matrix.

Usage:
    python scripts/build_sidecar.py
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = REPO_ROOT / "engine"
BIN_DIR = REPO_ROOT / "desktop" / "src-tauri" / "binaries"


def rustc_target_triple() -> str:
    result = subprocess.run(
        ["rustc", "-vV"], capture_output=True, text=True, check=True
    )
    for line in result.stdout.splitlines():
        if line.startswith("host:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("could not parse target triple from `rustc -vV`")


def main() -> None:
    triple = rustc_target_triple()
    suffix = ".exe" if platform.system() == "Windows" else ""
    dist_dir = ENGINE_DIR / "dist-sidecar"

    print(f"==> Freezing engine for {triple}")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--name",
            "crossmith-engine",
            "--distpath",
            str(dist_dir),
            "--workpath",
            str(ENGINE_DIR / "build-sidecar"),
            "--specpath",
            str(ENGINE_DIR),
            str(ENGINE_DIR / "src" / "crossmith" / "api" / "main.py"),
        ],
        check=True,
        cwd=ENGINE_DIR,
    )

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    src = dist_dir / f"crossmith-engine{suffix}"
    dest = BIN_DIR / f"crossmith-engine-{triple}{suffix}"
    shutil.copy2(src, dest)
    dest.chmod(0o755)
    print(f"==> Wrote {dest}")


if __name__ == "__main__":
    main()
