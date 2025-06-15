import pytest
try:
    from fastapi.testclient import TestClient
except Exception:  # pragma: no cover - fastapi missing
    TestClient = None  # type: ignore

if TestClient is None:  # pragma: no cover - skip when FastAPI unavailable
    pytest.skip("fastapi not installed", allow_module_level=True)

from web.api.main import create_app
from web.api.deps import get_uow
from app.unit_of_work import MemoryUnitOfWork
from domain.ingredient.models import Ingredient
from domain.inventory.models import InventoryItem
from domain.shared.value_objects import Quantity, Unit


def _prepare_uow():
    uow = MemoryUnitOfWork()
    egg = Ingredient(name="鸡蛋", default_unit=Unit.PIECE)
    tomato = Ingredient(name="西红柿", default_unit=Unit.GRAM)
    uow.ingredients.add(egg)
    uow.ingredients.add(tomato)
    uow.inventories.add_or_update(
        InventoryItem(ingredient_id=egg.id, quantity=Quantity.of(4, Unit.PIECE))
    )
    uow.inventories.add_or_update(
        InventoryItem(ingredient_id=tomato.id, quantity=Quantity.of(500, Unit.GRAM))
    )
    return uow


@pytest.fixture()
def client():
    uow = _prepare_uow()
    app = create_app()

    def override_uow():
        yield uow

    app.dependency_overrides[get_uow] = override_uow
    with TestClient(app) as c:
        yield c


def test_ping(client):
    resp = client.get("/ping")
    assert resp.status_code == 200
    assert resp.json() == {"msg": "pong"}


def test_recipe_endpoints(client):
    data = {
        "name": "番茄炒蛋",
        "ingredients": {"鸡蛋": [2, ""], "西红柿": [300, "g"]},
        "steps": ["打蛋", "热锅"],
        "category": "主菜",
        "method": "炒",
        "difficulty": "中",
        "pairing": "米饭",
        "time_minutes": "10-15min",
        "notes": "小火慢炒",
        "tutorial": "http://example.com",
        "cover": "http://img.example.com/egg.jpg",
    }
    resp = client.post("/recipes/", json=data)
    assert resp.status_code == 201

    resp = client.patch("/recipes/番茄炒蛋/difficulty", json={"value": "中高"})
    assert resp.status_code == 200

    resp = client.get("/recipes/番茄炒蛋")
    assert resp.status_code == 200
    assert resp.json()["metadata"]["difficulty"] == "中高"
    assert resp.json()["metadata"]["cover"] == "http://img.example.com/egg.jpg"

    resp = client.patch("/recipes/番茄炒蛋/notes", json={"value": "加点糖"})
    assert resp.status_code == 200

    resp = client.patch("/recipes/番茄炒蛋/cover", json={"value": "http://img.example.com/new.jpg"})
    assert resp.status_code == 200

    resp = client.get("/recipes/番茄炒蛋")
    assert resp.json()["metadata"]["cover"] == "http://img.example.com/new.jpg"

    resp = client.patch(
        "/recipes/番茄炒蛋/ingredients",
        json={"ingredients": {"鸡蛋": [3, ""], "西红柿": [400, "g"]}},
    )
    assert resp.status_code == 200

    resp = client.get("/recipes/")
    assert resp.status_code == 200
    assert resp.json() == ["番茄炒蛋"]

    resp = client.delete("/recipes/番茄炒蛋")
    assert resp.status_code == 204
    resp = client.get("/recipes/")
    assert resp.json() == []


def test_inventory_endpoints(client):
    resp = client.get("/inventory/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2

    resp = client.post(
        "/inventory/",
        json={"ingredient": "鸡蛋", "amount": 10, "unit": "pcs"},
    )
    assert resp.status_code == 201
    resp = client.get("/inventory/")
    amounts = {item["ingredient"]: item["amount"] for item in resp.json()}
    assert amounts["鸡蛋"] == 10.0

    resp = client.delete("/inventory/鸡蛋")
    assert resp.status_code == 204
    resp = client.get("/inventory/")
    names = [item["ingredient"] for item in resp.json()]
    assert "鸡蛋" not in names


def test_planner_endpoints(client):
    # create two recipes
    r1 = client.post(
        "/recipes/",
        json={
            "name": "菜1",
            "ingredients": {"鸡蛋": [2, ""], "西红柿": [300, "g"]},
            "steps": ["s1"],
        },
    ).json()["id"]
    r2 = client.post(
        "/recipes/",
        json={
            "name": "菜2",
            "ingredients": {"鸡蛋": [5, ""]},
            "steps": ["s"],
        },
    ).json()["id"]

    resp = client.get("/planner/cookable")
    assert resp.status_code == 200
    assert resp.json() == ["菜1"]

    resp = client.post(
        "/planner/shopping",
        json={"recipes": {r1: 2, r2: 0}},
    )
    assert resp.status_code == 200
    assert resp.json() == [{"ingredient": "西红柿", "amount": 100.0, "unit": "g"}]
