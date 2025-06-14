from domain.shared.value_objects import Difficulty, Quantity
from domain.recipe.models import Recipe, RecipeIngredient

def test_recipe_create_and_update_notes():
    r = Recipe(
        id="r1",
        name="西红柿鸡蛋面",
        category="主食",
        method="煮",
        difficulty=Difficulty.EASY,
        duration_min=20,
        duration_max=30,
        ingredients=[
            RecipeIngredient("tomato", Quantity(1, "个")),
            RecipeIngredient("egg", Quantity(2, "个")),
        ],
    )
    assert r.notes is None
    r.update_notes("加点葱花更香")
    assert r.notes == "加点葱花更香"
