"""共享 pytest 夹具 (tests/conftest.py).

此文件在 pytest 收集时自动加载，为所有测试提供公共依赖：

* **uow** —— 预填充两种食材（鸡蛋、西红柿）及对应库存的 `MemoryUnitOfWork`。
* **event_bus** —— 收集领域事件，便于断言。
"""
from __future__ import annotations

import pytest

from app.unit_of_work import MemoryUnitOfWork
from domain.inventory.models import InventoryItem
from domain.ingredient.models import Ingredient
from domain.shared.value_objects import Quantity, Unit
from app.services.cook_service import EventBus

###############################################################################
# 简易事件总线 (收集事件用)
###############################################################################

class ListEventBus(EventBus):  # noqa: WPS110
    """把 publish 的事件存到 ``self.events``。"""

    def __init__(self) -> None:  # noqa: D401
        self.events: list = []

    def publish(self, event):  # noqa: D401, ANN001
        self.events.append(event)

###############################################################################
# Fixtures
###############################################################################

@pytest.fixture()
def uow() -> MemoryUnitOfWork:
    """返回预填充库存的内存 UnitOfWork。"""
    uow = MemoryUnitOfWork()

    # 创建食材
    egg = Ingredient(name="鸡蛋", default_unit=Unit.PIECE)
    tomato = Ingredient(name="西红柿", default_unit=Unit.GRAM)
    uow.ingredients.add(egg)
    uow.ingredients.add(tomato)

    # 写入库存
    uow.inventories.add_or_update(
        InventoryItem(ingredient_id=egg.id, quantity=Quantity.of(4, Unit.PIECE))
    )
    uow.inventories.add_or_update(
        InventoryItem(ingredient_id=tomato.id, quantity=Quantity.of(500, Unit.GRAM))
    )

    return uow


@pytest.fixture()
def event_bus() -> ListEventBus:
    """返回收集事件的总线。"""
    return ListEventBus()
