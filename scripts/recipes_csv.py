import csv
import json
from app.unit_of_work import SqlAlchemyUnitOfWork
from app.services.recipe_service import RecipeService, RecipeAlreadyExistsError

FIELDS = [
    "name",
    "category",
    "method",
    "difficulty",
    "pairing",
    "time_minutes",
    "notes",
    "tutorial",
    "cover",
    "ingredients",
    "steps",
]


def export_recipes(csv_path: str = "recipes.csv") -> None:
    """Export all recipes to a CSV file."""
    uow = SqlAlchemyUnitOfWork()
    svc = RecipeService(uow)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for r in svc.list_recipes():
            meta = r.metadata or {}
            row = {
                "name": r.name,
                "category": meta.get("category", ""),
                "method": meta.get("method", ""),
                "difficulty": meta.get("difficulty", ""),
                "pairing": meta.get("pairing", ""),
                "time_minutes": meta.get("time_minutes", ""),
                "notes": meta.get("notes", ""),
                "tutorial": meta.get("tutorial", ""),
                "cover": meta.get("cover", ""),
                "ingredients": json.dumps({
                    svc.uow.ingredients.get(iid).name: [float(q.amount), q.unit.value]
                    for iid, q in r.ingredients.items()
                    if svc.uow.ingredients.get(iid)
                }, ensure_ascii=False),
                "steps": json.dumps(list(r.steps), ensure_ascii=False),
            }
            writer.writerow(row)


def import_recipes(csv_path: str = "recipes.csv") -> None:
    """Load recipes from a CSV file and store them."""
    uow = SqlAlchemyUnitOfWork()
    svc = RecipeService(uow)
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ingredients = json.loads(row["ingredients"])
            steps = json.loads(row["steps"])
            meta = {k: row[k] for k in FIELDS if k not in {"name", "ingredients", "steps"} and row[k]}
            try:
                svc.create_recipe(row["name"], ingredients, steps, meta)
            except RecipeAlreadyExistsError:
                continue


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export or import recipes")
    parser.add_argument("action", choices=["export", "import"])
    parser.add_argument("csv", nargs="?", default="recipes.csv")
    args = parser.parse_args()

    if args.action == "export":
        export_recipes(args.csv)
    else:
        import_recipes(args.csv)
