# Cutting a release

Crossmith builds itself the same way it's meant to build other people's
projects: a version tag pushed to GitHub triggers
[`.github/workflows/release.yml`](../../.github/workflows/release.yml),
which cross-builds native installers on real Windows, macOS, and Linux
GitHub-hosted runners and attaches them to a (draft) GitHub Release.

This exists specifically because compiling the Tauri/Rust shell has never
been confirmed to succeed on a real Windows or macOS machine — see
`docs/guides/getting-started.md`'s honesty note. Rather than depending on
someone manually testing that on their own machine, CI's real OS runners
*are* the first true end-to-end test, on all three platforms, every time
a release is cut.

## How to cut one

```bash
git tag v1.0.0
git push origin v1.0.0
```

That's it — pushing the tag is the trigger. Go to the repo's **Actions**
tab and watch the `Release` workflow run (three jobs, one per OS, in
parallel — expect 5-15 minutes, most of it Rust compilation).

To test the pipeline without creating a real release (no tag, nothing
published), use the **Actions** tab → `Release` → **Run workflow**
(`workflow_dispatch`). This runs the exact same build on all three
platforms; only the "attach to GitHub Release" step is skipped.

## What the workflow actually does, per platform

1. Checks out the repo.
2. **Linux only:** installs the system webview libraries — the exact
   package list from `docs/guides/troubleshooting.md`'s Linux section,
   confirmed working there.
3. Sets up Python 3.11, Node 20, and Rust **stable via
   [`dtolnay/rust-toolchain`](https://github.com/dtolnay/rust-toolchain)**
   — deliberately not the OS package manager, for the same reason
   `docs/guides/getting-started.md` tells a human not to `apt install
   rustc`: it's too old for current dependencies.
4. `scripts/sync_version.py` rewrites the version in `desktop/package.json`,
   `desktop/src-tauri/tauri.conf.json`, `desktop/src-tauri/Cargo.toml`, and
   `engine/pyproject.toml` to match the pushed tag (so `v1.0.0` produces
   installers that all report version `1.0.0`, everywhere).
5. `scripts/build_sidecar.py` freezes the Python engine into a standalone
   binary with PyInstaller and drops it where Tauri's `externalBin`
   config expects it. **This step is the one part of the whole pipeline
   already confirmed working, by hand, in a sandboxed Linux environment**:
   the frozen binary started up and answered `GET /health` correctly. It
   has not yet been confirmed on Windows or macOS — that's exactly what
   the first real CI run will tell us.
6. `npm run tauri build` compiles the Rust shell and produces the
   platform-native installer(s): `.msi`/`.exe` (Windows, via NSIS), `.dmg`
   (macOS), `.deb`/`.AppImage`/`.rpm` (Linux) — whichever `tauri-cli`
   decides to build for that OS.
7. Uploads whatever was produced as a build artifact (so a
   `workflow_dispatch` test run always leaves something downloadable),
   and — only on an actual tag push — attaches those same files to a
   **draft** GitHub Release.

## Why "draft"

The release is created as a draft on purpose: nothing goes live/public
until you open it in the GitHub UI, review the attached installers and
the auto-generated release notes, and click **Publish**. If a build is
broken on one platform, you'll see it there before anyone downloads it.

## The one thing this doesn't verify

CI proves the *build* succeeds on each OS. It does not prove the
resulting installer actually installs cleanly and the app opens and works
on a real end-user machine — a real (if imperfect) proxy, but not a full
substitute for someone downloading the artifact and trying it. Doing that
once, on each OS, before publishing a release for real is still worth it.

## Version numbers between releases

`desktop/package.json`, `tauri.conf.json`, `Cargo.toml`, and
`engine/pyproject.toml` are only kept in sync *at release time*, by
`sync_version.py` running in CI. Day to day they can drift (they all
currently say `0.1.0`) — that's expected and fine; don't hand-edit them
before a release, the workflow does it.
