"""domain.shared.events
~~~~~~~~~~~~~~~~~~~~~~

领域事件定义。

在 DDD 中，**领域事件 (Domain Event)** 用于描述“某事已经发生”且对
领域内其他部分具有意义的重要事实。事件需要满足：

1. **不可变** —— 事件一旦发生即定格，不应再被修改；
2. **描述过去** —— 事件名称多用过去式，如 *RecipeCooked*；
3. **可序列化** —— 方便持久化、跨进程传递或发布到消息队列。

下方代码包含：

* ``DomainEvent`` 基类：统一 `id` / `occurred_on` / `metadata` 字段；
* 两个具体事件：``RecipeCooked``、``InventoryLow``，分别在烹饪成功和库存低于阈值时发布。

所有注释使用中文，便于团队快速理解与维护。
"""
from __future__ import annotations

import datetime as _dt
import uuid as _uuid
from dataclasses import dataclass, field
from typing import Mapping

from domain.shared.value_objects import IngredientId, RecipeId, Quantity

###############################################################################
# 领域事件基类
###############################################################################

# kw_only=True 解决 *子类新增必填字段* 与 *父类默认字段* 的顺序冲突：
#   Python dataclass 要求：无默认参数需位于有默认参数之前；
#   继承场景下，父类字段会先排在前面，若父类字段 **有默认值**，
#   子类再添加 *无默认值* 字段就会违反此规则。
# 设置 kw_only=True 后，父类带默认值的字段只能作为关键字参数传入，
# 因此不会与子类的位置参数产生冲突，完美解决 “Non‑default argument follows
# default argument” 报错。

@dataclass(frozen=True, slots=True, kw_only=True)
class DomainEvent:  # noqa: WPS110
    """所有领域事件的共同基类。"""

    id: _uuid.UUID = field(default_factory=_uuid.uuid4, metadata={"doc": "事件唯一标识"})
    occurred_on: _dt.datetime = field(
        default_factory=lambda: _dt.datetime.now(_dt.timezone.utc),
        metadata={"doc": "事件发生时间（UTC）"},
    )
    metadata: Mapping[str, str] | None = field(
        default=None,
        metadata={"doc": "附加上下文信息（可选）"},
    )

    # WHY: 使用 UTC 存储时间戳，避免跨时区错误；显示时再转换本地时区。

    # ------------------------------------------------------------------
    # 序列化辅助（用于持久化 / MQ 负载）
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, object]:  # noqa: D401
        """序列化为 JSON 友好的字典。"""
        return {
            "event_type": self.__class__.__name__,
            "id": str(self.id),
            "occurred_on": self.occurred_on.isoformat(),
            "payload": {
                k: (str(v) if isinstance(v, _uuid.UUID) else v)
                for k, v in self.__dict__.items()
                if k not in {"id", "occurred_on", "metadata"}
            },
            "metadata": dict(self.metadata) if self.metadata else {},
        }


###############################################################################
# 具体事件：RecipeCooked
###############################################################################

@dataclass(frozen=True, slots=True, kw_only=True)
class RecipeCooked(DomainEvent):  # noqa: WPS110
    """成功烹饪某道菜谱后发布。"""

    # 无默认参数先写，符合 dataclass 规则
    recipe_id: RecipeId
    consumed_ingredients: Mapping[IngredientId, Quantity] = field(
        metadata={"doc": "本次烹饪扣减的食材及数量"},
    )
    servings: int = field(
        default=1,
        metadata={"doc": "份数，用于营养/成本统计，默认 1"},
    )

    # WARNING: consumed_ingredients 建议使用不可变 Mapping（如 MappingProxyType）
    #          调用端如需写入，请在创建事件前自行构造。

###############################################################################
# 具体事件：InventoryLow
###############################################################################

@dataclass(frozen=True, slots=True, kw_only=True)
class InventoryLow(DomainEvent):  # noqa: WPS110
    """库存低于阈值时发布。"""

    ingredient_id: IngredientId
    threshold: Quantity
    current_qty: Quantity

    # WHY: 将 threshold 放到事件里，方便订阅者判断补货等级或推送文案。
