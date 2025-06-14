"""
In-memory implementation of RecipeRepository.
适用于单元测试 / 原型期，无持久化。
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Iterable

from domain.recipe.model import Recipe
from domain.recipe.ports import RecipeRepository


class InMemoryRecipeRepository(RecipeRepository):  # type: ignore[misc]
    """A simple dict-backed repository for Recipe aggregates."""

    def __init__(self) -> None:
        # recipe_id -> Recipe
        self._data: "OrderedDict[str, Recipe]" = OrderedDict()

    # ----------------------
    #  RecipeRepository API
    # ----------------------
    def by_id(self, recipe_id: str) -> Recipe | None:
        return self._data.get(recipe_id)

    def list_all(self) -> Iterable[Recipe]:
        # 返回一份拷贝，避免外部误改
        return list(self._data.values())

    def save(self, recipe: Recipe) -> None:
        self._data[recipe.id] = recipe

    def delete(self, recipe_id: str) -> None:
        self._data.pop(recipe_id, None)


# 让 “from adapters.repo_memory import InMemoryRecipeRepository” 生效
__all__ = ["InMemoryRecipeRepository"]
