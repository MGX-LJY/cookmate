"""infra.logging
~~~~~~~~~~~~~~~

简单日志配置工具。

提供 ``setup`` 函数统一初始化根 logger，以及 ``get_logger`` 辅助按需获取。
"""
from __future__ import annotations

import logging

DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def setup(level: str | int = "INFO", *, log_file: str | None = None) -> None:
    """配置根日志记录器。"""
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(level=level, format=DEFAULT_FORMAT, handlers=handlers)


def get_logger(name: str | None = None) -> logging.Logger:
    """获取按默认配置初始化的 ``Logger``。"""
    return logging.getLogger(name)
