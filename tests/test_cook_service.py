"""domain.shared.value_objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
核心值对象 (Quantity/Unit) 及标识符定义。
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, getcontext
from enum import Enum
from typing import Final, NewType

# 设置全局 Decimal 精度
getcontext().prec = 9

###############################################################################
# 单位枚举
###############################################################################

class Unit(str, Enum):
    GRAM = "g"
    KILOGRAM = "kg"
    MILLILITER = "ml"
    LITER = "l"
    PIECE = "pcs"

    _CONVERSION: Final[dict[tuple["Unit", "Unit"], Decimal]] = {
        (GRAM, KILOGRAM): Decimal("0.001"),
        (KILOGRAM, GRAM): Decimal("1000"),
        (MILLILITER, LITER): Decimal("0.001"),
        (LITER, MILLILITER): Decimal("1000"),
    }

    def conversion_factor_to(self, target: "Unit") -> Decimal | None:  # noqa: D401
        return self._CONVERSION.get((self, target))

###############################################################################
# Quantity 值对象
###############################################################################

@dataclass(frozen=True, slots=True)
class Quantity:  # noqa: WPS110
    amount: Decimal
    unit: Unit

    # ---------- 工厂 ----------
    @classmethod
    def of(cls, amount: "int | float | str | Decimal", unit: Unit) -> "Quantity":
        try:
            value = Decimal(str(amount))
        except InvalidOperation as exc:  # noqa: WPS110
            raise ValueError(f"非法数值: {amount}") from exc
        return cls(value, unit)

    # ---------- 单位转换 ----------
    def to(self, target_unit: Unit) -> "Quantity":
        if self.unit == target_unit:
            return self
        factor = self.unit.conversion_factor_to(target_unit)
        if factor is None:
            raise ValueError("单位不兼容，无法转换")
        return Quantity(self.amount * factor, target_unit)

    # ---------- 算术 ----------
    def _ensure_same_unit(self, other: "Quantity") -> tuple[Decimal, Decimal]:
        if self.unit == other.unit:
            return self.amount, other.amount
        converted = other.to(self.unit)
        return self.amount, converted.amount

    def __add__(self, other: "Quantity") -> "Quantity":
        a1, a2 = self._ensure_same_unit(other)
        return Quantity(a1 + a2, self.unit)

    def __sub__(self, other: "Quantity") -> "Quantity":
        a1, a2 = self._ensure_same_unit(other)
        result = a1 - a2
        if result < 0:
            raise ValueError("结果为负，非法")
        return Quantity(result, self.unit)

    # 与数字相乘 / 除
    def __mul__(self, factor: "int | float | Decimal") -> "Quantity":  # noqa: WPS110
        try:
            fac = Decimal(str(factor))
        except InvalidOperation as exc:  # noqa: WPS110
            raise TypeError("Quantity 只能与数值相乘") from exc
        return Quantity(self.amount * fac, self.unit)

    __rmul__ = __mul__

    def __truediv__(self, divisor: "int | float | Decimal") -> "Quantity":  # noqa: WPS110
        try:
            div = Decimal(str(divisor))
        except InvalidOperation as exc:  # noqa: WPS110
            raise TypeError("Quantity 只能除以数值") from exc
        if div == 0:
            raise ZeroDivisionError
        return Quantity(self.amount / div, self.unit)

    # ---------- 比较 ----------
    def __lt__(self, other: "Quantity") -> bool:  # noqa: WPS110
        a1, a2 = self._ensure_same_unit(other)
        return a1 < a2

    def __le__(self, other: "Quantity") -> bool:  # noqa: WPS110
        a1, a2 = self._ensure_same_unit(other)
        return a1 <= a2

    def __eq__(self, other: object) -> bool:  # noqa: WPS110
        if not isinstance(other, Quantity):
            return NotImplemented
        a1, a2 = self._ensure_same_unit(other)
        return a1 == a2

    def __hash__(self) -> int:  # noqa: D401
        return hash((self.amount, self.unit))

    def __repr__(self) -> str:  # noqa: D401
        return f"Quantity(amount={self.amount}, unit={self.unit})"

###############################################################################
# 聚合根标识符
###############################################################################

RecipeId = NewType("RecipeId", uuid.UUID)
IngredientId = NewType("IngredientId", uuid.UUID)


def new_recipe_id() -> RecipeId:  # noqa: D401
    return RecipeId(uuid.uuid4())


def new_ingredient_id() -> IngredientId:  # noqa: D401
    return IngredientId(uuid.uuid4())
