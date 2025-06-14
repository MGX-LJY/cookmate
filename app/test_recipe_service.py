from adapters.repo_memory.recipe_repo import InMemoryRecipeRepository
from app.recipe_service import RecipeService
from domain.recipe.models import Recipe
from domain.recipe.models import RecipeIngredient
from domain.shared.value_objects import Difficulty, Quantity


def test_recipe_service_upsert_and_get():
    repo = InMemoryRecipeRepository()
    service = RecipeService(repo)

    r = Recipe(
        id="r1",
        name="可乐鸡翅",
        category="主菜",
        method="煮",
        difficulty=Difficulty.MEDIUM,
        duration_min=30,
        duration_max=40,
        ingredients=[RecipeIngredient("chicken_wing", Quantity(6, "只"))],
    )

    service.upsert(r)
    fetched = service.get("r1")

    assert fetched is not None
    assert fetched.name == "可乐鸡翅"
    assert len(list(service.list_all())) == 1
