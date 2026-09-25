"""The interface every language/framework adapter implements.

Community adapters ship as separate installable packages and register
under the `crossmith.adapters` entry-point group declared in pyproject.toml.
See docs/guides/adapter-development.md for a full walkthrough with a
worked example.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DetectionResult:
    """What an adapter concluded about a project, and how sure it is."""

    matched: bool
    confidence: float
    """0.0-1.0. Below CONFIDENCE_THRESHOLD (see detection/engine.py), the UI
    must show a manual-override screen instead of silently acting on this."""
    language: str
    framework: str | None = None
    entry_point: str | None = None
    dependencies: list[str] = field(default_factory=list)
    icon_candidate: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)
    """Human-readable evidence, shown in the UI's 'why did it guess this' panel."""


@dataclass
class BuildResult:
    success: bool
    artifact_paths: list[Path] = field(default_factory=list)
    logs: str = ""
    error: str | None = None
    error_explanation: str | None = None
    """Plain-language 'what happened, why, how to fix it' — never hand the
    user a raw traceback alone. See docs/DECISIONS.md's key risks."""


class Adapter(ABC):
    """One implementation per language/framework.

    Adapters are stateless: a fresh instance is created per build so one
    project's build can never leak state into another's.
    """

    name: str
    """Unique, stable id used in config files and CLI flags, e.g. "python"."""

    packaging_backends: tuple[str, ...] = ()
    """Which packaging backends this adapter can drive, in preference order."""

    @abstractmethod
    def detect(self, project_path: Path) -> DetectionResult:
        """Inspect project_path and report what this adapter thinks it is.

        Must not mutate the project. Must not raise on a non-match — return
        DetectionResult(matched=False, confidence=0.0, language=...) instead,
        so one adapter erroring never blocks the others from running.
        """

    @abstractmethod
    def install_dependencies(self, project_path: Path, env_path: Path) -> None:
        """Install the project's dependencies into an isolated environment at
        env_path. Must not write anything outside env_path/project_path."""

    @abstractmethod
    def run_tests(self, project_path: Path, env_path: Path) -> BuildResult:
        """Run the project's test suite if one is configured.

        success=True with empty logs is the correct result when there is
        simply no test suite to run — that is not a failure.
        """

    @abstractmethod
    def build(
        self,
        project_path: Path,
        env_path: Path,
        target_platform: str,
        output_dir: Path,
    ) -> BuildResult:
        """Produce a native artifact for target_platform in output_dir."""

    def suggest_fix(self, error: BuildResult) -> str | None:
        """Optional: map a known failure pattern to a human suggestion.

        Default is no suggestion — the caller falls back to the AI engine
        (if the user enabled it) or just shows the error as-is.
        """
        return None
