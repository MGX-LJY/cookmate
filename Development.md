# Development Guide

> **目标**：明确 *Cookmate* MVP (CLI + SQLite) 阶段**每个文件/模块**的功能与边界，方便团队协作与后续迭代。

---

## 📂 目录结构总览

```text
cookmate/
├── domain/
│   ├── recipe/
│   │   ├── models.py
│   │   └── repository.py
│   ├── ingredient/
│   │   ├── models.py
│   │   └── repository.py
│   ├── inventory/
│   │   ├── models.py
│   │   └── repository.py
│   └── shared/
│       ├── value_objects.py
│       └── events.py
├── app/
│   ├── services/
│   │   ├── recipe_service.py
│   │   ├── cook_service.py
│   │   └── planner_service.py
│   └── unit_of_work.py
├── adapters/
│   ├── repo_memory/
│   │   ├── recipe_repo.py
│   │   ├── inventory_repo.py
│   │   └── ingredient_repo.py
│   ├── repo_sqlite/
│   │   ├── db.py
│   │   ├── recipe_repo.py
│   │   ├── inventory_repo.py
│   │   └── ingredient_repo.py
│   └── cli/
│       └── main.py
├── infra/
│   ├── event_bus.py
│   └── logging.py
└── tests/
    ├── test_recipe_service.py
    ├── test_cook_service.py
    ├── test_planner_service.py
    └── conftest.py
```

---

## 📑 文件职责明细

### 1. **domain/** — 纯领域模型层

| 文件                           | 角色   | 主要职责                                                                                        |
| ---------------------------- | ---- | ------------------------------------------------------------------------------------------- |
| **recipe/models.py**         | 聚合根  | `Recipe` 数据结构；含 `id`、`name`、`steps`、`ingredients(required_qty)`；封装不变式检查与成本估算等领域方法。          |
| **recipe/repository.py**     | Port | 定义 `AbstractRecipeRepo` 接口 (`add` / `get` / `list`)；不实现持久化。                                 |
| **ingredient/models.py**     | 聚合根  | `Ingredient` 定义；包括 `unit`、`nutrition` 元数据；提供单位换算助手。                                         |
| **ingredient/repository.py** | Port | `AbstractIngredientRepo`。                                                                   |
| **inventory/models.py**      | 聚合根  | `InventoryItem`：`ingredient_id`、`quantity`、`expires_on`；封装 `is_expired()`、`consume(qty)` 等。 |
| **inventory/repository.py**  | Port | `AbstractInventoryRepo`。                                                                    |
| **shared/value\_objects.py** | 值对象  | 不可变对象：`Quantity`、`Unit`、标识符类 (`RecipeId`, `IngredientId`)；实现比较与序列化。                         |
| **shared/events.py**         | 领域事件 | 事件定义：`RecipeCooked`, `InventoryLow`；事件基类含时间戳、payload。                                       |

### 2. **app/** — 应用服务层

| 文件                               | 角色   | 主要职责                                               |
| -------------------------------- | ---- | -------------------------------------------------- |
| **services/recipe\_service.py**  | 应用服务 | 处理新增/编辑菜谱，用 UoW 协调事务；验证重复菜名。                       |
| **services/cook\_service.py**    | 应用服务 | 核心烹饪流程：校验库存、扣减、发布 `RecipeCooked`，返回缺料报告。           |
| **services/planner\_service.py** | 应用服务 | 根据库存筛选可做菜；生成购物清单 (按门店分拆)。                          |
| **unit\_of\_work.py**            | 事务边界 | `UnitOfWork` 抽象 & 具体实现：聚合 Repo、管理 commit/rollback。 |

### 3. **adapters/** — 基础设施适配层

