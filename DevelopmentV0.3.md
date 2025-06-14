# Development Guide (v0.3)

> **目标**：在 v0.2 基础上进一步完善前端界面布局，并为 PlannerService 的高级功能预留接口。

> **状态标识** | ✅ 完成并通过测试 | ⬜ 尚未实现 / 未通过

---

## 📂 目录结构总览（含完成状态）

```text
cookmate/
├── web/
│   ├── api/                         ✅
│   └── frontend/
│       ├── main.py                  ✅ 更新版本号
│       └── static/
│           └── index.html           ✅ 全新布局
```

---

## 🚦 关键任务

| # | 文件/目录 | 说明 | 完成标志 |
|---|-----------|------|---------|
| 1 | `web/frontend/static/index.html` | 优雅导航栏+示例菜谱表格 | ✅ |
| 2 | `web/frontend/main.py` | 暴露静态资源，更新版本号 | ✅ |
| 3 | `web/api/routers/recipe.py` | 新增删除接口 | ✅ |
| 4 | `README.md` | 更新路线图与示例菜谱 | ✅ |
| 5 | `pyproject.toml` | 升级版本到 0.3.1 | ✅ |

> **下一步优先级**：在 v0.4 中为 UI 增加动画效果与过渡。

