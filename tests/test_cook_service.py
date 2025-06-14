"""CookService 集成测试 (Memory UoW).

覆盖场景：
1. cook 正常扣减库存并发布事件；
2. 库存不足时抛 InsufficientInventoryError；
3. 不存在的菜谱抛 ValueError；
4. servings 参数非法抛 ValueError。

"""
from __future__ import annotations

import pytest

from app.services.cook_service import CookService, InsufficientInventoryError
from app.services.recipe_service import RecipeService
from domain.shared.value_objects import Quantity, Unit, new_recipe_id
from domain.recipe.models import Recipe

DEFAULT_STEPS = ["打蛋", "热锅", "翻炒"]


def _create_recipe(service: RecipeService):
    return service.create_recipe(
        name="番茄炒蛋",
        ingredient_inputs={"鸡蛋": (2, ""), "西红柿": (300, "g")},
        steps=DEFAULT_STEPS,
    )


def test_cook_success(uow, event_bus):
    recipe_id = _create_recipe(RecipeService(uow))
    svc = CookService(uow, event_bus)
    svc.cook(recipe_id)

    egg_ing = uow.ingredients.find_by_name("鸡蛋")
    tomato_ing = uow.ingredients.find_by_name("西红柿")
    egg_item = uow.inventories.get(egg_ing.id)
    tomato_item = uow.inventories.get(tomato_ing.id)
    assert egg_item.quantity == Quantity.of(2, Unit.PIECE)
    assert tomato_item.quantity == Quantity.of(200, Unit.GRAM)
    assert uow._committed is True
    assert len(event_bus.events) == 1
    event = event_bus.events[0]
    assert event.recipe_id == recipe_id
    assert event.servings == 1


def test_cook_insufficient_inventory(uow, event_bus):
    recipe_id = _create_recipe(RecipeService(uow))
    egg = uow.ingredients.find_by_name("鸡蛋")
    tomato = uow.ingredients.find_by_name("西红柿")
    svc = CookService(uow, event_bus)
    with pytest.raises(InsufficientInventoryError) as exc:
        svc.cook(recipe_id, servings=3)
    # 未提交事务，事件为空
    assert uow._committed is False
    assert len(event_bus.events) == 0
    missing = exc.value.missing
    assert missing[egg.id] == Quantity.of(2, Unit.PIECE)
    assert missing[tomato.id] == Quantity.of(400, Unit.GRAM)


def test_cook_recipe_not_found(uow, event_bus):
    svc = CookService(uow, event_bus)
    with pytest.raises(ValueError):
        svc.cook(new_recipe_id())


def test_cook_invalid_servings(uow, event_bus):
    recipe_id = _create_recipe(RecipeService(uow))
    svc = CookService(uow, event_bus)
    with pytest.raises(ValueError):
        svc.cook(recipe_id, servings=0)