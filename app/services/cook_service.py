"""app.services.cook_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

烹饪执行用例服务。

核心流程 (MVP)
--------------
1. **加载菜谱** —— 根据 `recipe_id` 获取 `Recipe`；
2. **校验库存** —— 判断当前库存是否足够；若不足返回缺料列表；
3. **扣减库存** —— 更新 `InventoryItem.quantity`；
4. **写入烹饪日志 / 发布事件** —— 生成 `RecipeCooked` 领域事件，通过注入的
   `EventBus` 发布；
5. **提交事务** —— 调用 `UnitOfWork.commit()` 确认写入。

设计说明
--------
* **EventBus**：简单接口 `publish(event)`，由调用端注入（默认空实现）。
* **事务边界**：整个 `cook()` 流程位于一个 UoW 上下文中。
* **可扩展**：未来可加入成本核算、营养计算等逻辑。
"""
from __future__ import annotations

from typing import Mapping

from app.unit_of_work import AbstractUnitOfWork
from domain.inventory.models import InventoryItem
from domain.inventory.repository import AbstractInventoryRepo
from domain.recipe.models import Recipe
from domain.recipe.repository import AbstractRecipeRepo
from domain.shared.events import RecipeCooked
from domain.shared.value_objects import IngredientId, Quantity, RecipeId
from infra.event_bus import EventBus, NullEventBus

###############################################################################
# 辅助接口
###############################################################################


###############################################################################
# 自定义异常
###############################################################################

class InsufficientInventoryError(RuntimeError):  # noqa: WPS110
    """库存不足异常，附带缺料映射。"""

    def __init__(self, missing: Mapping[IngredientId, Quantity]):  # noqa: D401
        super().__init__("库存不足")
        self.missing = missing

###############################################################################
# CookService
###############################################################################

class CookService:  # noqa: WPS110
    """执行烹饪流程的应用服务。"""

    def __init__(
        self,
        uow: AbstractUnitOfWork,
        event_bus: EventBus | None = None,
    ) -> None:  # noqa: D401
        self.uow = uow
        self.events = event_bus or NullEventBus()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def cook(self, recipe_id: RecipeId, servings: int = 1) -> None:  # noqa: D401
        """执行烹饪。

        Parameters
        ----------
        recipe_id: RecipeId
            要烹饪的菜谱 ID。
        servings: int, default=1
            份数（倍率）。不支持小数；如需半份请先 `Recipe.scale()`。
        """
        if servings <= 0:
            raise ValueError("servings 必须大于 0")

        with self.uow as uow:
            recipe = self._get_recipe(uow.recipes, recipe_id)
            consumed_map = self._calculate_consumption(recipe, servings)
            missing = self._check_inventory(uow.inventories, consumed_map)
            if missing:
                raise InsufficientInventoryError(missing)

            # 扣减库存
            for ing_id, qty_needed in consumed_map.items():
                item = uow.inventories.get(ing_id)
                assert item is not None  # 已验证存在
                uow.inventories.add_or_update(item.consume(qty_needed))

            # 发布领域事件
            event = RecipeCooked(
                recipe_id=recipe.id,
                servings=servings,
                consumed_ingredients=consumed_map,
            )
            self.events.publish(event)
            # commit 在 UoW __exit__ 内完成

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------

    @staticmethod
    def _get_recipe(repo: AbstractRecipeRepo, recipe_id: RecipeId) -> Recipe:  # noqa: D401
        recipe = repo.get(recipe_id)
        if not recipe:
            raise ValueError(f"Recipe {recipe_id} 不存在")
        return recipe

    @staticmethod
    def _calculate_consumption(
        recipe: Recipe,
        servings: int,
    ) -> dict[IngredientId, Quantity]:  # noqa: D401
        return {
            ing_id: qty * servings for ing_id, qty in recipe.ingredients.items()
        }

    @staticmethod
    def _check_inventory(
        repo: AbstractInventoryRepo,
        required: Mapping[IngredientId, Quantity],
    ) -> dict[IngredientId, Quantity]:  # noqa: D401
        """返回缺料映射（IngredientId -> 缺少量）；若充足返回空 dict。"""
        missing: dict[IngredientId, Quantity] = {}
        for ing_id, qty_req in required.items():
            item = repo.get(ing_id)
            if item is None or item.quantity < qty_req:
                cur_qty = item.quantity if item else Quantity.of(0, qty_req.unit)
                missing[ing_id] = qty_req - cur_qty  # type: ignore[arg-type]
        return missing
