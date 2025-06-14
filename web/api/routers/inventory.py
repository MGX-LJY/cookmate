"""Inventory API router."""
from __future__ import annotations

from datetime import date

try:
    from fastapi import APIRouter, Depends, HTTPException, Response
    from pydantic import BaseModel
except Exception:  # pragma: no cover - allow import without FastAPI/Pydantic
    APIRouter = None  # type: ignore
    Depends = None  # type: ignore
    HTTPException = Exception  # type: ignore
    class BaseModel:  # type: ignore
        pass

from app.unit_of_work import AbstractUnitOfWork
from domain.inventory.models import InventoryItem
from domain.shared.value_objects import Quantity, Unit
from web.api.deps import get_uow

if APIRouter is not None:  # pragma: no cover - skip when FastAPI unavailable
    router = APIRouter(prefix="/inventory", tags=["inventory"])

    class InventoryIn(BaseModel):  # noqa: D401
        """Schema for adding or updating inventory."""

        ingredient: str
        amount: float | int | str
        unit: str
        expires_on: date | None = None

    class InventoryOut(BaseModel):  # noqa: D401
        """Inventory item representation."""

        ingredient: str
        amount: float
        unit: str
        expires_on: date | None = None

    def _serialize_item(uow: AbstractUnitOfWork, item: InventoryItem) -> InventoryOut:
        ing = uow.ingredients.get(item.ingredient_id)
        name = ing.name if ing else str(item.ingredient_id)
        return InventoryOut(
            ingredient=name,
            amount=float(item.quantity.amount),
            unit=item.quantity.unit.value,
            expires_on=item.expires_on,
        )

    @router.get("/")
    def list_inventory(uow: AbstractUnitOfWork = Depends(get_uow)) -> list[InventoryOut]:
        """Return current inventory list."""
        with uow as tx:
            return [_serialize_item(tx, item) for item in tx.inventories.list()]

    @router.get("/low")
    def low_stock(uow: AbstractUnitOfWork = Depends(get_uow)) -> list[InventoryOut]:
        """Return low stock items."""
        with uow as tx:
            return [_serialize_item(tx, item) for item in tx.inventories.low_stock()]

    @router.get("/expiring")
    def expiring(
        days: int = 3,
        uow: AbstractUnitOfWork = Depends(get_uow),
    ) -> list[InventoryOut]:
        """Items expiring within given days."""
        with uow as tx:
            return [
                _serialize_item(tx, item) for item in tx.inventories.expiring_soon(days)
            ]

    @router.post("/", status_code=201)
    def add_or_update_inventory(
        data: InventoryIn,
        uow: AbstractUnitOfWork = Depends(get_uow),
    ) -> dict[str, str]:
        """Add or update an inventory item."""
        with uow as tx:
            ing = tx.ingredients.find_by_name(data.ingredient)
            if not ing:
                raise HTTPException(status_code=404, detail="Ingredient not found")
            qty = Quantity.of(data.amount, Unit(data.unit))
            tx.inventories.add_or_update(
                InventoryItem(
                    ingredient_id=ing.id,
                    quantity=qty,
                    expires_on=data.expires_on,
                )
            )
        return {"ingredient_id": str(ing.id)}

    @router.delete("/{ingredient}", status_code=204, response_class=Response)
    def remove_inventory(
        ingredient: str,
        uow: AbstractUnitOfWork = Depends(get_uow),
    ) -> Response:
        """Remove an inventory item by ingredient name."""
        with uow as tx:
            ing = tx.ingredients.find_by_name(ingredient)
            if not ing:
                raise HTTPException(status_code=404, detail="Ingredient not found")
            tx.inventories.remove(ing.id)
        return Response(status_code=204)
else:  # pragma: no cover - placeholder
    router = None

