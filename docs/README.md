# Crossmith Docs

- [**DECISIONS.md**](DECISIONS.md) — Phase 0 strategy: name, positioning, tech
  stack with rationale, architecture, MVP scope, risks, rejected alternatives.
  Start here to understand *why* things are built the way they are.
- [**original-brief.md**](original-brief.md) — the full original project brief
  this was scoped down from. DECISIONS.md is the source of truth for what's
  actually being built; this is kept for the detail on later-phase features
  (more languages, Android, code signing, community/launch plans) that
  hasn't been scoped into a phase yet.
- **architecture/** — deeper dives per layer, as they're written.
- **guides/**:
  - [`getting-started.md`](guides/getting-started.md) — install and run your first build
  - [`adapter-development.md`](guides/adapter-development.md) — build a new language/platform adapter, using the real Python adapter as a worked example
  - [`troubleshooting.md`](guides/troubleshooting.md) — common problems, including ones found building Crossmith itself (Nuitka's `patchelf` requirement, AV false positives)
  - [`ai-assist.md`](guides/ai-assist.md) — the optional local AI assist (Needle): what it does, privacy, what's tested
  - [`release-process.md`](guides/release-process.md) — how the self-release CI works and how to cut a release

See the main [README](../README.md#roadmap) for what's built vs. still planned.
