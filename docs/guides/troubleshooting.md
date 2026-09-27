# Troubleshooting

## "Nuitka's onefile mode on Linux requires 'patchelf'"

Nuitka's Linux onefile builds need the `patchelf` system tool. Install it:

```bash
sudo apt install patchelf      # Debian/Ubuntu
sudo dnf install patchelf      # Fedora
brew install patchelf          # macOS
```

You don't strictly have to — if it's missing, Crossmith automatically falls
back to PyInstaller for that build and says so in the build log. Install
`patchelf` when you want Nuitka's antivirus-friendlier output (see
[`docs/DECISIONS.md`](../DECISIONS.md)) instead of the fallback.

## Windows Defender (or another antivirus) flags the built `.exe`

This happens to freshly built, unsigned binaries in general — not just
Crossmith's — because heuristic AV engines are suspicious of code with no
publisher history yet. It's less common with the default Nuitka backend
(real compiled code) than with PyInstaller (bytecode bundling), but it can
still happen with either.

What helps:
- Submit the binary to [VirusTotal](https://www.virustotal.com) — if only
  one or two obscure engines flag it, that's a generic heuristic, not a
  real detection
- Code-signing removes most of this, but isn't automated yet (see the
  roadmap in the main [README](../../README.md))
- If you can, ask affected users to submit a false-positive report to their
  AV vendor — this is what actually gets a specific build whitelisted

## `cargo build` fails with `feature edition2024 is required`

This means your Rust toolchain is too old — some of Tauri's dependencies
now require a fairly recent stable Rust. Confirmed on Ubuntu 24.04: the
`rustc`/`cargo` you get from `apt install rustc cargo` is **1.75**, which
is not new enough, even though `desktop/src-tauri/Cargo.toml` currently
(optimistically) lists `rust-version = "1.77"`.

Fix: don't install Rust from your distro's package manager. Use
[rustup](https://rustup.rs) instead and make sure it's on the `stable`
channel (`rustup update stable`), which will be well past 1.77. If you
already have a distro-installed `rustc` on your `PATH`, make sure the
rustup-managed one takes priority (`rustup` does this automatically by
putting `~/.cargo/bin` first — just double check with `which rustc`).

## Linux build fails looking for `webkit2gtk` / `javascriptcoregtk` / soup / appindicator

Tauri's Linux build needs these system dev packages (confirmed working
versions on Ubuntu 24.04, package names may differ slightly on other
distros):

```bash
sudo apt install libwebkit2gtk-4.1-dev libssl-dev libsoup-3.0-dev \
  libayatana-appindicator3-dev librsvg2-dev libxdo-dev build-essential \
  curl wget file pkg-config
```

If `libwebkit2gtk-4.1-dev` 404s for you, run `sudo apt update` first —
that alone resolved it here.

## Windows: `link.exe` not found / MSVC-related build errors

You're missing the Microsoft C++ Build Tools, or Rust is using the GNU
toolchain instead of MSVC. Install the [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
with "Desktop development with C++" checked, then run
`rustup default stable-msvc` and restart your terminal.

## Windows: blank window / WebView2-related error on first run

Get the WebView2 Runtime ("Evergreen Bootstrapper") from
[Microsoft's download page](https://developer.microsoft.com/en-us/microsoft-edge/webview2/#download-section)
and install it. Most Windows 10/11 machines have this already, but it can
be missing on older or LTSC builds.

## "ModuleNotFoundError" / "No module named X" during or after a build

Something your code imports isn't listed in `requirements.txt` (or
`pyproject.toml`'s `dependencies`). Crossmith only installs what's
declared — it can't know about an import that isn't. Add the missing
package and rebuild.

## Detection picked the wrong entry point, or didn't match at all

The Python adapter looks for `main.py`, `app.py`, `run.py`, `__main__.py`,
or `cli.py` at your project's root, in that order, falling back to "the
only `.py` file at the root" if there's exactly one. If none of that fits
your layout, that's expected — low-confidence or no-match results are
supposed to ask you rather than guess. A manual-override screen (and
support for pointing at a nested entry point) is tracked on the roadmap.

## The desktop app can't reach the engine ("Can't reach the Crossmith engine")

- **In dev:** make sure you started it with `scripts/dev.sh` (or
  `dev.ps1`), not `tauri dev` directly — that script is what drops the
  sidecar wrapper the Rust shell expects to find. See
  [`CONTRIBUTING.md`](../../CONTRIBUTING.md).
- **Port already in use:** something else is already listening on 8765.
  Stop it, or set `CROSSMITH_PORT` before starting.
- Check `~/.crossmith/logs/engine.log` for what the engine itself saw.

Still stuck? [Open an issue](../../.github/ISSUE_TEMPLATE/bug_report.yml) —
a minimal reproduction is the fastest way to get it fixed.
