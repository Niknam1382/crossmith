#!/usr/bin/env python3
"""Sync the project version across every place it's declared, from one
source of truth: a version string like "1.0.0" (no leading "v").

Used by .github/workflows/release.yml, which passes the pushed tag with
its leading "v" stripped -- so pushing tag v1.0.0 builds installers that
all report version 1.0.0. Also runnable by hand before a manual release.

Usage:
    python scripts/sync_version.py 1.0.0
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def sync_package_json(path: Path, version: str) -> None:
    data = json.loads(path.read_text())
    data["version"] = version
    path.write_text(json.dumps(data, indent=2) + "\n")


def wix_safe_version(version: str) -> str:
    """Reduce a semver string to the numeric-only major.minor.patch WiX's
    MSI ProductVersion accepts.

    WiX (the Windows .msi target) rejects any pre-release identifier or
    build-metadata suffix -- e.g. "1.0.0-rc1" fails with "app version
    cannot have build metadata or pre-release identifier" (confirmed
    against tauri-bundler's own version-validation logic). NSIS, Cargo,
    npm, and PyPI all accept the full semver string fine; only WiX needs
    this reduced form, via the separate `bundle.windows.wix.version`
    override -- so the "real" version (rc suffix included) still shows up
    everywhere else, and the tag itself is untouched.
    """
    return version.split("+", 1)[0].split("-", 1)[0]


def sync_tauri_conf(path: Path, version: str) -> None:
    data = json.loads(path.read_text())
    data["version"] = version
    bundle = data.setdefault("bundle", {})
    windows = bundle.setdefault("windows", {})
    wix = windows.setdefault("wix", {})
    wix["version"] = wix_safe_version(version)
    path.write_text(json.dumps(data, indent=2) + "\n")


def sync_cargo_toml(path: Path, version: str) -> None:
    text = path.read_text()
    new_text, count = re.subn(
        r'^version = ".*"$', f'version = "{version}"', text, count=1, flags=re.MULTILINE
    )
    if count != 1:
        raise RuntimeError(f"expected exactly one top-level version line in {path}")
    path.write_text(new_text)


def sync_pyproject_toml(path: Path, version: str) -> None:
    text = path.read_text()
    new_text, count = re.subn(
        r'^version = ".*"$', f'version = "{version}"', text, count=1, flags=re.MULTILINE
    )
    if count != 1:
        raise RuntimeError(f"expected exactly one top-level version line in {path}")
    path.write_text(new_text)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/sync_version.py <version, e.g. 1.0.0>", file=sys.stderr)
        raise SystemExit(1)
    version = sys.argv[1].lstrip("v")

    sync_package_json(REPO_ROOT / "desktop" / "package.json", version)
    sync_tauri_conf(REPO_ROOT / "desktop" / "src-tauri" / "tauri.conf.json", version)
    sync_cargo_toml(REPO_ROOT / "desktop" / "src-tauri" / "Cargo.toml", version)
    sync_pyproject_toml(REPO_ROOT / "engine" / "pyproject.toml", version)
    print(f"==> Synced version {version} across desktop/package.json, "
          f"tauri.conf.json, Cargo.toml, and engine/pyproject.toml")


if __name__ == "__main__":
    main()
