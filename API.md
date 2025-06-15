# Cookmate 接口文档

下表列出了 `web/api` 目录下所有 FastAPI 路由文件中定义的接口。除特殊说明外，均返回 JSON 格式。

## 通用

| 方法 | 路径 | 说明 | 定义文件 |
| --- | --- | --- | --- |
| GET | `/ping` | 健康检查 | `web/api/main.py` |

## 菜谱 (`web/api/routers/recipe.py`)

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/recipes/` | 获取所有菜谱名称 |
| POST | `/recipes/` | 新建菜谱，body: `{"name": str, "ingredients": {食材: [数量, 单位]}, "steps": [str]}` |
| DELETE | `/recipes/{name}` | 删除指定名称的菜谱 |

## 库存 (`web/api/routers/inventory.py`)

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/inventory/` | 当前库存列表 |
| GET | `/inventory/low` | 库存过低的食材 |
| GET | `/inventory/expiring?days=N` | N 天内过期的食材 |
| POST | `/inventory/` | 新增或更新库存，body: `{"ingredient": str, "amount": number, "unit": str, "expires_on": "YYYY-MM-DD"}` |
| DELETE | `/inventory/{ingredient}` | 删除指定食材的库存 |

## 智能筛选 (`web/api/routers/planner.py`)

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/planner/cookable?servings=N` | 根据现有库存列出可做菜谱 |
| POST | `/planner/shopping` | 生成购物清单，body: `{"recipes": {recipe_id: servings}}` (可选) |


