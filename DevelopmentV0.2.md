# Development Guide (v0.2)

> **目标**：明确 *Cookmate* v0.2 (FastAPI + 前端 Demo) 阶段 **每个文件/模块** 的功能与边界，方便团队协作与后续迭代。
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
│       └── main.py                  ✅
├── infra/
│   ├── event_bus.py                 ✅
│   └── logging.py                   ✅
├── web/
│   ├── api/
│   │   ├── main.py                  ✅
│   │   ├── deps.py                  ✅
│   │   └── routers/
│   │       ├── recipe.py            ✅
│   │       ├── inventory.py         ✅
│   │       └── planner.py           ✅
│   └── frontend/
│       ├── index.html               ⬜
│       └── static/                  ⬜
└── tests/
    ├── test_recipe_service.py       ✅
    ├── test_cook_service.py         ✅
    ├── test_planner_service.py      ✅
    └── conftest.py                  ✅
```

---

## 🚦 编码顺序 & 完成标记

| # | 文件/目录 | 为什么先写 | 完成标志 |
|---|-----------|-----------|---------|
| 1 | `web/api/main.py`, `deps.py` | 框架入口，提供统一依赖 | ✅ |
| 2 | `web/api/routers/recipe.py` | 暴露菜谱相关 API | ✅ |
| 3 | `web/api/routers/inventory.py` | 库存管理 API | ✅ |
| 4 | `web/api/routers/planner.py` | 智能筛选 & 购物清单 | ✅ |
| 5 | `tests/test_api_endpoints.py` | 覆盖所有路由 | ⬜ |
| 6 | `web/frontend/` | 简易前端 Demo | ⬜ |
| 7 | 文档与部署脚本 | 发布准备 | ⬜ |

> **下一步优先级**：启动 v0.2 开发，搭建 FastAPI 服务与前端 Demo。

---

## 📑 里程碑对应文件

| 里程碑 | 需完成文件 | 当前进度 |
|--------|-----------|---------|
| **M1 Domain+Memory** | `domain/**`, `adapters/repo_memory/**`, `app/services/**`, `tests/test_recipe_service.py`, `app/unit_of_work.py` | ✅ 完成 |
| **M2 SQLite+CLI** | `adapters/repo_sqlite/**`, `infra/**`, `tests/test_cook_service.py`, `tests/test_planner_service.py`, `adapters/cli/main.py` | ✅ 完成 |
| **M3 API 基础** | `web/api/**`, `tests/test_api_endpoints.py` | ⬜ |
| **M4 前端 Demo** | `web/frontend/**` | ⬜ |

---

### 迭代节奏建议

| 日程 | 目标 |
|------|------|
| **Day 1** | 搭建 FastAPI 应用框架，提供基本依赖。 |
| **Day 2** | 完成核心业务路由（Recipe/Inventory/Planner），编写 API 测试。 |
| **Day 3** | 交付前端 Demo，确保与 API 联调通过，打标签 *v0.2.0*。 |

---

> 请在开始下一步编码前，对照上表勾选状态并提交 PR。任何问题欢迎在 Issue 中讨论！
