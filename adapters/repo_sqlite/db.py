"""adapters.repo_sqlite.db
~~~~~~~~~~~~~~~~~~~~~~~~~~

SQLite / SQLAlchemy 2.0 基础设施。

该模块只做三件事：
1. **创建 Engine** – 统一打开同一 SQLite 文件；
2. **提供 SessionLocal** – 给 Repo & UoW 注入；
3. **暴露 metadata & create_all()** – 供 CLI 初始化数据库。

> ⚠️ 领域模型层 **不允许** 直接依赖 SQLAlchemy；
> 任何 ORM 映射类应位于 `adapters.repo_sqlite.*_repo` 中定义。
"""
from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

###############################################################################
# 配置常量
###############################################################################

# 默认数据库文件位于项目根的 .data 目录中；可通过环境变量覆盖。
_DB_DIR = Path(os.getenv("COOKMATE_DB_DIR", ".data"))
_DB_DIR.mkdir(exist_ok=True)
_DB_PATH = _DB_DIR / os.getenv("COOKMATE_DB_FILE", "cookmate.sqlite3")
_SQLITE_URL = f"sqlite+pysqlite:///{_DB_PATH}"

###############################################################################
# Naming Convention (防止迁移冲突)
###############################################################################

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=NAMING_CONVENTION)

###############################################################################
# Engine & SessionLocal
###############################################################################

_engine: Engine | None = None


def get_engine(echo: bool = False) -> Engine:  # noqa: D401
    """惰性创建并返回全局 Engine。"""
    global _engine  # noqa: WPS420
    if _engine is None:
        _engine = create_engine(
            _SQLITE_URL,
            echo=echo,
            future=True,  # SQLAlchemy 2.0 API 风格
        )
    return _engine


# scoped_session 保证线程隔离；repo 内持有 session 实例即可。
SessionLocal = scoped_session(
    sessionmaker(bind=get_engine(), autocommit=False, autoflush=False, future=True),
)

###############################################################################
# DB 初始化
###############################################################################

def init_db(*orm_bases) -> None:  # noqa: D401
    """创建所有声明在 *orm_bases 的表。(repo 层调用)"""
    engine = get_engine()
    for base in orm_bases:
        base.metadata.create_all(engine)

###############################################################################
# CLI Helper
###############################################################################

if __name__ == "__main__":
    from argparse import ArgumentParser, Namespace

    parser = ArgumentParser(description="Cookmate DB 初始化/检查工具")
    parser.add_argument("--echo", action="store_true", help="SQLAlchemy echo flag")

    args: Namespace = parser.parse_args()
    engine = get_engine(echo=args.echo)
    print(f"Database URL = {_SQLITE_URL}")
    # 仅打印数据库连接可用性；真正 create_all 由 repo_sqlite/*_repo 调用
    with engine.connect() as conn:
        conn.execute("SELECT 1")
        print("SQLite connection OK ✔")
