"""adapters.repo_sqlite.inventory_repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SQLite 实现的 ``AbstractInventoryRepo``。

设计笔记
---------
* **单表模型** `inventory_items`：`
  ingredient_id (PK, FK)`, `amount`, `unit`, `expires_on`。
* **Quantity 表现**：`amount` DECIMAL(12,3) + `unit` varchar(10)。
* 业务筛选 `low_stock` 与 `expiring_soon(days)` 直接在 Python 层过滤，
  MVP 不做复杂 SQL；后期可改视图 / 物化列。
"""
from __future__ import annotations

import datetime as _dt
import uuid as _uuid
from typing import Iterable, Mapping

from sqlalchemy import DECIMAL, Date, ForeignKey, String, select
from sqlalchemy.orm import Session, mapped_column

from domain.inventory.models import InventoryItem
from domain.inventory.repository import AbstractInventoryRepo
from domain.shared.value_objects import IngredientId, Quantity, Unit

from .db import metadata

###############################################################################
# ORM 映射
###############################################################################

class InventoryItemORM:  # noqa: WPS110
    """SQLAlchemy ORM for InventoryItem."""

    __tablename__ = "inventory_items"
    metadata = metadata

    ingredient_id: str = mapped_column(String(36), primary_key=True)
    amount = mapped_column(DECIMAL(12, 3), nullable=False)
    unit = mapped_column(String(10), nullable=False)

    expires_on = mapped_column(Date, nullable=True)

###############################################################################
# Repo 实现
###############################################################################

class SqlInventoryRepo(AbstractInventoryRepo):  # noqa: WPS110
    """基于 SQLAlchemy 的 InventoryRepo。"""

    def __init__(self, session: Session) -> None:  # noqa: D401
        self.session = session

    # ----------------------------- 查询 -----------------------------
    def get(self, ingredient_id: IngredientId) -> InventoryItem | None:  # noqa: D401
        orm = self.session.get(InventoryItemORM, str(ingredient_id))
        return _to_domain(orm) if orm else None

    def list(self) -> Iterable[InventoryItem]:  # noqa: D401
        stmt = select(InventoryItemORM)
        for orm in self.session.scalars(stmt):
            yield _to_domain(orm)

    def low_stock(self) -> Iterable[InventoryItem]:  # noqa: D401
        return [item for item in self.list() if item.is_low_stock()]

    def expiring_soon(self, days: int = 3) -> Iterable[InventoryItem]:  # noqa: D401
        today = _dt.date.today()
        return [
            item
            for item in self.list()
            if item.expires_on and today <= item.expires_on <= today + _dt.timedelta(days=days)
        ]

    # ----------------------------- 写入 -----------------------------
    def add_or_update(self, item: InventoryItem) -> None:  # noqa: D401
        existing = self.session.get(InventoryItemORM, str(item.ingredient_id))
        orm = _to_orm(item)
        if existing:
            # 覆盖写
            self.session.delete(existing)
        self.session.add(orm)

    def remove(self, ingredient_id: IngredientId) -> None:  # noqa: D401
        obj = self.session.get(InventoryItemORM, str(ingredient_id))
        if obj:
            self.session.delete(obj)

###############################################################################
# 转换助手
###############################################################################

def _to_domain(orm: InventoryItemORM) -> InventoryItem:  # noqa: D401
    quantity = Quantity.of(orm.amount, Unit(orm.unit))
    return InventoryItem(
        ingredient_id=IngredientId(_uuid.UUID(orm.ingredient_id)),
        quantity=quantity,
        expires_on=orm.expires_on,
    )


def _to_orm(item: InventoryItem) -> InventoryItemORM:  # noqa: D401
    return InventoryItemORM(
        ingredient_id=str(item.ingredient_id),
        amount=item.quantity.amount,
        unit=item.quantity.unit.value,
        expires_on=item.expires_on,
    )
