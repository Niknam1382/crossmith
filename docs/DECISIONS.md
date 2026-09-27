# Crossmith — Phase 0: Strategy & Foundational Decisions

> Working name in the original brief: *AutoForge AI*. Renamed below, with rationale.

## 1. Name, Tagline, Pitch

- **Name:** Crossmith
- **Why:** *Cross* (cross-platform) + *-smith* (craftsperson — as in wordsmith, locksmith). Short, ASCII-only, easy to say and search; no dominant naming collision found on GitHub/PyPI/npm at time of writing. Verify final availability (domains, exact PyPI/npm slugs, trademarks) as a Phase 7 launch-checklist item — not a blocker now.
- **Tagline:** *Any codebase. Every platform. Zero config.*
- **One-line pitch:** Crossmith turns a source-code project into ready-to-ship, native installers for every major platform — auto-detected, built in an isolated environment, with nothing ever uploaded off your machine by default.

## 2. Positioning

Crossmith is **not** a replacement for PyInstaller, Nuitka, Tauri's bundler, fastlane, or electron-builder — it's the orchestration layer above them. It picks the right underlying tool for a given project, wires it into one clean pipeline, adds automatic project understanding (so the user never hand-writes a spec file), and wraps the whole thing in a premium desktop UI plus a generated CI/CD pipeline for the platforms it can't build locally.

**Target users:** independent developers and small teams who have working source code and want to ship it everywhere, without becoming an expert in six different packaging toolchains.

## 3. Scope Reality Check (why this section exists)

The original brief asks for fully automatic builds across ~6 platforms and ~12 languages, with local AI, "0 to 100." Two constraints are physical, not a matter of effort:

1. **iOS** can only be built and signed on macOS, with Xcode and an Apple ID. Nothing running on Windows/Linux can produce a signed IPA. Crossmith's job is to *detect* iOS-capable projects and *generate* the correct Xcode/fastlane pipeline — the last mile always runs on the user's own Mac.
2. **Native compilers build for the OS they run on.** PyInstaller/Nuitka/MSVC/etc. don't meaningfully cross-compile a full GUI app. So "every platform from one click" is delivered honestly as: **(a)** an immediate, real, working build for whichever OS Crossmith itself is running on, plus **(b)** an auto-generated GitHub Actions matrix that builds every other target on real OS runners the moment the user pushes. This isn't a downgrade — it's the same mechanism Crossmith uses to release *itself* (§8).

Everything else in this document is scoped around that reality.

## 4. Tech Stack

| Layer | Decision | Why | Rejected |
|---|---|---|---|
| Desktop shell + UI | **Tauri v2 + React + TypeScript + Tailwind** | Native window, ~5–10MB shell, full design freedom for the "premium" bar the brief asks for; dark/light/i18n are straightforward. Tauri shell + Python sidecar is an established, proven 2026 pattern, not a novel risk. | Electron (100MB+ runtime); PySide6/Qt (harder to hit a modern/animated UI fast, keeps UI work outside the web ecosystem contributors already know); Flet (younger, smaller plugin ecosystem) |
| Core engine | **Python, as a local FastAPI process** (loopback-only, spawned/killed by the shell) | Matches your existing stack; keeps 100% of detection/build "smarts" in one language for contributors; async-friendly for long builds with live log streaming | n8n — explicitly excluded by the brief, and it's a workflow-automation tool, not an application runtime |
| Python → native packaging | **Pluggable backend: Nuitka (default) / PyInstaller (fast fallback)** | Nuitka compiles to C → real native code, avoiding most of the antivirus false-positive problems bytecode-bundling tools are known for — important since this tool's entire output is binaries strangers download and run | py2exe (unmaintained); cx_Freeze (fewer features, same AV-trust problem as PyInstaller) |
| Build isolation (MVP) | **Per-build Python virtualenv** | Zero extra install for the end user (no Docker requirement) while still isolating each build's dependencies. Container/VM isolation is designed in as an opt-in, pluggable "sandbox backend" for later | Docker-by-default (breaks "offline-friendly" and "zero-config" for anyone without Docker) |
| Local AI | **cactus-compute/needle — optional plugin, wired in post-MVP** | Confirmed real: MIT-licensed, 26M-param, tool-calling/structured-extraction model, fully offline. Also a very young project (weeks old). Right call: ship the deterministic heuristic detector as the reliable backbone now; add Needle behind the same interface once the core is proven, with automatic fallback if it's absent, low-confidence, or errors | A larger local LLM (llama.cpp + 3B-class) — too heavy for "zero-config"/"lightweight," contradicts the privacy/offline brief |
| Plugin/adapter system | **Python `importlib.metadata` entry points + an `Adapter` ABC** | The standard, well-understood Python extension mechanism — community adapters install as `pip install crossmith-adapter-nodejs`, nothing bespoke to learn | A hand-rolled plugin loader |
| License | **Apache-2.0** | Explicit patent grant — the safer choice for an infra/build tool whose plugins will touch many third-party toolchains | MIT (simpler, but weaker patent protection for this category of tool) |

