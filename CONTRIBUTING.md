# Contributing to Crossmith

First: thank you. A tool like this gets better in direct proportion to how
many different projects people try to throw at it. Reporting a project that
Crossmith *mis-detected* is as valuable as a code contribution.

## Ways to contribute (no code required)

- Try Crossmith on one of your own projects and open an issue for anything
  that felt wrong, confusing, or magical-in-a-bad-way
- Improve the docs — especially anything you had to figure out the hard way
- Triage issues, or help answer questions in Discussions
- Build a new [adapter](docs/guides/adapter-development.md) for a language
  Crossmith doesn't support yet

## Project layout

```
crossmith/
├── desktop/     # Tauri v2 + React/TypeScript UI (the shell)
├── engine/      # Python core: detection, build, packaging, adapters, AI
├── docs/        # Architecture, guides, ADRs
├── examples/    # Sample projects used for manual + automated testing
└── scripts/     # Dev/release tooling
```

The UI and the engine talk over a loopback-only HTTP API — you can develop
and test them independently. See `docs/architecture/` for the full picture.

## Development setup

### Engine (Python)

Requires Python 3.11+.

```bash
cd engine
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest                          # run the test suite
uvicorn crossmith.api.main:app --reload --port 8765   # run the engine standalone
```

### Desktop shell (Tauri + React)

Requires Node 20+ and the Rust stable toolchain ([rustup.rs](https://rustup.rs)).

```bash
cd desktop
npm install
npm run tauri dev        # starts the engine automatically and opens the app
```

### Running everything together

`scripts/dev.sh` (or `scripts\dev.ps1` on Windows) starts the engine and the
Tauri dev shell together with one command.

## Coding standards

- **Python:** formatted with `ruff format`, linted with `ruff check`, type
  hints required on public functions (`mypy` runs in CI). Run
  `pre-commit install` once, and hooks handle the rest.
- **TypeScript/React:** formatted with Prettier, linted with ESLint —
  `npm run lint` before pushing.
- **Commit messages:** [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`). This drives
  automatic changelog generation and semantic version bumps — it's not
  bureaucracy, it's what makes releases automatic.

## Adding a new language/framework adapter

This is the single highest-leverage contribution. Start at
[`docs/guides/adapter-development.md`](docs/guides/adapter-development.md) —
it walks through the `Adapter` interface, the detection rules an adapter
declares, and a minimal worked example. Open a
[feature request](.github/ISSUE_TEMPLATE/feature_request.yml) first if you
want feedback on the approach before investing time.

## Testing expectations

- New detection logic → a fixture project under `engine/tests/fixtures/` plus
  a test asserting what Crossmith should conclude about it
- New adapter → at least one working example project under `examples/`
  that builds successfully in CI
- Bug fix → a regression test that fails without your fix

## Pull request process

1. Fork, branch off `main`, keep the change focused
2. Make sure `pytest` (engine) and `npm test` (desktop) pass locally
3. Open the PR — the template will walk you through the rest
4. A maintainer will review; expect discussion on anything touching the
   detection engine or the adapter interface, since those are the hardest
   things to change later without breaking existing adapters

## Questions?

Open a [Discussion](../../discussions) rather than an issue — it's easier
for the next person to find.
