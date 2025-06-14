"""domain.ingredient.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Ingredient` 聚合根定义。

在 *Cookmate* 中，一个 **Ingredient**（食材）代表冰箱/菜谱中可用的基础原料。
它是库存 (`InventoryItem`) 与菜谱 (`Recipe`) 的共同依赖对象，因此需要相对
稳定且精准的字段设计。

核心设计原则：

1. **不可变标识** —— 使用 `IngredientId (UUID)` 作为唯一主键；
2. **最小必要信息** —— MVP 阶段保留 `name / default_unit / metadata`，避免过度
   建模，后期可扩充营养信息等；
3. **统一计量单位** —— `default_unit` 标识此食材在库存统计时的主度量单位；
4. **无外部依赖** —— 纯 Python / dataclass，领域层不依赖 ORM / API。

> ⚠️ 注意：Ingredient 本身不持有当前库存数量，库存信息位于
> `domain.inventory.models.InventoryItem`。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from domain.shared.value_objects import IngredientId, Unit, new_ingredient_id

###############################################################################
# 类型别名
###############################################################################

# MVP 仅保存少量元数据；后期可扩展为 NutritionFacts、BarCode 等结构体。
MetaData = Mapping[str, str]

###############################################################################
# Ingredient 聚合根
###############################################################################

# kw_only=True 避免 “Fields with a default value must come after any fields without a default”
# 问题，同时保持调用端灵活（关键字参数即可）。

@dataclass(frozen=True, slots=True, kw_only=True)
class Ingredient:  # noqa: WPS110
    """食材聚合根。"""

    # 无默认值字段（必须先写）
    name: str = field(metadata={"doc": "食材名称"})
    default_unit: Unit = field(metadata={"doc": "默认计量单位"})

    # 有默认值字段（后写或 kw_only）
    id: IngredientId = field(
        default_factory=new_ingredient_id,
        metadata={"doc": "UUID 主键"},
    )
    metadata: MetaData | None = field(
        default=None,
        metadata={"doc": "附加元数据，可为条形码/供应商等"},
    )

    # ------------------------------------------------------------------
    # 验证逻辑
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:  # noqa: D401
        if not self.name or not self.name.strip():
            raise ValueError("Ingredient.name 不能为空")

    # ------------------------------------------------------------------
    # 业务辅助方法
    # ------------------------------------------------------------------

    def with_metadata(self, **kwargs: str) -> "Ingredient":  # noqa: D401
        """返回带更新后 metadata 的新实例（保持不可变性）。"""
        merged: dict[str, str] = {**(self.metadata or {}), **kwargs}
        return Ingredient(
            name=self.name,
            default_unit=self.default_unit,
            id=self.id,
            metadata=merged,
        )

    # ------------------------------------------------------------------
    # 字符串表示
    # ------------------------------------------------------------------

    def __str__(self) -> str:  # noqa: D401
        return f"{self.name}({self.default_unit.value})"

    def __repr__(self) -> str:  # noqa: D401
        return (
            "Ingredient("  # noqa: WPS237
            f"id={self.id}, name='{self.name}', unit={self.default_unit}, metadata={self.metadata})"
        )
