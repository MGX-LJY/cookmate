"""domain.shared.value_objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
核心值对象（Value Objects）定义。

值对象在领域驱动设计 (DDD) 中有两个关键特性：
1. **不可变 (Immutable)** —— 创建后其状态不能再被修改，只能整体替换；
2. **基于值相等 (Equality by Value)** —— 判断两个 VO 是否相等看其内部值是否相同，而非内存地址。

本模块为 *Cookmate* 定义三个典型值对象：

* ``Unit`` —— 计量单位枚举；可扩展，带基础换算系数；
* ``Quantity`` —— 数量 + 单位的组合，提供加减、比较与单位换算；
* ``RecipeId`` / ``IngredientId`` —— 聚合根标识符，基于 ``uuid.UUID``，保证跨进程唯一。

所有类均带有中文注释，方便团队（特别是非英语母语成员）理解。

Usage 示例::

    >>> from domain.shared.value_objects import Quantity, Unit
    >>> q1 = Quantity(500, Unit.GRAM)
    >>> q1.to(Unit.KILOGRAM)
    Quantity(amount=Decimal('0.5'), unit=<Unit.KILOGRAM: 'kg'>)
    >>> q1 + Quantity(0.3, Unit.KILOGRAM)
    Quantity(amount=Decimal('0.8'), unit=<Unit.KILOGRAM: 'kg'>)
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, getcontext
from enum import Enum
from typing import Final, NewType

# 设定 Decimal 全局精度，足以应对烹饪场景（克/毫升通常不会超过 3 位小数）。
getcontext().prec = 9  # noqa: WPS432 (魔法数字)：业务上精度固定即可

###############################################################################
# 计量单位
###############################################################################

class Unit(str, Enum):
    """支持的计量单位。"""

    GRAM: str = "g"
    KILOGRAM: str = "kg"
    MILLILITER: str = "ml"
    LITER: str = "l"
    PIECE: str = "pcs"  # 计数单位，例如 “个 / 只”

    # 可根据需要继续扩展，如 TAEL(两)、TABLESPOON(Tbsp) 等

    # WHY: 枚举成员值使用常见英文缩写，既保证唯一性又便于序列化/展示。

    # ------------------------ 换算系数表 ----------------------------------
    # 设计上放到枚举内部，方便读取；若后期需要动态扩展，可迁移到配置表/
    # 数据库存量化。
    _CONVERSION: Final[dict[tuple["Unit", "Unit"], Decimal]] = {
        (GRAM, KILOGRAM): Decimal("0.001"),
        (KILOGRAM, GRAM): Decimal("1000"),
        (MILLILITER, LITER): Decimal("0.001"),
        (LITER, MILLILITER): Decimal("1000"),
    }

    def conversion_factor_to(self, target: "Unit") -> Decimal | None:  # noqa: WPS110
        """返回当前单位转换到 *target* 的系数；若无直接转换则返回 ``None``。"""
        return self._CONVERSION.get((self, target))


###############################################################################
# 数量值对象
###############################################################################

@dataclass(frozen=True, slots=True)
class Quantity:  # noqa: WPS110 (允许类名直白表达领域概念)
    """数量 + 单位。

    * **不可变**：使用 ``@dataclass(frozen=True)`` 保证实例创建后属性只读。
    * **槽优化**：``slots=True`` 节省内存，加快属性访问；
    * **小数精度**：使用 ``decimal.Decimal`` 避免浮点误差。
    """

    amount: Decimal = field(metadata={"doc": "数值部分"})
    unit: Unit = field(metadata={"doc": "计量单位"})

    # ---------------------------------------------------------------------
    # 工厂方法
    # ---------------------------------------------------------------------

    @classmethod
    def of(cls, amount: "int | float | str | Decimal", unit: Unit) -> "Quantity":
        """辅助构建函数，自动将 *amount* 转为 ``Decimal``。"""
        try:
            value = Decimal(str(amount))
        except InvalidOperation as exc:  # noqa: WPS110
            raise ValueError(f"非法数值: {amount}") from exc
        return cls(value, unit)

    # ---------------------------------------------------------------------
    # 单位换算
    # ---------------------------------------------------------------------

    def to(self, target_unit: Unit) -> "Quantity":
        """转换为 *target_unit*；若转换路径不存在则抛 ``ValueError``。"""
        if self.unit == target_unit:
            return self  # 同单位直接返回自身（VO 不变，可以安全共享）

        factor = self.unit.conversion_factor_to(target_unit)
        if factor is None:
            raise ValueError(f"无法从 {self.unit.value} 转换到 {target_unit.value}")

        return Quantity(self.amount * factor, target_unit)

    # ---------------------------------------------------------------------
    # 算术运算
    # ---------------------------------------------------------------------

    def _ensure_same_unit(self, other: "Quantity") -> tuple[Decimal, Decimal]:  # noqa: D401
        """校验/转换单位，返回同单位下的 *self*, *other* 数值。"""
        if self.unit == other.unit:
            return self.amount, other.amount
        # 尝试将 other 转为 self 的单位
        try:
            converted_other = other.to(self.unit)
        except ValueError as exc:  # noqa: WPS110
            raise ValueError("单位不兼容，无法计算") from exc
        return self.amount, converted_other.amount

    def __add__(self, other: "Quantity") -> "Quantity":
        a1, a2 = self._ensure_same_unit(other)
        return Quantity(a1 + a2, self.unit)

    def __sub__(self, other: "Quantity") -> "Quantity":
        a1, a2 = self._ensure_same_unit(other)
        result = a1 - a2
        if result < 0:
            raise ValueError("结果数量为负数，不合理")
        return Quantity(result, self.unit)

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

    # ---------------------------------------------------------------------
    # 比较运算（基于量值统一单位后比较）
    # ---------------------------------------------------------------------

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
        # 因为 __eq__ 被覆盖，需显式定义 __hash__ 才能保持可哈希性
        return hash((self.amount, self.unit))

    # ---------------------------------------------------------------------
    # 友好显示
    # ---------------------------------------------------------------------

    def __repr__(self) -> str:  # noqa: D401
        return f"Quantity(amount={self.amount}, unit={self.unit})"


###############################################################################
# 聚合根标识符（UUID）
###############################################################################

# WHY: 使用 NewType 生成静态类型安全的 ID，避免串用不同聚合 id。
RecipeId = NewType("RecipeId", uuid.UUID)
IngredientId = NewType("IngredientId", uuid.UUID)

# 提供便捷生成函数，业务层可以直接调用，而无需 import uuid 每次 new。

def new_recipe_id() -> RecipeId:  # noqa: D401
    """生成随机 ``RecipeId``。"""
    return RecipeId(uuid.uuid4())


def new_ingredient_id() -> IngredientId:  # noqa: D401
    """生成随机 ``IngredientId``。"""
    return IngredientId(uuid.uuid4())
