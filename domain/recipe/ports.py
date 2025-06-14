from __future__ import annotations

from typing import Iterable, Protocol

from domain.recipe.model import Recipe


class RecipeRepository(Protocol):
    """领域层只依赖这个接口"""

    def by_id(self, recipe_id: str) -> Recipe | None: ...

    def list_all(self) -> Iterable[Recipe]: ...

    def save(self, recipe: Recipe) -> None: ...

    def delete(self, recipe_id: str) -> None: ...
