from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True, slots=True)
class Ingredient:
    id: str
    name: str
    unit: str           # 克 / 个 / 勺…
    aliases: List[str]  # 同义词
    default_shelf_life_days: int | None = None
