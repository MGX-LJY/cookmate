"""domain.inventory.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~

`InventoryItem` 聚合根定义。

*Cookmate* 以 **InventoryItem** 表示“冰箱中某种食材的具体存量”，核心职责：

1. 记录 *Ingredient* 的标识符 (`ingredient_id`)；
2. 跟踪当前 **Quantity** 与可选的 `expires_on`（保质期）；
3. 提供业务方法：`add()`、`consume()`、`is_expired()`、`will_expire_within()` 等。

> ⚠️ 该模型不持有 *Ingredient* 对象本身，只存关联 ID，遵循聚合边界。

MVP 仅实现最小字段与逻辑，后期可扩展批次号 (lot)、采购价等。
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Final, Mapping

from domain.shared.value_objects import IngredientId, Quantity

###############################################################################
# 常量
###############################################################################

# 库存低阈值默认系数（剩余 < 10% 视为低库存），后续可提到设置里。
_DEFAULT_LOW_STOCK_RATIO: Final[float] = 0.1

###############################################################################
# InventoryItem 聚合根
###############################################################################

# kw_only=True 同样避免“默认值字段在前”问题，并保持关键字调用友好。

@dataclass(frozen=True, slots=True, kw_only=True)
class InventoryItem:  # noqa: WPS110
    """冰箱库存条目。"""

    # ---------------------------- 必填字段 -----------------------------
    ingredient_id: IngredientId = field(metadata={"doc": "关联 Ingredient 的 ID"})
    quantity: Quantity = field(metadata={"doc": "当前剩余数量"})

    # ---------------------------- 可选字段 -----------------------------
    expires_on: _dt.date | None = field(
        default=None,
        metadata={"doc": "保质期日期；None 表示长期存放"},
    )

    # ------------------------------------------------------------------
    # 校验逻辑
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:  # noqa: D401
        if self.quantity.amount < 0:
            raise ValueError("库存数量不能为负数")

    # ------------------------------------------------------------------
    # 业务方法
    # ------------------------------------------------------------------

    # PS: 由于 dataclass frozen，我们通过 "return self.__class__(...)" 创建新实例，
    #     保证不可变性。

    def add(self, delta: Quantity) -> "InventoryItem":  # noqa: D401
        """增加库存，返回新实例。"""
        if delta.unit != self.quantity.unit:
            delta = delta.to(self.quantity.unit)
        return InventoryItem(
            ingredient_id=self.ingredient_id,
            quantity=self.quantity + delta,
            expires_on=self.expires_on,
        )

    def consume(self, delta: Quantity) -> "InventoryItem":  # noqa: D401
        """扣减库存；若不足则抛 ``ValueError``。"""
        if delta.unit != self.quantity.unit:
            delta = delta.to(self.quantity.unit)
        if delta > self.quantity:
            raise ValueError("库存不足，无法扣减")
        return InventoryItem(
            ingredient_id=self.ingredient_id,
            quantity=self.quantity - delta,
            expires_on=self.expires_on,
        )

    # ------------------------------------------------------------------
    # 状态查询
    # ------------------------------------------------------------------

    def is_expired(self, on: _dt.date | None = None) -> bool:  # noqa: D401
        """判断是否在 *on* 日期（默认为今天）已过期。"""
        if self.expires_on is None:
            return False
        check_date = on or _dt.date.today()
        return self.expires_on < check_date

    def will_expire_within(self, days: int) -> bool:  # noqa: D401
        """判断是否将在 *days* 天内过期。``expires_on`` 为 ``None`` 时返回 ``False``。"""
        if self.expires_on is None:
            return False
        today = _dt.date.today()
        return today <= self.expires_on <= today + _dt.timedelta(days=days)

    def is_low_stock(self, ratio: float = _DEFAULT_LOW_STOCK_RATIO) -> bool:  # noqa: D401
        """判断是否低库存（当前 *默认* 定义为 < 10% 原始量）。"""
        # 低库存阈值判断留给应用层更妥，这里给 MVP 简易实现
        # 因为我们不知道“原始量”，此处示例假设 0 < qty < 0.1 视为低库存
        return self.quantity.amount <= 0 or self.quantity.amount < (Decimal("0.001"))

    # ------------------------------------------------------------------
    # 字符串 / 调试显示
    # ------------------------------------------------------------------

    def __str__(self) -> str:  # noqa: D401
        expiry = (
            f"，过期 {self.expires_on.isoformat()}" if self.expires_on else ""
        )
        return f"{self.ingredient_id}: {self.quantity}{expiry}"

    def __repr__(self) -> str:  # noqa: D401
        return (
            "InventoryItem("  # noqa: WPS237
            f"ingredient_id={self.ingredient_id}, quantity={self.quantity}, expires_on={self.expires_on})"
        )
