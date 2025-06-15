"""app.services.recipe_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

菜谱用例服务 (Application Service)。

为什么需要 Application Service?
---------------------------------
* **封装业务用例**：组织多个聚合根操作，控制事务边界；
* **保持领域纯净**：领域模型不直接依赖框架/存储，所有 I/O 通过 Service 注入的
  UnitOfWork 执行；
* **便于测试**：服务层对外暴露简洁方法签名，使用 MemoryUoW 可单元测试。

该文件实现 ``RecipeService``：
* `create_recipe()` —— 新增菜谱
* `update_recipe()` —— 编辑菜谱（按 ID 覆盖）
* `list_recipes()` —— 拉取所有菜谱

> ⚠️ 输入/输出以 **简单类型**（`dict` / `list` / 原生值对象）为主，便于 CLI、
> FastAPI 等上层调用；复杂验证交由领域模型内部完成。
"""
from __future__ import annotations

from typing import Mapping

from app.unit_of_work import AbstractUnitOfWork
from domain.recipe.models import Recipe
from domain.shared.value_objects import Quantity, RecipeId

###############################################################################
# DTO 类型别名
###############################################################################

IngredientInput = Mapping[str, tuple[float | int | str, str]]  # name -> (amount, unit)

###############################################################################
# 自定义异常
###############################################################################

class RecipeAlreadyExistsError(RuntimeError):  # noqa: WPS110
    """尝试创建已存在菜谱时抛出。"""


class RecipeNotFoundError(RuntimeError):  # noqa: WPS110
    """菜谱不存在。"""

###############################################################################
# RecipeService
###############################################################################

class RecipeService:  # noqa: WPS110
    """菜谱相关用例服务。"""

    def __init__(self, uow: AbstractUnitOfWork) -> None:  # noqa: D401
        self.uow = uow

    # ------------------------------------------------------------------
    # Public APIs
    # ------------------------------------------------------------------

    def create_recipe(
        self,
        name: str,
        ingredient_inputs: IngredientInput,
        steps: list[str] | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> RecipeId:  # noqa: D401
        """创建新菜谱。

        Parameters
        ----------
        name: str
            菜谱名称。
        ingredient_inputs: Mapping[str, (amount, unit)]
            键为 **Ingredient.name**，值为 (数量, 单位字符串)。Service 会在仓库中
            查找对应 IngredientId 并转换为 Quantity。
        steps: list[str] | None
            烹饪步骤；可为空。
        metadata: Mapping[str, str] | None
            额外信息（标签、时长等）。
        """
        with self.uow as uow:
            # 检查重名
            if uow.recipes.find_by_name(name):
                raise RecipeAlreadyExistsError(name)

            # 将食材名称映射到 IngredientId
            ingredients_map = {}
            for ing_name, (amount, unit_str) in ingredient_inputs.items():
                ing = uow.ingredients.find_by_name(ing_name)
                if not ing:
                    raise ValueError(f"食材 '{ing_name}' 不存在，请先录入食材")
                qty = Quantity.of(amount, unit=ing.default_unit if unit_str == "" else unit_str)  # type: ignore[arg-type]
                ingredients_map[ing.id] = qty

            recipe = Recipe(
                name=name,
                ingredients=ingredients_map,
                steps=steps or [],
                metadata=metadata,
            )
            uow.recipes.add(recipe)
            # commit 在 UoW __exit__ 中调用
            return recipe.id

    def update_recipe(self, recipe: Recipe) -> None:  # noqa: D401
        """覆盖更新菜谱。调用方自行构造新 Recipe 实例。"""
        with self.uow as uow:
            if not uow.recipes.get(recipe.id):
                raise RecipeNotFoundError(recipe.id)
            uow.recipes.update(recipe)

    def list_recipes(self) -> list[Recipe]:  # noqa: D401
        """列出所有菜谱。"""
        with self.uow as uow:
            return list(uow.recipes.list())

    def remove_recipe(self, name: str) -> None:  # noqa: D401
        """按菜名删除菜谱。"""
        with self.uow as uow:
            recipe = uow.recipes.find_by_name(name)
            if not recipe:
                raise RecipeNotFoundError(name)
            uow.recipes.remove(recipe.id)

    # ------------------------------------------------------------------
    # 新增：按菜名获取菜谱及单字段更新
    # ------------------------------------------------------------------

    def get_by_name(self, name: str) -> Recipe:
        """获取指定菜谱。"""
        with self.uow as uow:
            recipe = uow.recipes.find_by_name(name)
            if not recipe:
                raise RecipeNotFoundError(name)
            return recipe

    def update_metadata_field(self, name: str, key: str, value: str) -> None:
        """更新 metadata 中的单个字段。"""
        with self.uow as uow:
            recipe = uow.recipes.find_by_name(name)
            if not recipe:
                raise RecipeNotFoundError(name)
            meta = dict(recipe.metadata or {})
            meta[key] = str(value)
            updated = Recipe(
                name=recipe.name,
                ingredients=recipe.ingredients,
                steps=recipe.steps,
                metadata=meta,
                id=recipe.id,
            )
            uow.recipes.update(updated)

    def update_ingredients(self, name: str, ingredient_inputs: IngredientInput) -> None:
        """替换菜谱食材列表。"""
        with self.uow as uow:
            recipe = uow.recipes.find_by_name(name)
            if not recipe:
                raise RecipeNotFoundError(name)

            ingredients_map = {}
            for ing_name, (amount, unit_str) in ingredient_inputs.items():
                ing = uow.ingredients.find_by_name(ing_name)
                if not ing:
                    raise ValueError(f"食材 '{ing_name}' 不存在，请先录入食材")
                qty = Quantity.of(amount, unit=ing.default_unit if unit_str == "" else unit_str)  # type: ignore[arg-type]
                ingredients_map[ing.id] = qty

            updated = Recipe(
                name=recipe.name,
                ingredients=ingredients_map,
                steps=recipe.steps,
                metadata=recipe.metadata,
                id=recipe.id,
            )
            uow.recipes.update(updated)