## 5. Architecture

```
┌──────────────────────────────┐      loopback HTTP only       ┌────────────────────────────────┐
│  Tauri v2 shell + React UI    │ ─────────────────────────────▶│   Python FastAPI core engine    │
│  (drag-drop, logs, themes)    │◀───────────────────────────── │   (spawned as a sidecar)        │
└──────────────────────────────┘                                └────────────────────────────────┘
                                                                              │
                     ┌───────────────┬────────────────┬─────────────────────┼────────────────┬───────────────────┐
                     ▼               ▼                ▼                     ▼                ▼                   ▼
              Detection Engine  AI Engine (opt.)  Adapter Registry     Build Engine     Packaging Engine   Release/CI Generator
```

Local state (build cache, history) lives in a project-local `.crossmith/` folder plus a small SQLite file — never uploaded anywhere.

## 6. MVP Scope

**In:**
- Desktop shell: drag-drop, dark/light, live build logs, settings
- Python-only detection (language/framework/entrypoint/deps/icon/README metadata), confidence-scored, with a manual-override screen when confidence is low
- Isolated per-build virtualenv, dependency install, test run if present
- Real local output for whichever OS Crossmith runs on (Windows `.exe`, Linux binary + AppImage, macOS `.app`), via the Nuitka/PyInstaller backend
- Auto-generated GitHub Actions matrix for the platforms not built locally
- Checksums + a simple build manifest
- Plugin/adapter interface (skeleton; Python adapter is the only implementation shipped)
- One polished, working example project
- Full GitHub-excellence scaffolding (README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, issue/PR templates, self-release CI)

**Out (real roadmap items, not abandoned):** Node.js/Go/Rust/Java/Flutter/etc. adapters · Android · iOS · Needle wiring · code-signing/notarization automation · plugin marketplace · package-manager distribution (winget/brew/choco/etc.)

## 7. Key Risks

- **Antivirus false positives on Windows output** → Nuitka-first strategy, plus a documented VirusTotal-submission/whitelisting guide.
- **"Zero-config" breaking on messy real repos** → every detection result is confidence-scored; low confidence always surfaces a manual-override screen instead of a silent wrong guess.
- **Scope creep vs. the "GitHub-ready quality" bar** → the MVP boundary above is deliberately strict; breadth is roadmap, not a v0.1 promise.

## 8. Self-Build & Release

Crossmith releases itself with the same mechanism it recommends to users: GitHub Actions on `windows-latest` / `macos-latest` / `ubuntu-latest`, each building the Tauri bundle with a Python sidecar frozen via PyInstaller (a small background HTTP service — a much simpler packaging job than the Nuitka path Crossmith offers end users for their own, often GUI-heavy, projects).

## 9. Rejected Alternatives (project-level)

- **All-Rust core** — smaller footprint and faster, but throws away Python's dominant position in scripting/build tooling and raises the contribution bar for the target audience (Python developers).
- **Cloud build workers as the primary path** — contradicts "privacy-first, nothing uploaded by default"; kept as a possible opt-in *post-MVP* feature, never the default.

---
*Next: Phase 1 — full repository scaffold (tree, README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, issue/PR templates).*

## Addendum — Phase 4: Needle wired in

