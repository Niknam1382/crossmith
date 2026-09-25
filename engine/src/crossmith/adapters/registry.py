"""Adapter registry — discovers installed adapters via Python entry points.

Community adapters ship as separate packages (e.g. `crossmith-adapter-nodejs`)
and register under the `crossmith.adapters` entry-point group. No code in
this file changes when a new language is added.
"""

from __future__ import annotations

from collections.abc import Iterator
from importlib.metadata import entry_points

from crossmith.adapters.base import Adapter
from crossmith.logging_config import configure_logging

_ENTRY_POINT_GROUP = "crossmith.adapters"

logger = configure_logging()


def discover_adapters() -> Iterator[Adapter]:
    """Instantiate every adapter installed in the current environment.

    A single broken adapter is logged and skipped rather than crashing the
    whole app — one bad plugin should never take down Crossmith.
    """
    for ep in entry_points(group=_ENTRY_POINT_GROUP):
        try:
            adapter_cls = ep.load()
            yield adapter_cls()
        except Exception:
            logger.warning("Failed to load adapter %r, skipping", ep.name, exc_info=True)
