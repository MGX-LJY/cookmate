"""domain.recipe.repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

菜谱仓库抽象 Port。

在六边形架构 (Hexagonal / Clean Architecture) 中，**Domain 层只依赖抽象接口**，
而实际的持久化逻辑由 Adapters 层实现。此模块定义 *Recipe* 相关的仓库协议，
供应用服务层注入并在测试中用内存实现替换。

> 本文件 **不包含任何数据库代码**，只声明方法签名与 type hints。
"""
from __future__ import annotations

import abc
from typing import Iterable, Protocol, runtime_checkable

from domain.shared.value_objects import RecipeId
from domain.recipe.models import Recipe

###############################################################################
# Repository Protocol
###############################################################################

@runtime_checkable
class AbstractRecipeRepo(Protocol):  # noqa: WPS110
    """菜谱仓库接口（Port）。"""

    # ---------------------------- 查询 ----------------------------
    @abc.abstractmethod
    def get(self, recipe_id: RecipeId) -> Recipe | None:  # noqa: D401
        """按 `recipe_id` 获取菜谱；不存在返回 ``None``。"""

    @abc.abstractmethod
    def list(self) -> Iterable[Recipe]:  # noqa: D401
        """返回仓库中所有菜谱的迭代器。"""

    @abc.abstractmethod
    def find_by_name(self, name: str) -> Recipe | None:  # noqa: D401
        """按菜名精确查找，用于避免重名。"""

    # ---------------------------- 写入 ----------------------------
    @abc.abstractmethod
    def add(self, recipe: Recipe) -> None:  # noqa: D401
        """保存新菜谱。若 `id` 已存在则抛异常。"""

    @abc.abstractmethod
    def update(self, recipe: Recipe) -> None:  # noqa: D401
        """更新现有菜谱。按 ``recipe.id`` 覆盖存储。"""

    @abc.abstractmethod
    def remove(self, recipe_id: RecipeId) -> None:  # noqa: D401
        """删除菜谱；若不存在应当静默忽略或抛自定义异常（实现自定）。"""

    # WHY: 不强制返回值，交由具体实现决定；应用层通常不关心删除结果。
