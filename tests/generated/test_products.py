# Généré par fastapi-forge — NE PAS MODIFIER : régénéré par `forge sync`.
import pytest

PREFIX = "/products"
PK_COLUMNS = ["id"]


def test_list_products(client):
    response = client.get(PREFIX, params={"limit": 5})
    assert response.status_code == 200, response.text
    body = response.json()
    assert set(body) == {"items", "total", "limit", "offset"}
    assert len(body["items"]) <= 5


def test_get_products_roundtrip(client):
    items = client.get(PREFIX, params={"limit": 1}).json()["items"]
    if not items:
        pytest.skip("table vide")
    path = PREFIX + "".join(f"/{items[0][col]}" for col in PK_COLUMNS)
    response = client.get(path)
    assert response.status_code == 200, response.text
    assert response.json() == items[0]


def test_get_missing_products_returns_404(client):
    assert client.get(PREFIX + "/00000000-0000-0000-0000-000000000000").status_code == 404
