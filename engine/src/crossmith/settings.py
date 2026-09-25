"""Settings manager.

Local-only, human-editable config at ~/.crossmith/config.toml. No setting
in here ever controls sending source code anywhere off this machine — see
docs/DECISIONS.md's AI & privacy section.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Literal

import tomli_w
from pydantic import BaseModel

CONFIG_DIR = Path.home() / ".crossmith"
CONFIG_FILE = CONFIG_DIR / "config.toml"


class Settings(BaseModel):
    theme: Literal["light", "dark", "system"] = "system"
    language: Literal["en", "fa"] = "en"

    ai_assist_enabled: bool = False
    """Local AI (Needle) assist. Off by default — opt-in only."""

    telemetry_enabled: bool = False
    """Always off by default. Never silently enabled by an update."""

    default_packaging_backend: Literal["nuitka", "pyinstaller"] = "nuitka"

    @classmethod
    def load(cls, path: Path | None = None) -> Settings:
        # Resolved inside the call (not as a default arg) so patching the
        # module-level CONFIG_FILE — e.g. in tests — is actually honored.
        resolved = path if path is not None else CONFIG_FILE
        if not resolved.exists():
            return cls()
        with resolved.open("rb") as f:
            data = tomllib.load(f)
        return cls.model_validate(data)

    def save(self, path: Path | None = None) -> None:
        resolved = path if path is not None else CONFIG_FILE
        resolved.parent.mkdir(parents=True, exist_ok=True)
        with resolved.open("wb") as f:
            tomli_w.dump(self.model_dump(mode="json"), f)
