"""adapters.repo_sqlite.recipe_repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SQLite 实现的 ``AbstractRecipeRepo``。

> **设计取舍 (MVP)**
> 1. **两张表**：`recipes`（主表）+ `recipe_ingredients`（多对多映射）；
> 2. **JSON 列**：`steps`、`metadata` 直接存 JSON；
> 3. **Unit 以 str 保存**，Quantity.amount 用 DECIMAL；
> 4. **惰性加载 ingredients** – 查询时用 joinedload，性能够用。

领域对象 ↔ ORM 模型 转换通过私有助手实现；外部只暴露 `SqlRecipeRepo`。
"""
from __future__ import annotations

import uuid as _uuid
from typing import Iterable, Mapping

from sqlalchemy import DECIMAL, JSON, Column, ForeignKey, String, Table, select
from sqlalchemy.orm import Session, mapped_column, relationship

from domain.recipe.models import Recipe
from domain.recipe.repository import AbstractRecipeRepo
from domain.shared.value_objects import IngredientId, Quantity, RecipeId, Unit

from .db import metadata  # 同一命名约定元数据

###############################################################################
# ORM 映射
###############################################################################

class RecipeORM:  # noqa: WPS110
    """SQLAlchemy ORM for Recipe 主表。"""

    __tablename__ = "recipes"
    metadata = metadata

    id: _uuid.UUID = mapped_column("id", String(36), primary_key=True)
    name: str = mapped_column(String(100), unique=True, nullable=False)
    steps: list[str] = mapped_column(JSON, nullable=False, default=list)
    metadata_extra: Mapping[str, str] | None = mapped_column("metadata", JSON)

    ingredients = relationship(
        "RecipeIngredientORM",
        cascade="all, delete-orphan",
        back_populates="recipe",
        lazy="joined",
    )


class RecipeIngredientORM:  # noqa: WPS110
    """Recipe 与 Ingredient 映射表。"""

    __tablename__ = "recipe_ingredients"
    metadata = metadata

    recipe_id = mapped_column(String(36), ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    ingredient_id = mapped_column(String(36), nullable=False, primary_key=True)

    amount = Column(DECIMAL(12, 3), nullable=False)
    unit = Column(String(10), nullable=False)

    recipe = relationship("RecipeORM", back_populates="ingredients")

###############################################################################
# Repo 实现
###############################################################################

class SqlRecipeRepo(AbstractRecipeRepo):  # noqa: WPS110
    """基于 SQLAlchemy 的 RecipeRepo。"""

    def __init__(self, session: Session) -> None:  # noqa: D401
        self.session = session

    # ----------------------------- 查询 -----------------------------
    def get(self, recipe_id: RecipeId) -> Recipe | None:  # noqa: D401
        stmt = select(RecipeORM).where(RecipeORM.id == str(recipe_id))
        orm_obj = self.session.scalar(stmt)
        return _to_domain(orm_obj) if orm_obj else None

    def list(self) -> Iterable[Recipe]:  # noqa: D401
        stmt = select(RecipeORM)
        for orm_obj in self.session.scalars(stmt):
            yield _to_domain(orm_obj)

    def find_by_name(self, name: str) -> Recipe | None:  # noqa: D401
        stmt = select(RecipeORM).where(RecipeORM.name == name)
        orm_obj = self.session.scalar(stmt)
        return _to_domain(orm_obj) if orm_obj else None

    # ----------------------------- 写入 -----------------------------
    def add(self, recipe: Recipe) -> None:  # noqa: D401
        orm_obj = _to_orm(recipe)
        self.session.add(orm_obj)

    def update(self, recipe: Recipe) -> None:  # noqa: D401
        # 简单策略：先删除再插入（行级删除更新）；后期可改 diff 更新
        existing = self.session.get(RecipeORM, str(recipe.id))
        if existing:
            self.session.delete(existing)
        self.session.add(_to_orm(recipe))

    def remove(self, recipe_id: RecipeId) -> None:  # noqa: D401
        obj = self.session.get(RecipeORM, str(recipe_id))
        if obj:
            self.session.delete(obj)

###############################################################################
# 转换助手
###############################################################################

def _to_domain(orm: RecipeORM) -> Recipe:  # noqa: D401
    ingredients = {
        IngredientId(_uuid.UUID(row.ingredient_id)): Quantity.of(row.amount, Unit(row.unit))
        for row in orm.ingredients
    }
    return Recipe(
        id=RecipeId(_uuid.UUID(orm.id)),
        name=orm.name,
        steps=orm.steps or [],
        metadata=orm.metadata_extra or None,
        ingredients=ingredients,
    )


def _to_orm(recipe: Recipe) -> RecipeORM:  # noqa: D401
    orm = RecipeORM(
        id=str(recipe.id),
        name=recipe.name,
        steps=list(recipe.steps),
        metadata_extra=recipe.metadata,
    )
    orm.ingredients = [
        RecipeIngredientORM(
            ingredient_id=str(ing_id),
            amount=qty.amount,
            unit=qty.unit.value,
        )
        for ing_id, qty in recipe.ingredients.items()
    ]
    return orm
