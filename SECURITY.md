# Security Policy

Crossmith builds and packages executables — trust is the entire product. This
document explains how we handle security, and how to report a problem.

## Reporting a Vulnerability

**Please do not open a public issue for security vulnerabilities.**

Use GitHub's private [Security Advisories](../../security/advisories/new)
reporting form for this repository, or email **security@crossmith.dev**
(placeholder — update before launch) with:

- A description of the vulnerability and its potential impact
- Steps to reproduce (proof-of-concept code or a sample project, if relevant)
- The Crossmith version and OS you tested on

We aim to acknowledge new reports within **72 hours** and to ship a fix or
mitigation, or agree on a disclosure timeline, within **90 days**.

## Supported Versions

Until the first `1.0` release, only the latest `0.x` release receives
security fixes. After `1.0`, this table will track the current and previous
minor versions.

| Version | Supported |
|---|---|
| `0.x` (latest) | ✅ |
| `< latest 0.x` | ❌ |

## Our Security Principles

- **No source code leaves your machine by default.** Detection, AI-assisted
  analysis, and builds run locally. Any feature that would send data off-device
  is opt-in and clearly labeled.
- **No hidden telemetry.** Nothing is collected unless you explicitly opt in.
- **Every build runs isolated.** Each build gets its own virtual environment
  (with pluggable container/VM sandboxing planned for hardening); a project
  you build cannot read or modify another project's files or credentials.
- **Dependencies are pinned and scanned.** Both Crossmith's own dependencies
  and the ones it installs for your project are subject to lockfiles and
  automated scanning in CI.
- **You're warned before arbitrary code execution.** Detected build/test
  commands are shown to you before they run; Crossmith never silently
  executes a command it discovered in a repository.
- **Releases are checksummed**, with signed releases and reproducible builds
  as a post-MVP goal (tracked in the roadmap).
- **Plugins run with a declared permission model** — an adapter has to state
  what it needs (network access, filesystem scope, etc.) before it can be
  installed.

## Known Limitations (be honest with yourself before you're honest with users)

- Windows antivirus engines can still false-positive on freshly built,
  unsigned binaries — including ones Crossmith produces for your project.
  See the troubleshooting guide for submission/whitelisting steps.
- Code signing and notarization are not automated in the MVP; until then,
  unsigned builds will show OS-level "unknown publisher" warnings. This is
  expected, not a bug.