The §4 table above called this "post-MVP," confirmed real but noted the
model repo was "weeks old" at Phase 0. By Phase 4 it had shipped a major
version: **Needle 2**, 45M params (not 26M), 14MB, via `pip install
cactus-needle`. The package's actual, installed API (`cactus-needle`
3.0.5, verified by hand — `needle.Needle(tools=...)`, `.complete()`
returning a `confidence`-scored call, `needle.extract()`) matches what
was speculatively planned closely enough that no architecture decision
here needed to change, but two things are worth recording that weren't
knowable at Phase 0:

- **"Fully offline" needed a precise correction, not a retraction.** The
  *package* fetches its own weights (~14MB) from Hugging Face once, on
  first use, and caches them. That is a real network call — just never
  one that carries any project data; inference itself is 100% local. The
  README's AI & privacy section and `docs/guides/ai-assist.md` now say
  this precisely instead of the flatter "fully local, nothing sent
  anywhere," which was true of the code but imprecise about the model
  fetch.
- **"Automatic fallback if it's absent, low-confidence, or errors" is now
  a tested guarantee, not just a design intent** — including the specific
  failure mode of no internet access to Hugging Face
  (`huggingface_hub.errors.LocalEntryNotFoundError`, confirmed to fail
  fast rather than hang) and of the `cactus-needle` package not being
  installed at all (confirmed: full test suite passes identically with
  and without it installed). See `docs/guides/ai-assist.md` for what was
  and wasn't possible to verify in a sandboxed environment without
  Hugging Face access.

