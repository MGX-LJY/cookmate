"""Recipe API router."""
from __future__ import annotations

try:
    from fastapi import APIRouter, Depends, HTTPException
    from pydantic import BaseModel
except Exception:  # pragma: no cover - allow import without FastAPI/Pydantic
    APIRouter = None  # type: ignore
    Depends = None  # type: ignore
    HTTPException = Exception  # type: ignore
    class BaseModel:  # type: ignore
        pass

from app.services.recipe_service import RecipeAlreadyExistsError, RecipeService
from app.unit_of_work import AbstractUnitOfWork
from web.api.deps import get_uow


if APIRouter is not None:  # pragma: no cover - skip when FastAPI unavailable
    router = APIRouter(prefix="/recipes", tags=["recipes"])

    class RecipeCreate(BaseModel):  # noqa: D401
        """Schema for creating recipes."""

        name: str
        ingredients: dict[str, tuple[float | int | str, str]]
        steps: list[str] | None = None

    @router.get("/")
    def list_recipes(uow: AbstractUnitOfWork = Depends(get_uow)) -> list[str]:
        """Return names of all recipes."""
        service = RecipeService(uow)
        return [r.name for r in service.list_recipes()]

    @router.post("/", status_code=201)
    def create_recipe(
        data: RecipeCreate,
        uow: AbstractUnitOfWork = Depends(get_uow),
    ) -> dict[str, str]:
        """Create a new recipe."""
        service = RecipeService(uow)
        try:
            rid = service.create_recipe(
                name=data.name,
                ingredient_inputs=data.ingredients,
                steps=data.steps,
            )
        except RecipeAlreadyExistsError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return {"id": str(rid)}
else:  # pragma: no cover - placeholder
    router = None
