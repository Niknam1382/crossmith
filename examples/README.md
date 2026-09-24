# Examples

Sample projects used for manual testing and as CI fixtures — each one should
build successfully with `crossmith build .` once the corresponding adapter
exists. Planned for Phase 3 (Python adapter MVP):

| Example | Purpose |
|---|---|
| `python-cli/` | Simplest possible case: single-file Python CLI, no dependencies |
| `python-gui/` | A small Python GUI app with an icon and one dependency |
| `python-with-tests/` | Exercises the "run tests before packaging" path |
| `python-with-assets/` | Non-code assets that must be bundled into the build |
| `broken-project/` | Intentionally missing an entry point / has an unpinned bad dependency — demonstrates the error-diagnosis panel and AI-suggested fixes |

Each example will get its own `README.md` explaining what it's meant to
prove once added.
