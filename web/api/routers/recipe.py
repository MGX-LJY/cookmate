"""Recipe API router."""
from __future__ import annotations

try:
    from fastapi import APIRouter, Depends, HTTPException, Response
    from pydantic import BaseModel
except Exception:  # pragma: no cover - allow import without FastAPI/Pydantic
    APIRouter = None  # type: ignore
    Depends = None  # type: ignore
    HTTPException = Exception  # type: ignore
    class BaseModel:  # type: ignore
        pass

from app.services.recipe_service import (
    RecipeAlreadyExistsError,
    RecipeNotFoundError,
    RecipeService,
)
from domain.recipe.models import Recipe
from app.unit_of_work import AbstractUnitOfWork
from web.api.deps import get_uow


if APIRouter is not None:  # pragma: no cover - skip when FastAPI unavailable
    router = APIRouter(prefix="/recipes", tags=["recipes"])

    class RecipeCreate(BaseModel):  # noqa: D401
        """Schema for creating recipes."""

        name: str
        ingredients: dict[str, tuple[float | int | str, str]]
        steps: list[str] | None = None
        category: str | None = None
        method: str | None = None
        difficulty: str | None = None
        pairing: str | None = None
        time_minutes: int | None = None
        tutorial: str | None = None

    class MetaField(BaseModel):  # noqa: D401
        """Single metadata value."""

        value: str

    class IngredientsIn(BaseModel):  # noqa: D401
        """Replace ingredients."""

        ingredients: dict[str, tuple[float | int | str, str]]

    @router.get("/")
    def list_recipes(uow: AbstractUnitOfWork = Depends(get_uow)) -> list[str]:
        """Return names of all recipes."""
        service = RecipeService(uow)
        return [r.name for r in service.list_recipes()]

    def _serialize_recipe(uow: AbstractUnitOfWork, recipe: Recipe) -> dict:
        with uow as tx:
            ingredients = {}
            for iid, qty in recipe.ingredients.items():
                ing = tx.ingredients.get(iid)
                name = ing.name if ing else str(iid)
                ingredients[name] = [float(qty.amount), qty.unit.value]
        return {
            "name": recipe.name,
            "ingredients": ingredients,
            "steps": list(recipe.steps),
            "metadata": recipe.metadata or {},
        }

    @router.get("/{name}")
    def get_recipe(name: str, uow: AbstractUnitOfWork = Depends(get_uow)) -> dict:
        svc = RecipeService(uow)
        try:
            recipe = svc.get_by_name(name)
        except RecipeNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        return _serialize_recipe(uow, recipe)

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
                metadata={
                    k: str(v)
                    for k, v in {
                        "category": data.category,
                        "method": data.method,
                        "difficulty": data.difficulty,
                        "pairing": data.pairing,
                        "time_minutes": data.time_minutes,
                        "tutorial": data.tutorial,
                    }.items()
                    if v is not None
                },
            )
        except RecipeAlreadyExistsError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return {"id": str(rid)}

    @router.delete("/{name}", status_code=204, response_class=Response)
    def delete_recipe(
        name: str,
        uow: AbstractUnitOfWork = Depends(get_uow),
    ) -> Response:
        """Delete a recipe by name."""
        service = RecipeService(uow)
        try:
            service.remove_recipe(name)
        except RecipeNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        return Response(status_code=204)

    # ---------------------------------------------------------------
    # 单字段更新接口
    # ---------------------------------------------------------------

    def _update(name: str, key: str, value: str, uow: AbstractUnitOfWork) -> None:
        svc = RecipeService(uow)
        try:
            svc.update_metadata_field(name, key, value)
        except RecipeNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.patch("/{name}/category")
    def set_category(
        name: str,
        data: MetaField,
        uow: AbstractUnitOfWork = Depends(get_uow),
    ) -> dict[str, str]:
        _update(name, "category", data.value, uow)
        return {"msg": "ok"}

    @router.patch("/{name}/method")
    def set_method(name: str, data: MetaField, uow: AbstractUnitOfWork = Depends(get_uow)) -> dict[str, str]:
        _update(name, "method", data.value, uow)
        return {"msg": "ok"}

    @router.patch("/{name}/difficulty")
    def set_difficulty(name: str, data: MetaField, uow: AbstractUnitOfWork = Depends(get_uow)) -> dict[str, str]:
        _update(name, "difficulty", data.value, uow)
        return {"msg": "ok"}

    @router.patch("/{name}/pairing")
    def set_pairing(name: str, data: MetaField, uow: AbstractUnitOfWork = Depends(get_uow)) -> dict[str, str]:
        _update(name, "pairing", data.value, uow)
        return {"msg": "ok"}

    @router.patch("/{name}/time_minutes")
    def set_time(name: str, data: MetaField, uow: AbstractUnitOfWork = Depends(get_uow)) -> dict[str, str]:
        _update(name, "time_minutes", data.value, uow)
        return {"msg": "ok"}

    @router.patch("/{name}/tutorial")
    def set_tutorial(name: str, data: MetaField, uow: AbstractUnitOfWork = Depends(get_uow)) -> dict[str, str]:
        _update(name, "tutorial", data.value, uow)
        return {"msg": "ok"}

    @router.patch("/{name}/ingredients")
    def set_ingredients(
        name: str,
        data: IngredientsIn,
        uow: AbstractUnitOfWork = Depends(get_uow),
    ) -> dict[str, str]:
        svc = RecipeService(uow)
        try:
            svc.update_ingredients(name, data.ingredients)
        except RecipeNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        return {"msg": "ok"}
else:  # pragma: no cover - placeholder
    router = None
