"""infra.event_bus
~~~~~~~~~~~~~~~~~

简易事件总线实现。

此模块提供三个可用的事件总线实现：

* ``NullEventBus`` —— 默认 no-op；
* ``SimpleEventBus`` —— 同步调用注册处理函数；
* ``LoggingEventBus`` —— 使用 ``logging`` 输出事件内容。

所有实现都遵循最小 ``EventBus`` 协议，只要求实现 ``publish(event)`` 方法。
"""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, DefaultDict, Protocol, Type
import logging

from domain.shared.events import DomainEvent


class EventBus(Protocol):  # noqa: WPS110
    """事件总线协议。"""

    def publish(self, event: DomainEvent) -> None:  # noqa: D401
        ...


class NullEventBus:
    """什么也不做的事件总线。"""

    def publish(self, event: DomainEvent) -> None:  # noqa: D401, ANN001
        return None


Handler = Callable[[DomainEvent], None]


class SimpleEventBus:
    """在本进程内同步分发事件。"""

    def __init__(self) -> None:  # noqa: D401
        self._subs: DefaultDict[Type[DomainEvent], list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: Handler) -> None:
        """注册事件处理函数。"""
        self._subs[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:  # noqa: D401
        for handler in self._subs.get(type(event), []):
            handler(event)


class LoggingEventBus:
    """将事件序列化后写入日志。"""

    def __init__(self, logger: logging.Logger | None = None) -> None:  # noqa: D401
        self.logger = logger or logging.getLogger(__name__)

    def publish(self, event: DomainEvent) -> None:  # noqa: D401
        self.logger.info("event: %s", event.to_dict())
