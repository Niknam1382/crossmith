# Building Clicksmith.exe

You do not need to do this to use Clicksmith - grab a build from the
[Releases page](https://github.com/OWNER/clicksmith/releases) instead. This is for building it
yourself, or hacking on the packaging.

## Requirements

- **Windows 10/11**, 64-bit. PyInstaller builds a native executable for whatever OS it runs on,
  so a Windows `.exe` must be built on Windows (the project's `windows-build-smoke` CI job does
  exactly this on every change - see `.github/workflows/ci.yml`).
- Python 3.11-3.13 (`py -3.12` recommended - matches CI).
- [Inno Setup 6](https://jrsoftware.org/isdl.php), only if you also want the `Setup.exe`
  installer, not just the portable build.

## One command

```powershell
git clone https://github.com/OWNER/clicksmith.git
cd clicksmith
.\scripts\build_windows.ps1
```

This creates a virtual environment, installs `requirements-dev.txt`, runs the test suite, then
PyInstaller, then runs the frozen exe with `--selftest` to confirm the build actually works
before calling it done. Output:

- `packaging\pyinstaller\dist\Clicksmith\Clicksmith.exe` - the portable build (a whole folder;
  zip it or copy the folder as-is - don't move just the `.exe` out on its own).
- `packaging\inno\Output\Clicksmith-Setup-<version>.exe` - the installer, if Inno Setup's
  `ISCC.exe` was found on `PATH`.

## Doing it by hand

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -q

python packaging\pyinstaller\generate_version_info.py
pyinstaller packaging\pyinstaller\clicksmith.spec --noconfirm

.\packaging\pyinstaller\dist\Clicksmith\Clicksmith.exe --selftest

# Optional installer:
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /DAppVersion=1.0.2 packaging\inno\clicksmith.iss
```

## How a release actually gets published

Pushing a tag matching `v*.*.*` (e.g. `v1.1.0`) triggers `.github/workflows/release.yml`, which
does exactly the steps above on a clean `windows-latest` GitHub Actions runner, then publishes the
zip, the installer, and a `SHA256SUMS.txt` to a GitHub Release. Building on a fresh CI runner
rather than a maintainer's own machine means every release is reproducible and isn't affected by
whatever else happens to be installed locally. See `CONTRIBUTING.md` for the full release
checklist (bump `__version__`, update `CHANGELOG.md`, tag, push).

## `--selftest`

`clicksmith --selftest` (also runnable as `Clicksmith.exe --selftest`) runs a handful of checks
against the actual frozen build - the engine performs real clicks against a fake backend, the
platform's `InputBackend` loads, `pynput` imports, the icon assets are present, the Persian
translation table is reachable, and the main window constructs - and exits non-zero if anything
fails. It's what both CI jobs and `build_windows.ps1` use to confirm a build isn't just "created a
file" but actually works, without needing a human to click around it first.
