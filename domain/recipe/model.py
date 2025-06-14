from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from domain.shared.value_objects import Difficulty, DurationMinutes, Quantity


@dataclass(frozen=True, slots=True)
class RecipeIngredient:
    ingredient_id: str  # FK -> Ingredient.id
    qty_needed: Quantity


@dataclass(slots=True)
class Recipe:  # 可变，因为会编辑
    id: str
    name: str
    category: str  # 主食 / 主菜 / 副菜…
    method: str    # 蒸 / 炒 / 煮…
    difficulty: Difficulty
    duration_min: DurationMinutes
    duration_max: DurationMinutes
    pairings: List[str] = field(default_factory=list)
    tutorial_url: str | None = None
    notes: str | None = None
    ingredients: List[RecipeIngredient] = field(default_factory=list)

    # 业务行为示例
    def update_notes(self, new_notes: str) -> None:
        self.notes = new_notes or self.notes
