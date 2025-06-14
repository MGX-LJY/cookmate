# Development Guide

> **目标**：明确 *Cookmate* MVP (CLI + SQLite) 阶段 **每个文件/模块** 的功能与边界，方便团队协作与后续迭代。
>
> **状态标识** | ✅ 完成并通过测试 | ⬜ 尚未实现 / 未通过

---

## 📂 目录结构总览（含完成状态）

```text
cookmate/
├── domain/
│   ├── recipe/
│   │   ├── models.py                ✅
│   │   └── repository.py            ✅
│   ├── ingredient/
│   │   ├── models.py                ✅
│   │   └── repository.py            ✅
│   ├── inventory/
│   │   ├── models.py                ✅
│   │   └── repository.py            ✅
│   └── shared/
│       ├── value_objects.py         ✅
│       └── events.py                ✅
├── app/
│   ├── services/
│   │   ├── recipe_service.py        ✅
│   │   ├── cook_service.py          ✅
│   │   └── planner_service.py       ✅
│   └── unit_of_work.py              ✅
├── adapters/
│   ├── repo_memory/
│   │   ├── recipe_repo.py           ✅
│   │   ├── inventory_repo.py        ✅
│   │   └── ingredient_repo.py       ✅
│   ├── repo_sqlite/
│   │   ├── db.py                    ✅
│   │   ├── recipe_repo.py           ✅
│   │   ├── inventory_repo.py        ✅
│   │   └── ingredient_repo.py       ✅
│   └── cli/
│       └── main.py                  ⬜
├── infra/
│   ├── event_bus.py                 ✅
│   └── logging.py                   ✅
└── tests/
    ├── test_recipe_service.py       ✅
    ├── test_cook_service.py         ✅
    ├── test_planner_service.py      ⬜
    └── conftest.py                  ✅
```

---

## 🚦 编码顺序 & 完成标记

| # | 文件/目录 | 为什么先写 | 完成标志 |
|---|-----------|-----------|---------|
| 1 | `domain/shared/value_objects.py`, `events.py` | 稳定基石，无外部依赖 | **✅ 已实现 & 通过测试** |
| 2 | `domain/ingredient/models.py` | 简单聚合，不依赖其他聚合 | **✅** |
| 3 | `domain/recipe/models.py` | 核心聚合依赖 Ingredient | **✅** |
| 4 | `domain/inventory/models.py` | 与 Cook 强关联 | **✅** |
| 5 | `domain/**/repository.py` | 定义 Port 先行 | **✅** |
| 6 | `adapters/repo_memory/*` | 支持 TDD，脱离 DB | **✅** |
| 7 | `app/unit_of_work.py` | 事务边界 | **✅** |
| 8 | `app/services/*.py` | 业务价值最大 | **✅** |
| 9 | `tests/*` (当前仅 Recipe) | 驱动设计收敛 | **✅ test_recipe_service test_cook_service通过** |
|10 | `adapters/repo_sqlite/*`, `infra/event_bus.py`, `infra/logging.py` | 持久化 & 基础设施 | ⬜ **待实现** |
|11 | `adapters/cli/main.py` | 完整用户链路 | ⬜ **待实现** |

> **下一步优先级**：实现步骤 10（SQLite Repos & EventBus & Logging）→ 步骤 11（Typer CLI）。

---

## 📑 里程碑对应文件

| 里程碑 | 需完成文件 | 当前进度 |
|--------|-----------|---------|
| **M1 Domain+Memory** | `domain/**`, `adapters/repo_memory/**`, `app/services/**`, `tests/test_recipe_service.py`, `app/unit_of_work.py` | **✅ 已全部通过 pytest** |
| **M2 SQLite+CLI** | `adapters/repo_sqlite/**`, `infra/**`, `tests/test_cook_service.py`, `tests/test_planner_service.py`, `adapters/cli/main.py` | ⬜ 进行中 |

---

### 迭代节奏建议

| 日程 | 目标 |
|------|------|
| **Day 1** | SQLite ORM & `db.py` 模板；完成三个 SQLite Repo；补充 EventBus、Logging。 |
| **Day 2** | `CookService` / `PlannerService` 集成测试 (SQLite 后端)；修复兼容性问题。 |
| **Day 3** | 完成 Typer CLI；编写 End‑to‑End 测试脚本；打标签 *v0.1.0*。 |

---

> 请在开始下一步编码前，对照上表勾选状态并提交 PR。任何问题欢迎在 Issue 中讨论！
