"""Pluggable packaging backend interface.

See docs/DECISIONS.md's "Python -> native packaging" decision: Nuitka is
the default (real compilation, fewer antivirus false positives),
PyInstaller is the fast fallback. Both implement this same interface so
the adapter that calls them doesn't need to know which one it's using.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PackageResult:
    success: bool
    artifact_path: Path | None = None
    logs: str = ""
    error: str | None = None


class PackagingBackend(ABC):
    name: str

    @abstractmethod
    def is_available(self) -> bool:
        """Whether this backend's tooling can be used right now."""

    @abstractmethod
    def package(
        self,
        entry_point: Path,
        env_python: Path,
        output_dir: Path,
        *,
        app_name: str,
        icon: Path | None = None,
    ) -> PackageResult:
        """Produce a single-file native executable for entry_point.

        env_python is the interpreter of the project's own isolated venv
        (see build/venv_manager.py) — packaging must run through it so the
        project's dependencies are on the path the freezer inspects.
        """
