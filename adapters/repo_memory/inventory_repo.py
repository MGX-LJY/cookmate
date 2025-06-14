"""adapters.repo_memory.inventory_repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`AbstractInventoryRepo` 的 **内存实现**。

特点
-----
* 内部存储：`dict[IngredientId, InventoryItem]`，键唯一。
* 并发安全：`threading.RLock` 简易读写锁，足够单机 CLI/API 场景。
* 逻辑函数：实现 ``low_stock`` & ``expiring_soon`` 条件过滤，直接依赖
  `InventoryItem` 的业务方法。

> ⚠️ 与数据库实现行为保持一致（尤其方法名 / 异常）。单元测试可在 Memory 与
> SQLite 实现之间无缝切换。
"""
from __future__ import annotations

import threading
from collections import OrderedDict
from datetime import date as _date
from typing import Iterable

from domain.inventory.models import InventoryItem
from domain.inventory.repository import AbstractInventoryRepo
from domain.shared.value_objects import IngredientId

###############################################################################
# In-memory Inventory Repository
###############################################################################

class MemoryInventoryRepo(AbstractInventoryRepo):  # noqa: WPS110
    """基于内存字典的库存仓库实现。"""

    def __init__(self) -> None:  # noqa: D401
        # OrderedDict 方便测试输出顺序一致；键 = IngredientId
        self._storage: OrderedDict[IngredientId, InventoryItem] = OrderedDict()
        self._lock = threading.RLock()

    # ----------------------------- 查询 -----------------------------
    def get(self, ingredient_id: IngredientId) -> InventoryItem | None:  # noqa: D401
        with self._lock:
            return self._storage.get(ingredient_id)

    def list(self) -> Iterable[InventoryItem]:  # noqa: D401
        with self._lock:
            return list(self._storage.values())

    def low_stock(self) -> Iterable[InventoryItem]:  # noqa: D401
        with self._lock:
            return [item for item in self._storage.values() if item.is_low_stock()]

    def expiring_soon(self, days: int = 3) -> Iterable[InventoryItem]:  # noqa: D401
        with self._lock:
            today = _date.today()
            return [
                item
                for item in self._storage.values()
                if item.will_expire_within(days) and not item.is_expired(today)
            ]

    # ----------------------------- 写入 -----------------------------
    def add_or_update(self, item: InventoryItem) -> None:  # noqa: D401
        with self._lock:
            self._storage[item.ingredient_id] = item

    def remove(self, ingredient_id: IngredientId) -> None:  # noqa: D401
        with self._lock:
            self._storage.pop(ingredient_id, None)  # 不存在时静默忽略
