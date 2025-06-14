"""CookService 单元测试 (MVP).

覆盖场景：
1. cook 成功扣减库存并发布事件；
2. servings 非法值触发 ValueError；
3. 菜谱不存在触发 ValueError；
4. 库存不足抛 InsufficientInventoryError 并回滚。
"""
from __future__ import annotations

import pytest

from app.services.recipe_service import RecipeService
from app.services.cook_service import CookService, InsufficientInventoryError
from domain.shared.value_objects import Quantity, Unit, new_recipe_id

DEFAULT_STEPS = ["打蛋", "热锅", "翻炒"]


def _create_recipe(service: RecipeService):
    return service.create_recipe(
        name="番茄炒蛋",
        ingredient_inputs={"鸡蛋": (2, ""), "西红柿": (300, "g")},
        steps=DEFAULT_STEPS,
    )


def test_cook_success(uow, event_bus):
    rid = _create_recipe(RecipeService(uow))
    svc = CookService(uow, event_bus)
    svc.cook(rid)

    egg = uow.ingredients.find_by_name("鸡蛋")
    tomato = uow.ingredients.find_by_name("西红柿")
    assert egg and tomato
    egg_item = uow.inventories.get(egg.id)
    tomato_item = uow.inventories.get(tomato.id)
    assert egg_item.quantity == Quantity.of(2, Unit.PIECE)
    assert tomato_item.quantity == Quantity.of(200, Unit.GRAM)

    assert uow._committed
    assert len(event_bus.events) == 1
    event = event_bus.events[0]
    assert event.recipe_id == rid
    assert event.servings == 1
    assert event.consumed_ingredients[egg.id] == Quantity.of(2, Unit.PIECE)


def test_cook_invalid_servings(uow):
    rid = _create_recipe(RecipeService(uow))
    svc = CookService(uow)
    with pytest.raises(ValueError):
        svc.cook(rid, servings=0)


def test_cook_recipe_not_found(uow):
    svc = CookService(uow)
    with pytest.raises(ValueError):
        svc.cook(new_recipe_id())
    assert not uow._committed


def test_cook_insufficient_inventory(uow, event_bus):
    svc_recipe = RecipeService(uow)
    rid = svc_recipe.create_recipe(
        name="鸡蛋大餐",
        ingredient_inputs={"鸡蛋": (5, "")},
        steps=[],
    )
    egg = uow.ingredients.find_by_name("鸡蛋")
    svc = CookService(uow, event_bus)
    with pytest.raises(InsufficientInventoryError) as exc:
        svc.cook(rid)
    missing = exc.value.missing
    assert egg.id in missing
    assert missing[egg.id] == Quantity.of(1, Unit.PIECE)
    assert event_bus.events == []
    assert not uow._committed
