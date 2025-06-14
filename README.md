
# Cookmate 🍳  
个人菜谱 & 冰箱库存管理器 – “录菜、管料、选菜、买菜” 一条龙

![status](https://img.shields.io/badge/status-pre--alpha-red)
![python](https://img.shields.io/badge/python-3.9%2B-blue)

---

## ✨ 主要特性
| 模块 | 能力 | 说明 |
|------|------|------|
| **菜谱管理** | 新增 / 编辑 / 批量导入 | 表格、爬虫、API 均可接入 |
| **库存管理** | 食材数量 / 保质期追踪 | 支持扫码、语音录入，过期提醒 |
| **烹饪执行** | 自动校验&扣减库存 | 生成历史记录，统计消耗 |
| **智能筛选** | 多维过滤可做菜 | 难度、时长、现有食材、口味… |
| **购物清单** | 一键汇总缺料 | 可拆分门店、比较价格 |

---

## 🏗️ 架构提要
- **分层 + 六边形**：`domain ➜ app ➜ adapters ➜ infra`  
- **模块化单体**：`domain/recipe`, `domain/inventory` 等物理隔离  
- **依赖倒置 & DI**：核心业务只依赖 Port 接口  
- **事件驱动**：领域事件广播，读取侧/提醒异步订阅  
- **测试优先**：每层对应独立测试文件夹，持续集成跑 `pytest`  

项目树（src-layout）：

```

cookmate/
├─ src/
│  ├─ domain/         # 纯业务模型
│  ├─ app/            # 用例服务
│  ├─ adapters/       # CLI / HTTP / Repo
│  └─ infra/          # 数据库、事件总线
└─ tests/             # pytest

````

---

## 🚀 快速开始

```bash
git clone https://github.com/yourname/cookmate.git
cd cookmate

# 安装 Python 3.9+ 后：
python3 -m venv .venv      # 创建虚拟环境
source .venv/bin/activate  # 激活
pip install -e .[dev]      # 开发模式安装（含 lint / test 依赖）

# 运行 CLI 原型
python -m adapters.cli.main --help
````

如需 Web API（FastAPI）：

```bash
uvicorn adapters.api.main:app --reload
```

浏览 `http://127.0.0.1:8000/docs` 查看 Swagger 文档。

---

## 🧩 代码风格 & 提交规范

| 工具             | 用途            | 运行方式                               |
| -------------- | ------------- | ---------------------------------- |
| **ruff**       | Lint & Format | `ruff check .`  /  `ruff format .` |
| **pytest**     | 单元 & 用例测试     | `pytest -q`                        |
| **pre-commit** | 自动钩子          | `pre-commit install`               |

提交信息遵循 **Conventional Commits**。

---

## 🗺️ 路线图

* [ ] 完成领域模型 & 抽象仓库
* [ ] SQLite 实现 + 移动到 `infra`
* [ ] 初版 CLI：录菜谱 / 录库存 / 扣库存
* [ ] 智能筛选 & 购物清单
* [ ] FastAPI HTTP 层 + 前端 Demo
* [ ] 持续集成：GitHub Actions 自动测试

---

## 🤝 贡献

欢迎 Issue、PR！在发起 PR 前请先创建对应 Issue 讨论设计，保持低耦合原则。

---

## 📄 License

MIT © 2025 Your Name

```

> **如何更新**  
> 1. 根据最终目录布局把 *项目树* 一段同步调整；  
> 2. 当新增依赖（如 `sqlalchemy`、`typer`）时，别忘了在 **Quick Start** 中补充。  

复制粘贴后即可作为第一个版本 README。如果需要更详细的安装截图、设计图或贡献指南，可随时扩展相应章节。祝编写顺利！
```
