"""domain.ingredient.repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

食材仓库抽象 Port。

该接口定义了 *Ingredient* 聚合根在持久化层的所有必要操作，供应用层依赖。
Adapters 层将提供具体实现（内存 / SQLite / 其他 DB）。

> 与菜谱仓库类似，本文件 **仅声明方法签名**，不涉及任何存储细节。
"""
from __future__ import annotations

import abc
from typing import Iterable, Protocol, runtime_checkable

from domain.shared.value_objects import IngredientId
from domain.ingredient.models import Ingredient

###############################################################################
# Repository Protocol
###############################################################################

@runtime_checkable
class AbstractIngredientRepo(Protocol):  # noqa: WPS110
    """食材仓库接口（Port）。"""

    # ---------------------------- 查询 ----------------------------
    @abc.abstractmethod
    def get(self, ingredient_id: IngredientId) -> Ingredient | None:  # noqa: D401
        """按 `ingredient_id` 获取食材；不存在返回 ``None``。"""

    @abc.abstractmethod
    def list(self) -> Iterable[Ingredient]:  # noqa: D401
        """返回仓库中所有食材的迭代器。"""

    @abc.abstractmethod
    def find_by_name(self, name: str) -> Ingredient | None:  # noqa: D401
        """按名称精确查找，避免重名或快速判断存在性。"""

    # ---------------------------- 写入 ----------------------------
    @abc.abstractmethod
    def add(self, ingredient: Ingredient) -> None:  # noqa: D401
        """保存新食材。若 ID 已存在则抛异常。"""

    @abc.abstractmethod
    def update(self, ingredient: Ingredient) -> None:  # noqa: D401
        """更新已有食材。按 ``ingredient.id`` 覆盖。"""

    @abc.abstractmethod
    def remove(self, ingredient_id: IngredientId) -> None:  # noqa: D401
        """删除食材；若不存在可静默或抛自定异常。"""
