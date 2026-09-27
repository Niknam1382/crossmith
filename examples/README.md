# Examples

Sample projects used for manual testing and as CI fixtures.

| Example | Status | Purpose |
|---|---|---|
| [`python-cli/`](python-cli/) | ✅ working | Simplest case: single-file Python CLI, no dependencies. Built and executed as part of the test suite (`pytest -m slow`) — this one is guaranteed to work, try it first |
| `python-gui/` | planned | A small Python GUI app with an icon and one dependency |
| `python-with-assets/` | planned | Non-code assets that must be bundled into the build |
| `broken-project/` | planned | Intentionally missing an entry point — demonstrates the manual-review flow and AI-suggested fixes |

Each example has its own directory with the source and (where it exists) a
test proving it actually builds and runs — see
[`docs/guides/adapter-development.md`](../docs/guides/adapter-development.md)
for why a real, executed artifact is the bar, not just a detection unit
test.
