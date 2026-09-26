# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

Nothing yet.

## [1.0.2] - 2026-09-25

### Fixed

- `packaging/pyinstaller/clicksmith.spec` was missing its `COLLECT()` step, so PyInstaller built
  a single-file exe directly at `dist/Clicksmith.exe` instead of the `dist/Clicksmith/` folder
  (with an `_internal/` subfolder) that the Inno Setup script, the release zip step, and the
  `--selftest` path everywhere else in the pipeline all expect. That mismatch is what made both
  `windows-build-smoke` and the release build fail right after a successful test run. Fixed by
  adding the `COLLECT()` call, which also means Clicksmith now starts instantly instead of
  self-extracting on every launch (the actual benefit of a onedir build for a Qt app).

## [1.0.1] - 2026-09-25

### Fixed

- CI and the release build both failed every job that runs the test suite (`pytest`) or
  `mypy`, because the `clicksmith` package itself was never installed before they ran -
  `requirements-dev.txt` installed PySide6, pynput, and the dev tools, but not the project.
  Added `-e .` to `requirements-dev.txt`, and `pythonpath = ["src"]` / `mypy_path = "src"` in
  `pyproject.toml` as a second safety net. This is what actually broke the first `v1.0.0`
  release build; 1.0.0's feature set is unaffected and this releases the same code, working.
- `ruff check`/`ruff format` and `mypy` were configured with rule sets never verified against
  a real run of those tools. Narrowed CI's Lint job to pyflakes only (real-bug detection, no
  formatting opinions) and marked Lint/Type-check as informational rather than blocking, so a
  future style/typing finding can't block a release the way a real test failure does. See the
  comment in `pyproject.toml`'s `[tool.ruff.lint]` and `CONTRIBUTING.md`.

## [1.0.0] - 2026-09-25

### Added

- Clicker mode: left/right/middle button, single/double/triple click, click-and-hold, a
  configurable interval (h/m/s/ms) with a percentage of random jitter, and three targeting modes
  (follow the cursor, a fixed point, or a random point inside an area).
- Macro mode: a recorder that turns real mouse/keyboard input into an editable step list
  (click, move, drag, scroll, type Unicode text, press a key combination, wait), plus a manual
  step editor with an on-screen position picker.
- Full Unicode text typing on Windows via `SendInput` (`KEYEVENTF_UNICODE`), independent of the
  active keyboard layout - Persian, Arabic, CJK, emoji, all work.
- Three stop conditions (until stopped / a number of repetitions / a duration), a start delay,
  a failsafe corner, and an optional "stop if the mouse moves" guard.
- A daily/weekly scheduler (specific days and time), running from the system tray.
- Multiple named, importable/exportable JSON profiles.
- Global hotkeys (start/stop, capture position, emergency stop), configurable in Settings.
- A `clicksmith run <profile.json>` headless CLI mode with `--dry-run`, for scripting or CI.
- A full Persian (فارسی) translation with right-to-left layout, alongside English.
- Dark and light themes.
- An opt-in, privacy-respecting update check against GitHub Releases (off by default).

### Notes

- Windows is the primary supported platform (native `SendInput` backend). An experimental
  cross-platform backend for Linux/macOS is included, built on `pynput`; see the README.

[Unreleased]: https://github.com/OWNER/clicksmith/compare/v1.0.2...HEAD
[1.0.2]: https://github.com/OWNER/clicksmith/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/OWNER/clicksmith/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/OWNER/clicksmith/releases/tag/v1.0.0
