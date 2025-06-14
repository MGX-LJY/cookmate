"""adapters.repo_sqlite.ingredient_repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SQLite 实现的 ``AbstractIngredientRepo``。

MVP 采用**单表模型** `ingredients`：
* `id` (PK, UUID str)
* `name` varchar(100) UNIQUE
* `default_unit` varchar(10)
* `metadata` JSON 可空

领域对象 ↔ ORM 模型 转换保持不可变语义。
"""
from __future__ import annotations

import uuid as _uuid
from typing import Iterable, Mapping

from sqlalchemy import JSON, String, select
from sqlalchemy.orm import Session, mapped_column

from domain.ingredient.models import Ingredient
from domain.ingredient.repository import AbstractIngredientRepo
from domain.shared.value_objects import IngredientId, Unit

from .db import metadata

###############################################################################
# ORM 映射
###############################################################################

class IngredientORM:  # noqa: WPS110
    """SQLAlchemy ORM for Ingredient."""

    __tablename__ = "ingredients"
    metadata = metadata

    id: str = mapped_column(String(36), primary_key=True)
    name: str = mapped_column(String(100), unique=True, nullable=False)
    default_unit: str = mapped_column(String(10), nullable=False)

    metadata_extra: Mapping[str, str] | None = mapped_column("metadata", JSON)

###############################################################################
# Repo 实现
###############################################################################

class SqlIngredientRepo(AbstractIngredientRepo):  # noqa: WPS110
    """基于 SQLAlchemy 的 IngredientRepo。"""

    def __init__(self, session: Session) -> None:  # noqa: D401
        self.session = session

    # ----------------------------- 查询 -----------------------------
    def get(self, ingredient_id: IngredientId) -> Ingredient | None:  # noqa: D401
        orm = self.session.get(IngredientORM, str(ingredient_id))
        return _to_domain(orm) if orm else None

    def list(self) -> Iterable[Ingredient]:  # noqa: D401
        stmt = select(IngredientORM)
        for orm in self.session.scalars(stmt):
            yield _to_domain(orm)

    def find_by_name(self, name: str) -> Ingredient | None:  # noqa: D401
        stmt = select(IngredientORM).where(IngredientORM.name == name)
        orm = self.session.scalar(stmt)
        return _to_domain(orm) if orm else None

    # ----------------------------- 写入 -----------------------------
    def add(self, ingredient: Ingredient) -> None:  # noqa: D401
        self.session.add(_to_orm(ingredient))

    def update(self, ingredient: Ingredient) -> None:  # noqa: D401
        existing = self.session.get(IngredientORM, str(ingredient.id))
        if existing:
            self.session.delete(existing)
        self.session.add(_to_orm(ingredient))

    def remove(self, ingredient_id: IngredientId) -> None:  # noqa: D401
        obj = self.session.get(IngredientORM, str(ingredient_id))
        if obj:
            self.session.delete(obj)

###############################################################################
# 转换助手
###############################################################################

def _to_domain(orm: IngredientORM) -> Ingredient:  # noqa: D401
    return Ingredient(
        id=IngredientId(_uuid.UUID(orm.id)),
        name=orm.name,
        default_unit=Unit(orm.default_unit),
        metadata=orm.metadata_extra or None,
    )


def _to_orm(ing: Ingredient) -> IngredientORM:  # noqa: D401
    return IngredientORM(
        id=str(ing.id),
        name=ing.name,
        default_unit=ing.default_unit.value,
        metadata_extra=ing.metadata,
    )
