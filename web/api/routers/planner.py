"""Planner API router."""
from __future__ import annotations

import uuid
from typing import Mapping

try:
    from fastapi import APIRouter, Depends, HTTPException
    from pydantic import BaseModel
except Exception:  # pragma: no cover - allow import without FastAPI/Pydantic
    APIRouter = None  # type: ignore
    Depends = None  # type: ignore
    HTTPException = Exception  # type: ignore
    class BaseModel:  # type: ignore
        pass

from app.services.planner_service import PlannerService
from domain.shared.value_objects import RecipeId
from web.api.deps import get_uow
from app.unit_of_work import AbstractUnitOfWork

if APIRouter is not None:  # pragma: no cover - skip when FastAPI unavailable
    router = APIRouter(prefix="/planner", tags=["planner"])

    class ShoppingRequest(BaseModel):  # noqa: D401
        """Desired recipes and servings."""

        recipes: Mapping[str, int] | None = None

    class ShoppingItem(BaseModel):  # noqa: D401
        """Item in shopping list."""

        ingredient: str
        amount: float
        unit: str

    @router.get("/cookable")
    def cookable_recipes(
        servings: int = 1,
        uow: AbstractUnitOfWork = Depends(get_uow),
    ) -> list[str]:
        """Return names of cookable recipes."""
        service = PlannerService(uow)
        recipes = service.list_cookable_recipes(servings)
        return [r.name for r in recipes]

    @router.post("/shopping")
    def shopping_list(
        data: ShoppingRequest,
        uow: AbstractUnitOfWork = Depends(get_uow),
    ) -> list[ShoppingItem]:
        """Generate shopping list for desired recipes."""
        desired = None
        if data.recipes:
            try:
                desired = {RecipeId(uuid.UUID(k)): v for k, v in data.recipes.items()}
            except ValueError as exc:  # noqa: WPS110
                raise HTTPException(status_code=400, detail=str(exc))
        service = PlannerService(uow)
        shopping = service.generate_shopping_list(desired)
        items = []
        with uow as tx:
            for ing_id, qty in shopping.items():
                ing = tx.ingredients.get(ing_id)
                name = ing.name if ing else str(ing_id)
                items.append(
                    ShoppingItem(
                        ingredient=name,
                        amount=float(qty.amount),
                        unit=qty.unit.value,
                    )
                )
        return items
else:  # pragma: no cover - placeholder
    router = None
