from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import NewType


class Difficulty(Enum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()

    @staticmethod
    def from_str(label: str) -> "Difficulty":
        mapping = {
            "低": Difficulty.EASY,
            "中低": Difficulty.MEDIUM,
            "中": Difficulty.MEDIUM,
            "中高": Difficulty.HARD,
            "高": Difficulty.HARD,
        }
        return mapping[label]


DurationMinutes = NewType("DurationMinutes", int)


@dataclass(frozen=True, slots=True)
class Quantity:
    """
    不可变值对象：数量 & 单位
    """
    amount: float
    unit: str

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("amount must be positive")
        if not self.unit:
            raise ValueError("unit must be non-empty")

    def __add__(self, other: "Quantity") -> "Quantity":
        if self.unit != other.unit:
            raise ValueError("unit mismatch")
        return Quantity(self.amount + other.amount, self.unit)

    def __sub__(self, other: "Quantity") -> "Quantity":
        return self.__add__(Quantity(-other.amount, other.unit))

    def __str__(self) -> str:  # easy debug / print
        return f"{self.amount}{self.unit}"
