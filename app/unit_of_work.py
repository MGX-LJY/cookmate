"""app.unit_of_work
~~~~~~~~~~~~~~~~~~~~

Unit‑of‑Work (UoW) 模式实现。

> 该模块在 *应用服务层* 承担 **事务边界** 角色：
> * 聚合多个仓库实例的生命周期；
> * 统一 commit / rollback；
> * 为服务提供 `with UnitOfWork(...)` 上下文管理器语法。

设计思路
--------
1. **抽象基类 `AbstractUnitOfWork`** —— 仅定义协议：`recipes`, `ingredients`,
   `inventories` 属性及 `commit()`, `rollback()` 方法；
2. **内存实现 `MemoryUnitOfWork`** —— 组合内存仓库，测试/原型时使用；
3. **SQLite 实现 `SqlAlchemyUnitOfWork`** —— 组合 SQLAlchemy Session 与
   SQLite 仓库，后续在 `adapters/repo_sqlite/` 中引用。

> ⚠️ 事务语义：SQLite/SQLAlchemy 使用 *session.commit()* / *session.rollback()*；
> Memory 版本则 commit 为 no‑op，以保持接口一致。
"""
from __future__ import annotations

import abc
from contextlib import AbstractContextManager
from typing import Protocol, runtime_checkable

from adapters.repo_memory.ingredient_repo import MemoryIngredientRepo
from adapters.repo_memory.inventory_repo import MemoryInventoryRepo
from adapters.repo_memory.recipe_repo import MemoryRecipeRepo
from domain.ingredient.repository import AbstractIngredientRepo
from domain.inventory.repository import AbstractInventoryRepo
from domain.recipe.repository import AbstractRecipeRepo

###############################################################################
# 抽象 UnitOfWork
###############################################################################

@runtime_checkable
class AbstractUnitOfWork(AbstractContextManager, Protocol):  # noqa: WPS110
    """UoW 协议。"""

    # 公开的仓库属性
    recipes: AbstractRecipeRepo
    ingredients: AbstractIngredientRepo
    inventories: AbstractInventoryRepo

    # 事务控制
    @abc.abstractmethod
    def commit(self) -> None:  # noqa: D401
        """提交事务。"""

    @abc.abstractmethod
    def rollback(self) -> None:  # noqa: D401
        """回滚事务。"""

###############################################################################
# 内存版 UnitOfWork
###############################################################################

class MemoryUnitOfWork(AbstractUnitOfWork):  # noqa: WPS110
    """基于内存仓库的 UoW，用于测试与 CLI 原型运行。"""

    def __init__(self) -> None:  # noqa: D401
        self.recipes = MemoryRecipeRepo()
        self.ingredients = MemoryIngredientRepo()
        self.inventories = MemoryInventoryRepo()
        self._committed: bool = False

    # ---------------- 上下文管理 ----------------
    def __enter__(self) -> "MemoryUnitOfWork":  # noqa: D401
        # 内存实现无真正事务，直接返回 self
        return self

    def __exit__(self, exc_type, exc, tb):  # noqa: D401, ANN001, ANN002, ANN003
        if exc:
            self.rollback()
        else:
            self.commit()
        # 按 `contextlib.AbstractContextManager` 约定，返回 False 以传播异常
        return False

    # ---------------- 事务操作 ----------------
    def commit(self) -> None:  # noqa: D401
        # 内存实现：标记已提交即可；便于测试断言
        self._committed = True

    def rollback(self) -> None:  # noqa: D401
        # 对内存 repo 直接重置存储，模拟回滚
        self.__init__()

###############################################################################
# 占位：SQLAlchemy / SQLite 实现（后续在 adapters 目录补充）
###############################################################################

try:  # noqa: WPS501 (允许裸 except ImportError)
    from adapters.repo_sqlite.db import SessionLocal
    from adapters.repo_sqlite.ingredient_repo import SqlIngredientRepo
    from adapters.repo_sqlite.inventory_repo import SqlInventoryRepo
    from adapters.repo_sqlite.recipe_repo import SqlRecipeRepo

    class SqlAlchemyUnitOfWork(AbstractUnitOfWork):  # noqa: WPS110
        """SQLite + SQLAlchemy UoW 实现。"""

        def __init__(self) -> None:  # noqa: D401
            self.session = SessionLocal()
            self.recipes = SqlRecipeRepo(self.session)
            self.ingredients = SqlIngredientRepo(self.session)
            self.inventories = SqlInventoryRepo(self.session)

        # 上下文管理
        def __enter__(self) -> "SqlAlchemyUnitOfWork":  # noqa: D401
            return self

        def __exit__(self, exc_type, exc, tb):  # noqa: D401, ANN001, ANN002, ANN003
            if exc:
                self.rollback()
            else:
                self.commit()
            self.session.close()
            return False

        # 事务操作
        def commit(self) -> None:  # noqa: D401
            self.session.commit()

        def rollback(self) -> None:  # noqa: D401
            self.session.rollback()

except ImportError:  # pragma: no cover
    # 尚未实现 SQLite 部分时保持占位，确保 import 不报错

    class SqlAlchemyUnitOfWork:  # type: ignore
        """占位符：等待 repo_sqlite 模块实现后替换。"""

        def __init__(self, *args, **kwargs):  # noqa: D401, ANN001
            raise NotImplementedError("SQLite UnitOfWork 尚未实现")
