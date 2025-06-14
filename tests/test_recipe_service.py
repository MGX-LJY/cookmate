"""RecipeService 单元测试 (MVP).

覆盖场景：
1. create_recipe 成功创建；
2. 重名菜谱触发 RecipeAlreadyExistsError；
3. list_recipes 返回已创建菜谱；
4. update_recipe 正常更新；
5. 更新不存在菜谱抛 RecipeNotFoundError。
"""
from __future__ import annotations

import pytest

from app.services.recipe_service import (
    RecipeAlreadyExistsError,
    RecipeNotFoundError,
    RecipeService,
)
from domain.shared.value_objects import Quantity, Unit, new_recipe_id
from domain.recipe.models import Recipe

DEFAULT_STEPS = ["打蛋", "热锅", "翻炒"]

###############################################################################
# helpers
###############################################################################

def _create(service: RecipeService):
    return service.create_recipe(
        name="番茄炒蛋",
        ingredient_inputs={"鸡蛋": (2, ""), "西红柿": (300, "g")},
        steps=DEFAULT_STEPS,
    )

###############################################################################
# 用例
###############################################################################

def test_create_recipe_success(uow):
    rid = _create(RecipeService(uow))
    assert rid is not None
    assert len(uow.recipes.list()) == 1


def test_create_recipe_duplicate(uow):
    svc = RecipeService(uow)
    _create(svc)
    with pytest.raises(RecipeAlreadyExistsError):
        _create(svc)


def test_list_recipes(uow):
    svc = RecipeService(uow)
    _create(svc)
    names = [r.name for r in svc.list_recipes()]
    assert names == ["番茄炒蛋"]


def test_update_recipe_success(uow):
    svc = RecipeService(uow)
    rid = _create(svc)
    original = uow.recipes.get(rid)
    assert original is not None

    # 放大两倍用量后更新
    doubled = {
        iid: Quantity.of(qty.amount * 2, qty.unit) for iid, qty in original.ingredients.items()
    }
    updated = Recipe(
        name=original.name,
        ingredients=doubled,
        steps=original.steps,
        metadata=original.metadata,
        id=original.id,
    )
    svc.update_recipe(updated)
    refreshed = uow.recipes.get(rid)
    first_qty = list(refreshed.ingredients.values())[0]
    assert first_qty == Quantity.of(4, Unit.PIECE)


def test_update_recipe_not_found(uow):
    svc = RecipeService(uow)
    any_ing = list(uow.ingredients.list())[0]
    fake_recipe = Recipe(
        name="不存在的菜",
        ingredients={any_ing.id: Quantity.of(1, Unit.PIECE)},
        id=new_recipe_id(),
    )
    with pytest.raises(RecipeNotFoundError):
        svc.update_recipe(fake_recipe)
