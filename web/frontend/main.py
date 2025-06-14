"""Frontend demo using FastAPI static files."""
from __future__ import annotations

from pathlib import Path

try:
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
except Exception:  # pragma: no cover - fastapi missing
    FastAPI = None  # type: ignore
    StaticFiles = None  # type: ignore


def create_app() -> "FastAPI":  # type: ignore[return-type]
    """Serve static frontend files."""
    if FastAPI is None or StaticFiles is None:  # pragma: no cover - import guard
        raise RuntimeError("FastAPI is not installed")

    app = FastAPI(title="Cookmate Frontend", version="0.3.0")
    static_dir = Path(__file__).parent / "static"
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    return app


if FastAPI is not None:  # pragma: no cover - ensure FastAPI available
    app = create_app()
else:  # pragma: no cover - placeholder when FastAPI not installed
    app = None
