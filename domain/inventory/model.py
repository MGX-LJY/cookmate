from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from domain.shared.value_objects import Quantity


@dataclass(frozen=True, slots=True)
class InventoryItem:
    id: str
    ingredient_id: str
    qty: Quantity
    location: str          # 冷冻 / 冷藏 / 常温
    expiry_date: date
