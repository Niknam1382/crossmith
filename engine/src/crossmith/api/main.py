"""Crossmith engine entrypoint.

A loopback-only FastAPI app, spawned as a sidecar process by the desktop
shell. Never binds to 0.0.0.0 — see SECURITY.md.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from crossmith import __version__
from crossmith.detection.engine import needs_manual_review, scan_project
from crossmith.logging_config import configure_logging
from crossmith.settings import Settings

logger = configure_logging()

app = FastAPI(title="Crossmith Engine", version=__version__)

# The Tauri webview is the only intended caller. Loopback binding (see run(),
# below) is the real security boundary; this is a secondary guard.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["tauri://localhost", "http://localhost:1420"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    version: str


class ScanRequest(BaseModel):
    project_path: str


class ScanResponse(BaseModel):
    matches: list[dict]
    needs_manual_review: bool


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@app.get("/settings", response_model=Settings)
def get_settings() -> Settings:
    return Settings.load()


@app.put("/settings", response_model=Settings)
def update_settings(settings: Settings) -> Settings:
    settings.save()
    return settings


@app.post("/projects/scan", response_model=ScanResponse)
def scan(request: ScanRequest) -> ScanResponse:
    path = Path(request.project_path).expanduser().resolve()
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"No such path: {path}")

    results = scan_project(path)
    logger.info("Scanned %s -> %d match(es)", path, len(results))
    return ScanResponse(
        matches=[r.__dict__ for r in results],
        needs_manual_review=needs_manual_review(results),
    )


def run() -> None:
    """Console-script entrypoint (see pyproject.toml `[project.scripts]`).

    Loopback ONLY. The desktop shell picks the port and passes it via the
    CROSSMITH_PORT env var; 8765 is just the standalone/dev default.
    """
    import os

    import uvicorn

    port = int(os.environ.get("CROSSMITH_PORT", "8765"))
    uvicorn.run(app, host="127.0.0.1", port=port, log_config=None)


if __name__ == "__main__":
    run()