| 路径                                   | 角色             | 主要职责                                                               |
| ------------------------------------ | -------------- | ------------------------------------------------------------------ |
| **repo\_memory/**                    | In‑Memory Repo | 为测试/原型实现 CRUD；线程安全。                                                |
|  └─ **recipe\_repo.py**              | Adapter        | `AbstractRecipeRepo` 的内存实现。                                        |
|  └─ **inventory\_repo.py**           | Adapter        | `AbstractInventoryRepo` 的内存实现。                                     |
|  └─ **ingredient\_repo.py**          | Adapter        | `AbstractIngredientRepo` 的内存实现。                                    |
| **repo\_sqlite/db.py**               | 基建             | 创建 SQLAlchemy 2.0 `engine` & `SessionLocal`；初始化表。                  |
| **repo\_sqlite/recipe\_repo.py**     | Adapter        | SQLite 持久化实现；包含 ORM 映射。                                            |
| **repo\_sqlite/inventory\_repo.py**  | Adapter        | 同上，针对 `InventoryItem`。                                             |
| **repo\_sqlite/ingredient\_repo.py** | Adapter        | 同上，针对 `Ingredient`。                                                |
| **cli/main.py**                      | 接口适配           | Typer CLI 入口，子命令：`add-recipe`、`cook`、`inventory`、`plan`；解析输入并调度服务。 |

### 4. **infra/** — 通用基础设施

| 文件                | 角色   | 主要职责                    |
| ----------------- | ---- | ----------------------- |
| **event\_bus.py** | 事件总线 | 发布/订阅简单实现；后续可替换外部 MQ。   |
| **logging.py**    | 日志   | `structlog` 配置，输出 JSON。 |

### 5. **tests/** — 测试

| 文件                            | 角色    | 主要职责                                            |
| ----------------------------- | ----- | ----------------------------------------------- |
| **conftest.py**               | 共用夹具  | 提供 Memory Repo & SQLite Repo fixture；参数化选择存储后端。 |
| **test\_recipe\_service.py**  | 单元测试  | 覆盖菜谱增删改查逻辑。                                     |
| **test\_cook\_service.py**    | 单元+集成 | 覆盖烹饪流程、库存扣减、事件发布。                               |
| **test\_planner\_service.py** | 单元测试  | 覆盖菜单筛选与购物清单生成。                                  |

---

## 🗂 里程碑对应文件

| 里程碑                  | 需完成文件                                                                    | 备注             |
| -------------------- | ------------------------------------------------------------------------ | -------------- |
| **M1 Domain+Memory** | `domain/**`, `adapters/repo_memory/**`, `app/services/**`, `tests/*`     | 单元测试绿灯         |
| **M2 SQLite+CLI**    | `adapters/repo_sqlite/**`, `adapters/cli/main.py`, `app/unit_of_work.py` | 集成测试、手动 CLI 体验 |

---

> 📝 *只实现你点名的文件，其他保持占位* —— 以最小增量确保 Commit 清晰。
下面给出 **MVP 阶段的编码顺序清单**（共 11 步），每一步说明“为什么先写”与“完成标志”。
按此路线可先在 **Memory-Repo** 环境跑通全部逻辑，再接入 SQLite 与 CLI，确保迭代粒度小、可随时回滚。

---

## 一览（只列文件，不写代码）

| #      | 需要完成的文件(夹)                                                         | 目标 & 理由                                                                                                                      | 完成标志                                                       |
| ------ | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| **1**  | `domain/shared/value_objects.py` `events.py`                       | 先定 **不可变值对象** 和 **领域事件基类**，给后续模型统一依赖点。DDD 推荐从稳定、无依赖的核心开始 ([learn.microsoft.com][1], [docs.appflowy.io][2])                   | `Quantity`, `Unit`, `RecipeId` 等类具备等值比较；`DomainEvent` 带时间戳 |
| **2**  | `domain/ingredient/models.py`                                      | Ingredient 聚合根依赖 Value Object，不依赖其他聚合，可最早落地 ([medium.com][3])                                                                | 含 `unit` 转换方法                                              |
| **3**  | `domain/recipe/models.py`                                          | Recipe 聚合根需要引用 Ingredient Id 与数量，是后续用例核心 ([medium.com][3])                                                                   | 校验食材列表非空、不重复                                               |
| **4**  | `domain/inventory/models.py`                                       | InventoryItem 与配套过期逻辑；Cook 流程必需 ([reddit.com][4])                                                                            | `consume(qty)` & `is_expired()` 通过测试                       |
| **5**  | `domain/**/repository.py` (三个)                                     | 定义 **Port** (抽象接口) 供服务依赖；Hexagonal 要先明确 Port 再写 Adapter ([stackoverflow.com][5], [softwareengineering.stackexchange.com][6]) | `add/get/list` 方法签字冻结                                      |
| **6**  | `adapters/repo_memory/*`                                           | In-Memory Repo 让单元测试独立于 DB；TDD/DDD 推荐先写内存实现再落地基础设施 ([softwareengineering.stackexchange.com][7], [stackoverflow.com][8])      | pytest 读取 / 写入全部通过                                         |
| **7**  | `app/unit_of_work.py`                                              | 聚合 Memory Repo，以事务边界封装；Repository + UoW 是经典组合 ([dev.to][9], [softwareengineering.stackexchange.com][6])                      | `with UnitOfWork()` 上下文自动 commit/rollback                  |
| **8**  | `app/services/*.py`                                                | Application Service 调度逻辑，依赖 Port + UoW，不触 I/O；业务价值最大，优先落地单元测试 ([medium.com][10])                                             | `cook_service` 能扣减库存并产出缺料列表                                |
| **9**  | `tests/*`                                                          | 为 #1 – #8 写红→绿测试；TDD 保证设计收敛 ([medium.com][11], [reddit.com][12])                                                             | `pytest -q` 绿灯                                             |
| **10** | `adapters/repo_sqlite/db.py` <br> `adapters/repo_sqlite/*_repo.py` | 基于 SQLAlchemy 2.0 映射实体；把已验证的领域逻辑持久化 ([reddit.com][4])                                                                        | Memory & SQLite 后端用同一测试套件均通过                               |
| **11** | `adapters/cli/main.py`                                             | Typer CLI 封装 Service；至此完成 “CLI + SQLite MVP” ([medium.com][3])                                                               | 终端可 `cookmate cook \"番茄炒蛋\"`                               |

> **注释约定**
>
> * 顶部模块级 docstring：一句话概述 + 栗子用法
> * 关键决策点行内 `# WHY: …` 阐释动机
> * 公共类型 & 协议在 `:returns:` / `:raises:` 中写明

---

### 推荐迭代节奏

1. **步骤 1 – 4**：一天内搞定 Value Object 与三聚合；边写边跑 `pytest --maxfail=1 -q`。
2. **步骤 5 – 9**：第二天集中写 Memory Repo→Service→Test，确保 Cook 流程闭环。
3. **步骤 10 – 11**：第三天落 SQLite & CLI，完成 MVP CLI 体验。

如需调整顺序或拆更小任务，随时告诉我！

[1]: https://learn.microsoft.com/en-us/archive/msdn-magazine/2009/february/best-practice-an-introduction-to-domain-driven-design?utm_source=chatgpt.com "Best Practice - An Introduction To Domain-Driven Design"
[2]: https://docs.appflowy.io/docs/documentation/software-contributions/architecture/domain-driven-design?utm_source=chatgpt.com "Domain Driven Design - AppFlowy Docs"
[3]: https://medium.com/%40mail2mhossain/domain-driven-design-demystified-strategic-tactical-and-implementation-layers-dad829be18f0?utm_source=chatgpt.com "Domain-Driven Design Demystified: Strategic, Tactical, and ..."
[4]: https://www.reddit.com/r/softwarearchitecture/comments/1brqh4t/a_very_simple_question_about_hexagonalclear/?utm_source=chatgpt.com "A very simple question about Hexagonal/Clear architecture - Reddit"
[5]: https://stackoverflow.com/questions/39765870/hexagonal-architecture-with-repository?utm_source=chatgpt.com "Hexagonal architecture with repository - Stack Overflow"
[6]: https://softwareengineering.stackexchange.com/questions/405699/is-the-repository-pattern-a-part-of-the-ports-and-adapters-concept?utm_source=chatgpt.com "Is the Repository pattern a part of the Ports and Adapters concept"
[7]: https://softwareengineering.stackexchange.com/questions/319759/how-to-combine-strict-tdd-and-ddd?utm_source=chatgpt.com "How to combine strict TDD and DDD?"
[8]: https://stackoverflow.com/questions/854142/tdd-and-ddd-while-still-understanding-the-domain?utm_source=chatgpt.com "TDD and DDD while still understanding the domain - Stack Overflow"
[9]: https://dev.to/ruben_alapont/repository-and-unit-of-work-in-domain-driven-design-531e?utm_source=chatgpt.com "Repository and Unit of Work in Domain-Driven Design"
[10]: https://medium.com/jamf-engineering/hexagonal-architecture-in-software-development-acb08c458f6a?utm_source=chatgpt.com "Hexagonal Architecture in Software Development | Jamf Engineering"
[11]: https://medium.com/%40joatmon08/test-driven-development-techniques-for-infrastructure-a73bd1ab273b?utm_source=chatgpt.com "Test-Driven Development for Infrastructure | by Rosemary Wang"
[12]: https://www.reddit.com/r/SoftwareEngineering/comments/1j7tcfy/tdd_on_trial_does_testdriven_development_really/?utm_source=chatgpt.com "TDD on Trial: Does Test-Driven Development Really Work? - Reddit"
