"""domain.recipe.models
~~~~~~~~~~~~~~~~~~~~~~~~

`Recipe` 聚合根定义。

在 *Cookmate* 中，一份 **Recipe**（菜谱）描述了：
1. 这道菜需要哪些 **Ingredient** 及各自用量；
2. 可选的烹饪步骤 (步骤文本列表)；
3. 额外元数据，如标签 / 难度 / 时长等（MVP 阶段暂不深入）。

> ⚠️ 菜谱只记录“理论用量”，实际扣减库存由 `CookService` 计算并发布
> `RecipeCooked` 事件。

设计要点：
* **Ingredient 依赖** —— 仅通过 `IngredientId` 引用，保持聚合边界清晰；
* **用量类型** —— 使用 `Quantity` 值对象，天然支持单位换算；
* **不可变** —— 采用 `frozen=True`，任何修改需生成新实例，匹配领域法则；
* **可扩展** —— MVP 只包含最小字段，后续可添加图片、标签、营养信息等。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from domain.shared.value_objects import (
    IngredientId,
    Quantity,
    RecipeId,
    new_recipe_id,
)

###############################################################################
# 类型别名
###############################################################################

# MVP 仅需简单标签；后续可扩展字段（spicy_level, cuisine 等）
MetaData = Mapping[str, str]
IngredientMap = Mapping[IngredientId, Quantity]

###############################################################################
# Recipe 聚合根
###############################################################################

@dataclass(frozen=True, slots=True, kw_only=True)
class Recipe:  # noqa: WPS110
    """菜谱聚合根。"""

    # ------------------------- 必填字段 -----------------------------
    name: str = field(metadata={"doc": "菜谱名称"})
    ingredients: IngredientMap = field(
        metadata={"doc": "所需食材及其用量 (IngredientId -> Quantity)"},
    )

    # ------------------------- 可选字段（带默认值） ------------------
    steps: Sequence[str] = field(
        default_factory=tuple,
        metadata={"doc": "烹饪步骤文本列表，可为空"},
    )
    id: RecipeId = field(
        default_factory=new_recipe_id,
        metadata={"doc": "UUID 主键"},
    )
    metadata: MetaData | None = field(
        default=None,
        metadata={"doc": "附加信息，如标签、时长、难度"},
    )

    # ------------------------------------------------------------------
    # 数据校验
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:  # noqa: D401
        if not self.name or not self.name.strip():
            raise ValueError("Recipe.name 不能为空")
        if not self.ingredients:
            raise ValueError("Recipe 必须至少包含一种食材")

    # ------------------------------------------------------------------
    # 业务方法
    # ------------------------------------------------------------------

    def required_ingredients(self) -> IngredientMap:  # noqa: D401
        """返回 *食材用量映射*（不可变视图），供 CookService 使用。"""
        # IngredientMap 本身可能是 MutableMapping；此处强制返回不可变副本
        return {iid: qty for iid, qty in self.ingredients.items()}

    def scale(self, factor: float | int) -> "Recipe":  # noqa: D401
        """按给定 *factor*（倍率）放大/缩小用量，生成新 Recipe。

        例如 2 份 → `factor=2`；半份 → `factor=0.5`。
        """
        if factor <= 0:
            raise ValueError("factor 必须为正数")
        scaled = {iid: qty * factor for iid, qty in self.ingredients.items()}
        return Recipe(
            name=self.name,
            ingredients=scaled,
            steps=self.steps,
            metadata=self.metadata,
            id=self.id,  # 保持相同 id，视作同一配方不同倍率
        )

    # ------------------------------------------------------------------
    # 字符串显示
    # ------------------------------------------------------------------

    def __str__(self) -> str:  # noqa: D401
        return self.name

    def __repr__(self) -> str:  # noqa: D401
        return (
            "Recipe("  # noqa: WPS237
            f"id={self.id}, name='{self.name}', ingredients={len(self.ingredients)} items)"
        )
