"""app.services.planner_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

智能筛选 / 购物清单用例服务（MVP 版本）。

目标
----
1. **list_cookable_recipes()**
   根据当前库存判断“马上就能做”的菜谱集合；
2. **generate_shopping_list()**
   给定一组目标菜谱（份数可选），汇总缺料→输出购物清单 (IngredientId -> Quantity)。

设计说明
--------
* **过滤维度**：MVP 仅实现“食材库存充足”这一条件；难度 / 时长等后续添加。
* **事务边界**：查询类逻辑读取仓库即可，不需要事务；购物清单生成读操作也可
  放在一个只读 UoW 上下文中。
"""
from __future__ import annotations

from collections import defaultdict
from typing import Mapping

from app.unit_of_work import AbstractUnitOfWork
from domain.recipe.models import Recipe
from domain.shared.value_objects import IngredientId, Quantity, RecipeId

###############################################################################
# PlannerService
###############################################################################

class PlannerService:  # noqa: WPS110
    """智能筛选与购物清单服务。"""

    def __init__(self, uow: AbstractUnitOfWork) -> None:  # noqa: D401
        self.uow = uow

    # ------------------------------------------------------------------
    # API 1: 可做菜谱筛选
    # ------------------------------------------------------------------

    def list_cookable_recipes(self, servings: int = 1) -> list[Recipe]:  # noqa: D401
        """返回当前库存可立即烹饪的菜谱列表。"""
        if servings <= 0:
            raise ValueError("servings 必须大于 0")
        with self.uow as uow:
            inventories = {item.ingredient_id: item.quantity for item in uow.inventories.list()}
            cookable: list[Recipe] = []
            for recipe in uow.recipes.list():
                if self._is_recipe_cookable(recipe, inventories, servings):
                    cookable.append(recipe)
            return cookable

    # ------------------------------------------------------------------
    # API 2: 购物清单生成
    # ------------------------------------------------------------------

    def generate_shopping_list(
        self,
        desired: Mapping[RecipeId, int] | None = None,
    ) -> dict[IngredientId, Quantity]:  # noqa: D401
        """根据 *desired* 菜谱份数计划生成购物清单。

        Parameters
        ----------
        desired: Mapping[RecipeId, int] | None
            目标菜谱 -> 份数；若为 ``None`` 表示使用全部菜谱各 1 份做计划。
        """
        with self.uow as uow:
            # 当前库存快照
            inventories = {item.ingredient_id: item.quantity for item in uow.inventories.list()}

            # 汇总需求
            total_need: dict[IngredientId, Quantity] = defaultdict(lambda: None)  # type: ignore[arg-type]
            for recipe in uow.recipes.list():
                servings = (desired or {}).get(recipe.id, 1)
                if servings <= 0:
                    continue
                for ing_id, qty in recipe.ingredients.items():
                    need = qty * servings
                    if prev := total_need.get(ing_id):
                        total_need[ing_id] = prev + need
                    else:
                        total_need[ing_id] = need

            # 计算缺口
            shopping: dict[IngredientId, Quantity] = {}
            for ing_id, qty_need in total_need.items():
                have = inventories.get(ing_id)
                if not have or have < qty_need:
                    missing = qty_need - have if have else qty_need
                    shopping[ing_id] = missing
            return shopping

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------

    @staticmethod
    def _is_recipe_cookable(
        recipe: Recipe,
        inventory: dict[IngredientId, Quantity],
        servings: int,
    ) -> bool:  # noqa: D401
        for ing_id, qty in recipe.ingredients.items():
            need = qty * servings
            have = inventory.get(ing_id)
            if have is None or have < need:
                return False
        return True
