# Getting started

Crossmith is pre-release — there's no installer yet (see the
[roadmap](../../README.md#roadmap)). For now, run it from source. This
guide assumes you haven't used Tauri or Rust before.

## 1. Install the three prerequisites

You need three separate toolchains, because Crossmith has three separate
parts (Python engine, Rust/Tauri shell, React/TS UI):

1. **Python 3.11+** — you almost certainly have this already. Check with
   `python3 --version`.
2. **Node 20+** — check with `node --version`. If you don't have it,
   [nodejs.org](https://nodejs.org) or `nvm` both work.
3. **Rust, via [rustup](https://rustup.rs)** — run the install script on
   that page, then restart your terminal. **Important: don't install Rust
   with `apt`/`dnf`/your distro's package manager instead** — on Ubuntu
   24.04 that gives you Rust 1.75, which is too old for some of Tauri's
   current dependencies and will fail with a confusing
   `feature edition2024 is required` error. `rustup` gives you an
   up-to-date version and is what Tauri itself recommends.

**Linux** — Tauri also needs some system libraries for the native
webview. On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install libwebkit2gtk-4.1-dev libssl-dev libsoup-3.0-dev \
  libayatana-appindicator3-dev librsvg2-dev libxdo-dev build-essential \
  curl wget file pkg-config
```

**Windows** — two more things Tauri needs beyond Rust/Node, straight from
[Tauri's own prerequisites page](https://v2.tauri.app/start/prerequisites/)
(not independently verified by us — see the honesty note below):

1. **Microsoft C++ Build Tools.** Download the [Visual Studio Build Tools
   installer](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   and, during installation, check **"Desktop development with C++"**.
2. **WebView2 Runtime.** Windows 11 and recent Windows 10 come with this
   preinstalled; if `./scripts/dev.ps1` fails looking for it, get the
   "Evergreen Bootstrapper" from the
   [WebView2 download page](https://developer.microsoft.com/en-us/microsoft-edge/webview2/#download-section).
3. When installing Rust via `rustup`, make sure the **MSVC** toolchain is
   selected as default (the rustup installer asks; if Rust is already
   installed, run `rustup default stable-msvc` to fix it after the fact).
   The GNU toolchain will not build Tauri correctly.

(macOS instead needs Xcode Command Line Tools: `xcode-select --install`.)

**Honesty note:** everything above except the "don't use apt for Rust"
warning is Tauri's own documentation, not something we've personally run
and confirmed — this whole project has only actually been exercised on
Linux so far (see the note at the end of this guide). If something here
is stale or wrong for your setup, `docs/guides/troubleshooting.md` and
[Tauri's Discord/GitHub discussions](https://v2.tauri.app/start/prerequisites/)
are the next stop, and an issue report from you would be the first real
Windows/macOS data point this project has.

## 2. Run it

```bash
git clone https://github.com/niknam1382/crossmith.git
cd crossmith
./scripts/dev.sh          # macOS/Linux — Windows: scripts\dev.ps1
```

What this does, in plain terms: it creates a Python virtual environment
for the engine and installs it, writes a small wrapper script so the Rust
shell can start the Python engine the same way it will in a real build,
then runs `tauri dev`, which compiles the Rust shell (slow the first
time — expect several minutes while it downloads and compiles ~450 Rust
crates) and opens the app window.

If it opens a window with a drag-and-drop area, it worked.

## 3. Build your first project

1. Drag a Python project folder onto the window — or use the bundled
   [`examples/python-cli`](../../examples/python-cli) folder, which is
   guaranteed to work, to sanity-check the pipeline first.
2. Confirm what Crossmith detected — language, entry point, dependencies.
3. Click **Build**.
4. Find the native binary in the build's output — Crossmith prints the
   path when it's done.

Only Python projects are supported right now, built for whichever OS
you're running Crossmith on. See
[Supported languages](../../README.md#supported-languages) and
[Supported output platforms](../../README.md#supported-output-platforms)
in the main README for what's next on the roadmap.

## Something not working?

See [`docs/guides/troubleshooting.md`](troubleshooting.md) — it covers the
issues that actually came up building Crossmith itself, including the
Rust-toolchain and Linux-library issues above, and Nuitka's `patchelf`
requirement.

## Honesty note on what's actually been tested

The Python engine (detection + real Nuitka/PyInstaller builds) has been
tested end-to-end on Linux, including a fresh clone with a fresh
virtualenv. The Rust/Tauri shell has **not** yet been confirmed to compile
successfully anywhere, on any OS — see
[`docs/DECISIONS.md`](../DECISIONS.md) and the project's current phase
notes for exactly what that means. If `./scripts/dev.sh` gets further for
you than it has for us so far, that's useful information — please open an
issue either way.
