"""domain.inventory.repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

库存仓库抽象 Port。

**InventoryItem** 是 *Cookmate* 读/写最频繁的实体之一：
CLI / API 所有与库存查询、烹饪扣减、入库补货都要经由它，因此仓库接口要同时
支持 **单条查询**、**批量列举** 与 **条件筛选**。MVP 阶段仅保留最小方法集，
满足核心闭环需求。

> 注意：本模块 **仅定义方法签名**，不实现任何持久化逻辑。
"""
from __future__ import annotations

import abc
from typing import Iterable, Protocol, runtime_checkable

from domain.shared.value_objects import IngredientId
from domain.inventory.models import InventoryItem

###############################################################################
# Repository Protocol
###############################################################################

@runtime_checkable
class AbstractInventoryRepo(Protocol):  # noqa: WPS110
    """库存仓库接口（Port）。"""

    # ---------------------------- 查询 ----------------------------
    @abc.abstractmethod
    def get(self, ingredient_id: IngredientId) -> InventoryItem | None:  # noqa: D401
        """按食材 ID 获取库存条目；不存在返回 ``None``。"""

    @abc.abstractmethod
    def list(self) -> Iterable[InventoryItem]:  # noqa: D401
        """列举全部库存条目。"""

    @abc.abstractmethod
    def low_stock(self) -> Iterable[InventoryItem]:  # noqa: D401
        """筛选低库存条目；具体阈值由实体方法 ``is_low_stock`` 决定。"""

    @abc.abstractmethod
    def expiring_soon(self, days: int = 3) -> Iterable[InventoryItem]:  # noqa: D401
        """筛选 *days* 天内即将过期的条目。"""

    # ---------------------------- 写入 ----------------------------
    @abc.abstractmethod
    def add_or_update(self, item: InventoryItem) -> None:  # noqa: D401
        """新增或覆盖库存条目（按 `ingredient_id` 唯一）。"""

    @abc.abstractmethod
    def remove(self, ingredient_id: IngredientId) -> None:  # noqa: D401
        """删除库存条目；若不存在可静默或抛异常（实现自定）。"""
