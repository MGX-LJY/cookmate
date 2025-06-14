"""PlannerService 集成测试 (Memory UoW).

覆盖场景：
1. list_cookable_recipes 仅返回库存充足的菜谱；
2. list_cookable_recipes servings 非法抛 ValueError；
3. generate_shopping_list 汇总全部菜谱缺料；
4. generate_shopping_list 支持自定义份数并忽略非正份数。
"""
from __future__ import annotations

import pytest

from app.services.recipe_service import RecipeService
from app.services.planner_service import PlannerService
from domain.shared.value_objects import Quantity, Unit

DEFAULT_STEPS = ["打蛋", "热锅", "翻炒"]

###############################################################################
# helpers
###############################################################################

def _create_recipe(service: RecipeService, eggs: int, tomato_g: int = 0):
    ingredients = {"鸡蛋": (eggs, "")}
    if tomato_g:
        ingredients["西红柿"] = (tomato_g, "g")
    return service.create_recipe(
        name=f"菜谱{eggs}-{tomato_g}",
        ingredient_inputs=ingredients,
        steps=DEFAULT_STEPS,
    )

###############################################################################
# 用例
###############################################################################

def test_list_cookable_recipes(uow):
    svc_recipe = RecipeService(uow)
    rid_ok = _create_recipe(svc_recipe, eggs=2, tomato_g=300)
    _create_recipe(svc_recipe, eggs=5)
    svc = PlannerService(uow)
    cookable_ids = {r.id for r in svc.list_cookable_recipes()}
    assert rid_ok in cookable_ids
    assert len(cookable_ids) == 1


def test_list_cookable_recipes_invalid_servings(uow):
    svc = PlannerService(uow)
    with pytest.raises(ValueError):
        svc.list_cookable_recipes(0)


def test_generate_shopping_list_all(uow):
    svc_recipe = RecipeService(uow)
    _create_recipe(svc_recipe, eggs=2, tomato_g=300)
    _create_recipe(svc_recipe, eggs=5)
    svc = PlannerService(uow)
    shopping = svc.generate_shopping_list()
    egg = uow.ingredients.find_by_name("鸡蛋")
    tomato = uow.ingredients.find_by_name("西红柿")
    assert shopping == {egg.id: Quantity.of(3, Unit.PIECE)}
    assert tomato.id not in shopping


def test_generate_shopping_list_custom(uow):
    svc_recipe = RecipeService(uow)
    rid = _create_recipe(svc_recipe, eggs=2, tomato_g=300)
    rid_bad = _create_recipe(svc_recipe, eggs=5)
    svc = PlannerService(uow)
    shopping = svc.generate_shopping_list({rid: 2, rid_bad: 0})
    egg = uow.ingredients.find_by_name("鸡蛋")
    tomato = uow.ingredients.find_by_name("西红柿")
    assert egg.id not in shopping
    assert shopping[tomato.id] == Quantity.of(100, Unit.GRAM)
