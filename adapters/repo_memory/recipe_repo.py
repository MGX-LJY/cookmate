"""adapters.repo_memory.recipe_repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`AbstractRecipeRepo` 的 **内存实现**。

用途：
* **单元测试** —— 无需真实数据库即可跑完整业务逻辑；
* **原型 / 演示** —— 轻量级运行 CLI / API；
* **基准接口契约** —— 为后续 SQLite / PostgreSQL 实现提供对照。

实现特点：
* 采用 `dict[RecipeId, Recipe]` 存储；
* 使用 `threading.RLock` 保证并发安全（简单读写锁）；
* 抛出自定义 `KeyError` 以保持与字典语义一致；
* 除增删改查外，不做任何缓存或索引优化，保持代码最小化。
"""
from __future__ import annotations

import threading
from collections import OrderedDict
from typing import Iterable

from domain.recipe.models import Recipe
from domain.shared.value_objects import RecipeId
from domain.recipe.repository import AbstractRecipeRepo

###############################################################################
# In‑Memory Implementation
###############################################################################

class MemoryRecipeRepo(AbstractRecipeRepo):  # noqa: WPS110
    """基于 Python 字典的 RecipeRepo。"""

    def __init__(self) -> None:  # noqa: D401
        # OrderedDict 方便测试时保持插入顺序，输出 list 可预测
        self._storage: OrderedDict[RecipeId, Recipe] = OrderedDict()
        self._lock = threading.RLock()

    # ----------------------------- 查询 -----------------------------
    def get(self, recipe_id: RecipeId) -> Recipe | None:  # noqa: D401
        with self._lock:
            return self._storage.get(recipe_id)

    def list(self) -> Iterable[Recipe]:  # noqa: D401
        with self._lock:
            # 返回 shallow copy 避免被调用方修改内部状态
            return list(self._storage.values())

    def find_by_name(self, name: str) -> Recipe | None:  # noqa: D401
        with self._lock:
            for recipe in self._storage.values():
                if recipe.name == name:
                    return recipe
            return None

    # ----------------------------- 写入 -----------------------------
    def add(self, recipe: Recipe) -> None:  # noqa: D401
        with self._lock:
            if recipe.id in self._storage:
                raise KeyError(f"Recipe {recipe.id} 已存在")
            self._storage[recipe.id] = recipe

    def update(self, recipe: Recipe) -> None:  # noqa: D401
        with self._lock:
            if recipe.id not in self._storage:
                raise KeyError(f"Recipe {recipe.id} 不存在，无法更新")
            self._storage[recipe.id] = recipe

    def remove(self, recipe_id: RecipeId) -> None:  # noqa: D401
        with self._lock:
            self._storage.pop(recipe_id, None)  # 不存在时静默忽略