Implementation: `engine/src/crossmith/ai/` (`base.py`'s `AIEngine`
interface, `needle_engine.py`'s `NeedleEngine`), wired into
`detection/engine.py` (`scan_project`'s optional `ai_engine` param) and
`build/orchestrator.py` (`run_build`'s error-explanation fallback), both
behind `Settings.ai_assist_enabled` (already existed from Phase 2/3 — the
setting and its desktop UI toggle were built ahead of the engine wiring
they were waiting on).

*Next: Phase 5 — build engine hardening (sandboxing, caching, retries).*

## Addendum — Phase 5b: self-release CI (pulled forward)

Local testing of the Tauri/Rust shell on Windows turned out to be
impractical for the user to do quickly. Rather than block further
progress on that, we pulled the self-release CI idea forward from
Phase 7 ("GitHub release excellence") to right now: a pushed version tag
(`.github/workflows/release.yml`) builds real installers on
windows-latest/macos-latest/ubuntu-22.04 GitHub-hosted runners and
attaches them to a draft Release. See `docs/guides/release-process.md`
for the full walkthrough.

This reframes what "testing this on Windows" even means: instead of one
person's one machine, it's GitHub's own Windows/macOS runners, on every
release, for free. It does not remove the value of a human trying the
resulting installer once before publishing — see that guide's closing
note — but it does mean nobody needs a working local Rust/Tauri
toolchain just to find out whether the build itself succeeds.

Two real gaps this surfaced and fixed along the way, not designed for
up front:

- **The bundle icons didn't exist.** `tauri.conf.json`'s `bundle.icon`
  list pointed at five files that were only ever a placeholder note in
  `icons/README.md`. `tauri build` — which CI now actually runs — would
  have failed immediately on every platform. Fixed by generating a
  simple, functional `docs/assets/logo.png` (a geometric mark in the
  UI's existing forge-amber accent color, not commissioned design work)
  and running `npx tauri icon` on it to produce the real set. This is a
  placeholder in the sense that it's not final branding, but it is a
  real, checked-in file the build now actually uses — no longer a TODO.
- **The sidecar-freezing step (`scripts/build_sidecar.py`) had never
  actually been run.** It was written in an earlier phase but not
  exercised. Running it for real: it worked on the first try, and the
  resulting frozen binary was started and answered `GET /health`
  correctly — the first real evidence the "ship the Python engine as a
  PyInstaller sidecar" plan from §8 actually works, not just compiles.

*Next: either Phase 5 (build engine hardening) or watching the first real
release-tag push actually run on Windows/macOS CI and fixing whatever it
finds — whichever the user prioritizes.*

## Addendum — Phase 5b, cont'd: first real CI run found two real bugs

`v1.0.0-rc1` was pushed as the first real end-to-end test (exactly the
plan above). Both `ci.yml` and `release.yml` failed. Root-caused by
actually reproducing each failure — pulling the exact commit CI built
(`codeload.github.com/.../tar.gz/<sha>`, not the working tree) into a
clean venv and rerunning `ruff`/`mypy`/`pytest`/`PyInstaller` against
it — rather than guessing from the CI log summary:

- **`engine/src/crossmith/build/` (the Build Engine —
  `orchestrator.py`, `venv_manager.py`) was never actually committed.**
  `.gitignore` had a bare `build/` line meant for Python's top-level
  packaging-artifact directory; with no leading slash, gitignore matches
  that name at *any* depth, so it silently also matched this real
  source package every time it was `git add`-ed. Every local run
  (including the Phase 5b sidecar test above) used the working tree,
  where the files exist on disk regardless of git — so this was
  invisible until CI did a real `git checkout`. Impact was worse than
  the CI failure alone suggested: `crossmith.api.main` and
  `crossmith.adapters.python_adapter` both import from it unconditionally,
  so the engine can't even be imported in a fresh clone. The Linux/macOS
  `release.yml` jobs still showed green and uploaded artifacts, because
  PyInstaller treats an unresolvable first-party import as a build-time
  *warning*, not an error — confirmed by actually running the frozen
  binary from that exact commit: it builds, then crashes on launch with
  `ModuleNotFoundError: No module named 'crossmith.build'` before the
  server ever binds, so `/health` never answers. The `ruff` failure
  (`I001`, reported as "import block un-sorted") was a symptom of the
  same bug, not a separate one — ruff's import classifier couldn't
  place a `crossmith.build` submodule it couldn't find on disk, and
  restoring the package resolved it with no code changes. Fix: added
  the missing package to git and re-scoped the ignore rule to
  `engine/build/`, matching only the actual packaging-artifact path.
- **WiX (the `.msi` target) rejects a non-numeric pre-release version.**
  `v1.0.0-rc1` is valid semver, and Cargo/npm/PyPI/NSIS all accept it,
  but confirmed against tauri-bundler's own version-validation code:
  WiX's `ProductVersion` must be `major.minor.patch[.build]`, all
  numeric, so `-rc1` fails with "app version cannot have build metadata
  or pre-release identifier." Only Windows builds both an NSIS `.exe`
  *and* a WiX `.msi` from the same `targets: "all"`, which is why only
  that platform failed. Fix: `sync_version.py` now also derives a
  numeric-only `major.minor.patch` and writes it to the documented
  `bundle.windows.wix.version` override, so WiX gets a version it
  accepts while every other artifact keeps reporting the real,
  full version (see `docs/guides/release-process.md`).

Both fixes were verified directly against the actual failing commit
(not just the corrected tree): `ruff`/`mypy`/`pytest` — including the
2 `slow` real-Nuitka/PyInstaller tests — all pass clean after restoring
`build/`, and the `ModuleNotFoundError` crash was reproduced and then
confirmed gone. The WiX fix could not be compiled end-to-end in this
environment (no Windows/WiX toolchain available); it's a direct
application of tauri-bundler's own documented `wix.version` escape
hatch, but the next tag push is still the first real confirmation of
it — see the "one gap" note this addendum doesn't close, below.

**One gap this doesn't close:** a separate, upstream Tauri bug
(tauri-apps/tauri#14681 — MSI bundling can fail when `externalBin` is
set, independent of version) was open against tauri-bundler and closed
via a fix (#15651) during 2026. This project's locked `@tauri-apps/cli`
(2.11.5) is recent enough it most likely postdates that fix, but that
couldn't be confirmed precisely from here — worth keeping in mind if
the Windows job fails *again* after this fix, with a different error.

*Next: push a new tag (`v1.0.0-rc2`) to confirm both fixes for real on
CI's Windows/macOS/Linux runners, then Phase 5 (build engine hardening)
or more language adapters — whichever the user prioritizes.*
