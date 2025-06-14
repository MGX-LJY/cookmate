import typer

from app.unit_of_work import MemoryUnitOfWork
from app.services.recipe_service import RecipeService
from app.services.cook_service import CookService, InsufficientInventoryError
from domain.ingredient.models import Ingredient
from domain.shared.value_objects import Unit
from infra.event_bus import LoggingEventBus
from infra.logging import setup

app = typer.Typer(name="cookmate")
inv_app = typer.Typer()
app.add_typer(inv_app, name="inventory")

uow = MemoryUnitOfWork()
event_bus = LoggingEventBus()


@app.command()
def add_ingredient(name: str, unit: str) -> None:
    """Add a new ingredient."""
    uow.ingredients.add(Ingredient(name=name, default_unit=Unit(unit)))
    typer.echo(f"Added ingredient '{name}' with unit {unit}")


@app.command("add-recipe")
def add_recipe(
    name: str,
    ingredient: list[str] = typer.Option(
        ..., "-i", "--ingredient", help="name,amount[,unit]", show_default=False
    ),
    step: list[str] = typer.Option(None, "-s", "--step", help="Cooking step"),
) -> None:
    """Create a recipe from CLI options."""
    svc = RecipeService(uow)
    inputs: dict[str, tuple[str, str]] = {}
    for item in ingredient:
        parts = item.split(",")
        if len(parts) not in (2, 3):
            raise typer.BadParameter("ingredient should be 'name,amount[,unit]'")
        ing_name, amount = parts[0], parts[1]
        unit_str = parts[2] if len(parts) == 3 else ""
        inputs[ing_name] = (amount, unit_str)
    rid = svc.create_recipe(name, inputs, list(step) if step else None)
    typer.echo(f"Recipe created: {rid}")


@app.command()
def list_recipes() -> None:
    """List all recipes."""
    svc = RecipeService(uow)
    for r in svc.list_recipes():
        typer.echo(f"{r.id} - {r.name}")


@app.command()
def cook(recipe: str, servings: int = 1) -> None:
    """Cook a recipe by name."""
    obj = uow.recipes.find_by_name(recipe)
    if not obj:
        typer.echo(f"Recipe '{recipe}' not found", err=True)
        raise typer.Exit(code=1)
    svc = CookService(uow, event_bus)
    try:
        svc.cook(obj.id, servings=servings)
        typer.echo("Cooked successfully")
    except InsufficientInventoryError as exc:
        typer.echo("Inventory insufficient:")
        for iid, qty in exc.missing.items():
            ing = uow.ingredients.get(iid)
            name = ing.name if ing else str(iid)
            typer.echo(f"- {name}: missing {qty}")
        raise typer.Exit(code=1)


@inv_app.command("list")
def list_inventory() -> None:
    """Display inventory items."""
    for item in uow.inventories.list():
        ing = uow.ingredients.get(item.ingredient_id)
        name = ing.name if ing else str(item.ingredient_id)
        q = item.quantity
        typer.echo(f"{name}: {q.amount}{q.unit.value}")


def main() -> None:
    setup()
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
