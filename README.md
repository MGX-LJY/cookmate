# Cookmate 🍳
> *个人菜谱 & 冰箱库存管理器* – 录菜、管料、选菜、买菜，一条龙完成

![status](https://img.shields.io/badge/status-pre--alpha-red)
![python](https://img.shields.io/badge/python-3.9%2B-blue)

---

## ✨ 功能概览

| 领域 | 说明 |
|------|------|
| **菜谱管理** | 新增 / 编辑 / 批量导入（CSV、网页爬虫） |
| **库存管理** | 食材数量 & 保质期追踪，支持扫码 / 语音录入 |
| **烹饪执行** | 校验→扣减库存，写入烹饪日志 |
| **智能筛选** | 难度、时长、现有食材等多维过滤可做菜 |
| **购物清单** | 汇总缺料，一键生成买菜清单（可按门店拆分） |

---

## 🏗️ 项目结构

```

.
├── adapters/              # 各类技术实现
│   ├── repo\_memory/       # 纯内存仓库（测试/原型）
│   └── repo\_sqlite/       # SQLite 仓库（预留）
├── app/                   # 用例层 (Services / Commands)
├── domain/                # 业务模型（纯净，无三方依赖）
│   ├── recipe/ --- 聚合根 Recipe
│   ├── ingredient/ --- 聚合根 Ingredient
│   ├── inventory/ --- 聚合根 InventoryItem
│   └── shared/ --- 值对象 & 领域事件
├── infra/                 # 数据库 & 事件总线等基础设施
├── tests/                 # pytest 测试
└── pyproject.toml         # 构建 / 依赖声明

````

> **Flat-layout**：顶层包 (`app`, `domain`, `adapters`, `infra`) 直接作为 Python 包；  
> `pyproject.toml` 中已显式列出包名，开发模式安装后即可 `import domain ...`。

---

## 🚀 快速开始

### 1. 克隆 & 进入目录

```bash
git clone https://github.com/yourname/cookmate.git
cd cookmate
````

### 2. 创建并激活虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

* **仅运行依赖**

  ```bash
  pip install -e .
  ```

* **运行 + 开发依赖（推荐给贡献者）**

  ```bash
  pip install -e .[dev]
  ```

### 4. 运行测试

```bash
pytest -q            # 发现 tests/ 下所有用例
```

---

## 🧑‍💻 开发速查

| 命令                                       | 说明                              |
| ---------------------------------------- | ------------------------------- |
| `make lint`                              | ruff 检查 & 格式化（需要在 Makefile 中定义） |
| `make mypy`                              | 静态类型检查                          |
| `uvicorn adapters.api.main:app --reload` | 启动 FastAPI（API 层完成后）            |
| `python -m adapters.cli.main --help`     | 查看 CLI 原型帮助                     |

---

## 🔌 技术要点

* **Hexagonal + 模块化单体**：业务核心与框架解耦，可平滑迁移到微服务。
* **依赖倒置**：Domain 只依赖抽象 Port；具体实现位于 `adapters/…`。
* **事件驱动**：领域事件广播，读取侧 / 过期提醒异步订阅。
* **测试优先**：Memory-repo + DI，单元测试无外部依赖。

---

## 🗺️ 路线图

* [ ] 领域模型 & 内存仓库 ✅
* [ ] SQLite 仓库 (SQLAlchemy)
* [ ] PlannerService：智能筛选 / 购物清单
* [ ] CLI：`cookmate add-recipe / cook / list`
* [ ] FastAPI HTTP 层 + 前端 Demo
* [ ] 持续集成：GitHub Actions 运行 lint + test
* [ ] Docker 化部署 & 备份策略

---

## 🤝 贡献指南

1. 新建 Issue 讨论需求或缺陷
2. Fork → 新建分支 (`feat/xxx` / `fix/xxx`)
3. 确保 `pytest` & `ruff` 通过
4. 提 PR，并关联 Issue

提交信息遵循 **Conventional Commits**。

---

## 📄 License

MIT © 2025 Your Name

```

> **提示**  
> - 若后续切换到 *src-layout*，只需更新“项目结构”与安装说明中的路径提示。  
> - 如果你计划加 `Makefile`、`pre-commit`，可在 **开发速查** 中列更多命令。  

复制到 `README.md` 后即可生效；需要徽章或作者信息个性化时按需求替换。祝项目进展顺利!
```
