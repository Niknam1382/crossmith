# Local AI assist (Needle)

Optional, off by default. This is Phase 4 from the [roadmap](../../README.md#roadmap).

## What it does

Crossmith's detection is deterministic by default: plain file/manifest
heuristics, no model involved, and it's right most of the time for
well-structured projects. AI assist is a fallback for the cases it isn't —
a project with an unusual layout, no recognizable manifest, or a mix of
languages that confuses every adapter.

When enabled, and only when every installed adapter's `detect()` came back
empty or below the confidence threshold (see `detection/engine.py`'s
`CONFIDENCE_THRESHOLD`), Crossmith:

1. Builds a small evidence snippet: the project's top-level file listing,
   plus the contents of any common manifest file that's present
   (`pyproject.toml`, `package.json`, `Cargo.toml`, etc.), truncated to a
   few KB.
2. Passes that to a local model ([cactus-compute/needle](https://github.com/cactus-compute/needle),
   via the `cactus-needle` PyPI package) asking it to fill in a
   `language` / `framework` / `entry_point` / `dependencies` schema.
3. Only surfaces the result if the model's own calibrated `confidence`
   score clears `needle_engine.CONFIDENCE_THRESHOLD` (0.65). Below that,
   or on any error, timeout, or missing dependency, Crossmith behaves
   exactly as if AI assist were off — see "Never load-bearing" below.

The same model is also consulted, the same way, as a last-resort source
for a *build failure's* plain-language explanation — but only after the
adapter's own `suggest_fix()` had nothing to say (see
`adapters/base.py`'s `Adapter.suggest_fix` docstring).

An AI-assisted detection result is never silently acted on: it's appended
to the result list, still subject to the same confidence gate as every
deterministic result, and the desktop UI marks it with an "AI-assisted
guess" badge plus its `reasons` list so it's never mistaken for a
confident deterministic match.

## Turning it on

```bash
pip install "crossmith-engine[ai]"      # pulls in cactus-needle
```

Then flip the toggle in the desktop app's Settings page ("Local AI
assist"), or set `ai_assist_enabled = true` directly in
`~/.crossmith/config.toml`. The first time it actually runs, it fetches
the ~14MB model from Hugging Face and caches it; after that, every call is
fully local.

## Never load-bearing

This is the one rule the whole feature is built around (see
`docs/DECISIONS.md`'s "Local AI" row and `ai/base.py`'s `AIEngine`
docstring): nothing anywhere else in Crossmith may assume AI assist is
available. Concretely, `NeedleEngine`:

- Checks `cactus-needle` is importable before doing anything else
  (`is_available()`), and skips straight to "no result" if not — this is
  what makes the `ai` extra truly optional. Verified by running the full
  test suite in a venv with `cactus-needle` not installed at all: same
  35/35 pass.
- Wraps every real call in a hard 20-second timeout on a background
  thread, so a slow or stalled first-time weights download can never
  block a scan or a build.
- Catches every exception, not just the expected ones. Verified by hand:
  calling `agent.complete(...)` with no network access to Hugging Face
  raises `huggingface_hub.errors.LocalEntryNotFoundError` — quickly, not
  a hang — and that's exactly the kind of failure this catch-all is for.

## What's tested and what isn't

Tested (`engine/tests/test_ai.py`, all mocked, no real model calls,
included in the default fast test run):

- The disabled/not-installed/available branches of `get_ai_engine`.
- Confidence gating (accepted above threshold, discarded below it, and
  discarded on Needle's own "no tool fits" empty-call response).
- Exceptions and timeouts are absorbed, never raised to the caller.
- `scan_project` only ever calls the AI engine when deterministic
  detection is already unsure, and a confident deterministic match is
  never displaced by a lower-confidence AI one.
- `run_build`'s error-explanation fallback: AI is only consulted when the
  adapter's own `suggest_fix()` returned `None`.

**Not tested**: an actual successful Needle inference call. This sandbox
has no network route to `huggingface.co`, only to PyPI/GitHub/npm, so the
one-time weights download can't complete here — every real call in this
environment fails with `LocalEntryNotFoundError`, which is itself a
useful (and now verified) data point about the fallback path, but it
means the "happy path" — a real detection hint or build explanation
actually coming back from the model — has not been observed end to end
anywhere yet. If you have real internet access when you try this, that's
the first real-world test of it; please report back what you see
(correct guess, wrong guess, or no result) so the confidence threshold
above can be tuned against real data instead of a guess.

## Confidence threshold

`needle_engine.CONFIDENCE_THRESHOLD = 0.65` is a starting guess, not a
tuned value — there's no real usage data yet to tune it against. If it
turns out too strict (rarely surfaces a hint) or too loose (surfaces
wrong guesses), that's expected to need adjusting once real usage exists.
