"""FastAPI application entrypoint."""
from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI
except Exception:  # pragma: no cover - allow import without FastAPI
    FastAPI = None  # type: ignore

from infra.logging import setup
from web.api.routers.recipe import router as recipe_router


def create_app() -> "FastAPI":  # type: ignore[return-type]
    """Create and configure the FastAPI application."""
    if FastAPI is None:  # pragma: no cover - import guard for tests
        raise RuntimeError("FastAPI is not installed")

    setup()
    app = FastAPI(title="Cookmate API", version="0.2.0")

    @app.get("/ping")
    async def ping() -> dict[str, str]:
        return {"msg": "pong"}

    if recipe_router is not None:  # pragma: no cover - skip if FastAPI missing
        app.include_router(recipe_router)

    return app


if FastAPI is not None:  # pragma: no cover - only defined when FastAPI available
    app = create_app()
else:  # pragma: no cover - fallback for environments without FastAPI
    app: Any | None = None
