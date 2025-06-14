"""Dependency providers for FastAPI routes."""
from __future__ import annotations

from typing import Generator

try:
    from fastapi import Depends
except Exception:  # pragma: no cover - allow import without FastAPI
    Depends = object  # type: ignore[misc,assignment]

from app.unit_of_work import MemoryUnitOfWork, AbstractUnitOfWork
from infra.event_bus import LoggingEventBus


def get_uow() -> Generator[AbstractUnitOfWork, None, None]:
    """Provide a new unit of work per request."""
    uow = MemoryUnitOfWork()
    try:
        yield uow
    finally:
        pass


def get_event_bus() -> LoggingEventBus:
    """Return an event bus instance."""
    return LoggingEventBus()
