# Cookmate API Reference

Below is a list of HTTP endpoints provided in v0.3. All responses are JSON.

## Ping
- `GET /ping` – health check

## Recipes
- `GET /recipes/` – list recipe names
- `POST /recipes/` – create a recipe
  - body: `{ "name": str, "ingredients": {name: [amount, unit]}, "steps": [str] }`
- `DELETE /recipes/{name}` – remove a recipe by name

## Inventory
- `GET /inventory/` – list current inventory
- `GET /inventory/low` – items in low stock
- `GET /inventory/expiring?days=N` – items expiring within N days
- `POST /inventory/` – add or update an item
  - body: `{ "ingredient": str, "amount": number, "unit": str, "expires_on": "YYYY-MM-DD" }`
- `DELETE /inventory/{ingredient}` – delete inventory entry

## Planner
- `GET /planner/cookable?servings=N` – list cookable recipes
- `POST /planner/shopping` – generate shopping list
  - body: `{ "recipes": {recipe_id: servings} }` (optional)
