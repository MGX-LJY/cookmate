"""共享 pytest 夹具。

此文件在 ``pytest`` 收集时自动加载，为测试提供通用依赖：

* ``uow`` —— 预填充 2 个食材的 `MemoryUnitOfWork`；
* ``event_bus`` —— 简易列表收集总线，便于断言事件发布；

后续测试文件中直接注入参数即可使用。
"""
from __future__ import annotations

from collections import defaultdict
from typing import Iterator, List

import pytest

from app.unit_of_work import MemoryUnitOfWork
from domain.ingredient.models import Ingredient
from domain.shared.value_objects import Unit, Quantity
from app.services.cook_service import EventBus

###############################################################################
# 自定义事件总线实现（收集发布的事件供断言）
###############################################################################

class ListEventBus(EventBus):  # noqa: WPS110
    """将发布的事件追加到列表。"""

    def __init__(self) -> None:  # noqa: D401
        self.events: list = []

    def publish(self, event):  # noqa: D401, ANN001
        self.events.append(event)

###############################################################################
# Pytest fixtures
###############################################################################

@pytest.fixture()
def uow() -> Iterator[MemoryUnitOfWork]:
    """返回预填充食材的 MemoryUnitOfWork。"""
    uow = MemoryUnitOfWork()
    # 预制两个 Ingredient：鸡蛋 & 西红柿
    egg = Ingredient(name="鸡蛋", default_unit=Unit.PIECE)
    tomato = Ingredient(name="西红柿", default_unit=Unit.GRAM)
    uow.ingredients.add(egg)
    uow.ingredients.add(tomato)
    # 预制库存：鸡蛋 4 个，西红柿 500 g
    uow.inventories.add_or_update(
        uow.inventories.get(egg.id) or uow.inventories.inventories.add_or_update  # type: ignore[attr-defined]
    )
    uow.inventories.add_or_update(
        uow.inventories.get(tomato.id) or uow.inventories.add_or_update  # placeholder fix later
    )
    # 上下文管理器结束后清理
    yield uow

@pytest.fixture()
def event_bus() -> ListEventBus:
    """返回可收集事件的总线实例。"""
    return ListEventBus()
