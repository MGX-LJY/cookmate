from adapters.repo_sqlite.db import init_db
from adapters.repo_sqlite.recipe_repo import RecipeORM, RecipeIngredientORM
from adapters.repo_sqlite.ingredient_repo import IngredientORM
from adapters.repo_sqlite.inventory_repo import InventoryItemORM

if __name__ == "__main__":
    init_db(RecipeORM, RecipeIngredientORM, IngredientORM, InventoryItemORM)
    print("SQLite database initialized ✔")
