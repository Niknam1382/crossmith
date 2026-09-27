# Writing an adapter

An adapter teaches Crossmith how to recognize, install dependencies for,
test, and build one language or framework. This guide walks through the
interface using the real, first-party Python adapter
(`engine/src/crossmith/adapters/python_adapter.py`) as the worked example —
it isn't a toy, it's the same code Crossmith itself uses.

## The interface

Every adapter implements `crossmith.adapters.base.Adapter`
(`engine/src/crossmith/adapters/base.py`):

```python
class Adapter(ABC):
    name: str
    packaging_backends: tuple[str, ...] = ()

    def detect(self, project_path: Path) -> DetectionResult: ...
    def install_dependencies(self, project_path: Path, env_path: Path) -> None: ...
    def run_tests(self, project_path: Path, env_path: Path) -> BuildResult: ...
    def build(self, project_path, env_path, target_platform, output_dir) -> BuildResult: ...
    def suggest_fix(self, error: BuildResult) -> str | None: ...  # optional
```

Adapters are stateless — a fresh instance is created per build, so nothing
you store on `self` can leak between unrelated projects.

## 1. `detect()` — and don't skip confidence

Look at `project_path` and decide (a) whether this adapter recognizes it
and (b) how sure you are. The Python adapter's version:

- Looks for `main.py`, `app.py`, `run.py`, `__main__.py`, or `cli.py` at
  the root; falls back to "the only `.py` file at the root" if there's
  exactly one
- No entry point found → `DetectionResult(matched=False, confidence=0.0, ...)`
  — **never raise on a non-match**; one adapter erroring must not stop
  the others from running (see `adapters/registry.py`)
- Starts at `confidence = 0.6` and adds small amounts for corroborating
  evidence (a conventionally-named entry point, a `pyproject.toml`,
  declared dependencies), capped at `0.98` — never `1.0`; you're pattern
  matching a real filesystem, not proving a theorem

Fill in `reasons: list[str]` with short, human-readable evidence — this
is what the UI's "why did it guess this" panel shows. `results[0].confidence
< CONFIDENCE_THRESHOLD` (see `detection/engine.py`) triggers a
manual-review screen instead of silently acting on a weak guess — respect
that by keeping your confidence honest, not inflated.

## 2. `install_dependencies()` — isolated, every time

Create the build's own environment at `env_path` (never reuse or write
outside it) and install the project's declared dependencies into it. The
Python adapter uses `build/venv_manager.py`'s `create_venv` +
`pip_install` helpers; an adapter for another ecosystem will have its own
equivalent (e.g. a Node adapter creating a local `node_modules` via `npm
ci`).

## 3. `run_tests()` — "no tests" is success, not failure

If the project has no configured test suite, return
`BuildResult(success=True, logs="No tests found — skipping.")`. That's a
fact about the project, not a problem with it. Only `success=False` when
tests exist *and fail*.

## 4. `build()` — read the packaging backend from Settings, produce one artifact

```python
backend_name = Settings.load().default_packaging_backend
backend = BACKENDS.get(backend_name, BACKENDS["pyinstaller"])
```

If your ecosystem has multiple possible packaging backends, follow the
same pattern as `engine/src/crossmith/packaging/`: one
`PackagingBackend` implementation per tool, selected by name, all
returning the same `PackageResult` shape.

**Handle the missing-system-dependency case.** This one is not
theoretical: Nuitka's Linux onefile mode fails outright if the `patchelf`
system tool isn't installed. Rather than surfacing that as a hard
failure, the Python adapter detects that specific error and falls back to
PyInstaller automatically, with a clear note in the build log explaining
what happened and how to get full support for the preferred backend
(see `python_adapter.py`'s `_is_missing_system_dependency` /
`_missing_system_dependency_hint`, and the fallback branch in `build()`).
If your backend(s) have similar sharp edges, handle them the same way —
degrade gracefully and say why, don't just fail.

## 5. `suggest_fix()` — optional, but worth it for known patterns

Given a failed `BuildResult`, return a short, human suggestion if you
recognize the failure pattern (a specific error string, a known missing
tool), or `None` if you don't. The caller falls back to the AI engine (if
the user enabled it) or just shows the raw error — your job is only to
catch the patterns you actually know about.

## 6. Register it

```toml
# pyproject.toml (of your adapter package, or engine/pyproject.toml for
# first-party adapters)
[project.entry-points."crossmith.adapters"]
your-language = "your_package.your_adapter:YourAdapter"
```

That's the entire integration surface — `adapters/registry.py` discovers
it automatically via `importlib.metadata.entry_points`. No core code
changes.

## 7. Test it — including a real build

Unit-test `detect()` against synthetic fixture directories (see
`engine/tests/test_python_adapter.py` for the pattern — no real
compilation needed, just directory/file layouts and assertions on the
`DetectionResult`).

Then add **one real, slow, end-to-end test** that actually builds a
sample project and runs the resulting binary — mark it
`@pytest.mark.slow` (excluded from the default `pytest` run; see
`engine/tests/test_build_integration.py`). A detection unit test proves
your logic is internally consistent; only an artifact that actually
executes proves the adapter works. Add the sample project itself under
`examples/`.

## Checklist before opening a PR

- [ ] `detect()` never raises, even on garbage input — returns
      `matched=False` instead
- [ ] Confidence is evidence-based, not hardcoded to a single value
- [ ] `install_dependencies()` writes only inside `env_path`
- [ ] `run_tests()` treats "no tests" as success
- [ ] `build()` reads the backend from `Settings`, not a hardcoded choice
- [ ] At least one real example project under `examples/`, with a
      `@pytest.mark.slow` test that builds it and runs the output
- [ ] Registered under `crossmith.adapters` in your `pyproject.toml`
