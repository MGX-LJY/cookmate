"""adapters.repo_memory.ingredient_repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`AbstractIngredientRepo` 的 **内存实现**。

用途
----
* 单元测试与原型运行；
* 对照数据层契约，辅助快速迭代领域逻辑；
* 线程安全、零外部依赖。

实现细节
--------
* 使用 `OrderedDict[IngredientId, Ingredient]` 按插入顺序保存，便于测试预测；
* 采用 `threading.RLock` 支持并发读写（简单场景足够）；
* 查重逻辑基于 `Ingredient.name`，可在应用层避免重名。
"""
from __future__ import annotations

import threading
from collections import OrderedDict
from typing import Iterable

from domain.ingredient.models import Ingredient
from domain.ingredient.repository import AbstractIngredientRepo
from domain.shared.value_objects import IngredientId

###############################################################################
# In-Memory Ingredient Repository
###############################################################################

class MemoryIngredientRepo(AbstractIngredientRepo):  # noqa: WPS110
    """基于内存字典的 IngredientRepo。"""

    def __init__(self) -> None:  # noqa: D401
        self._storage: OrderedDict[IngredientId, Ingredient] = OrderedDict()
        self._lock = threading.RLock()

    # ----------------------------- 查询 -----------------------------
    def get(self, ingredient_id: IngredientId) -> Ingredient | None:  # noqa: D401
        with self._lock:
            return self._storage.get(ingredient_id)

    def list(self) -> Iterable[Ingredient]:  # noqa: D401
        with self._lock:
            return list(self._storage.values())

    def find_by_name(self, name: str) -> Ingredient | None:  # noqa: D401
        with self._lock:
            for ing in self._storage.values():
                if ing.name == name:
                    return ing
            return None

    # ----------------------------- 写入 -----------------------------
    def add(self, ingredient: Ingredient) -> None:  # noqa: D401
        with self._lock:
            if ingredient.id in self._storage:
                raise KeyError(f"Ingredient {ingredient.id} 已存在")
            self._storage[ingredient.id] = ingredient

    def update(self, ingredient: Ingredient) -> None:  # noqa: D401
        with self._lock:
            if ingredient.id not in self._storage:
                raise KeyError(f"Ingredient {ingredient.id} 不存在，无法更新")
            self._storage[ingredient.id] = ingredient

    def remove(self, ingredient_id: IngredientId) -> None:  # noqa: D401
        with self._lock:
            self._storage.pop(ingredient_id, None)  # 如果不存在，静默忽略
