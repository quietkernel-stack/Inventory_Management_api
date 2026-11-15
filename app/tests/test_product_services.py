from datetime import datetime

import pytest

import app.services
from app.database import pool

PRODUCT_PAYLOAD = {
    "name": "Wireless Mouse",
    "price": 12500,
    "quantity": 20
}

def test_create_product_returns_expected_response(client):
    response = client.post("/products/", json=PRODUCT_PAYLOAD)
    assert response.status_code == 201

    body = response.json()
    assert set(body) == {
        "id", "name", "description", "price", "quantity", "created_at", "message"
    }
    assert isinstance(body["id"], int)
    assert body["name"] == "Wireless Mouse"
    assert body["description"] is None
    assert body["price"] == "12500.00"
    assert body["quantity"] == 20
    assert body["message"] == "Product added successfully"
    assert datetime.fromisoformat(body["created_at"])

def test_missing_required_fields_return_structured_validation_errors(client):
    response = client.post("/products/", json={})
    assert response.status_code == 422

    body = response.json()
    assert isinstance(body["detail"], list)
    assert all(
        isinstance(error, dict) and "loc" in error and "type" in error
        for error in body["detail"]
    )
    errors_by_location = {
        tuple(error["loc"]): error["type"]
        for error in body["detail"]
    }
    assert errors_by_location == {
        ("body", "name"): "missing",
        ("body", "price"): "missing",
    }

@pytest.mark.parametrize(
    ("payload", "expected_location", "expected_type"),
    [
        (
            {"name": "   ", "price": 10, "quantity": 1},
            ("body", "name"),
            "string_too_short",
        ),
        (
            {"name": "Syringe", "price": "21.234", "quantity": 1},
            ("body", "price"),
            "decimal_max_places",
        ),
        (
            {"name": "Syringe", "price": 21, "quantity": -1},
            ("body", "quantity"),
            "greater_than_equal",
        ),
    ],
)
def test_invalid_product_fields_return_expected_validation_error(
    client, payload, expected_location, expected_type
):
    response = client.post("/products/", json=payload)
    assert response.status_code == 422

    body = response.json()
    assert isinstance(body["detail"], list)
    assert all(
        isinstance(error, dict) and "loc" in error and "type" in error
        for error in body["detail"]
    )
    assert any(
        tuple(error["loc"]) == expected_location and error["type"] == expected_type
        for error in body["detail"]
    )

def test_creating_product_adds_expected_opening_balance(client):
    response = client.post("/products/", json=PRODUCT_PAYLOAD)
    assert response.status_code == 201

    product = response.json()
    with pool.connection() as conn:
        rows = conn.execute(
            "SELECT product_id, movement_type, quantity_change, new_quantity, reason "
            "FROM stock_movements;"
        ).fetchall()

    assert len(rows) == 1
    row = rows[0]
    assert row[0] == product["id"]
    assert row[1] == "opening balance"
    assert row[2] == product["quantity"]
    assert row[3] == product["quantity"]
    assert row[4] == "Initial product entry"


def failing_movement(*args, **kwargs):
    raise RuntimeError("Simulated database failure")

def test_transaction_rolls_back(client, monkeypatch):
    monkeypatch.setattr(
        app.services,
        "add_stock_movement",
        failing_movement
    )
    response = client.post("/products/", json=PRODUCT_PAYLOAD)
    assert response.status_code == 500

    with pool.connection() as conn:
        product_count = conn.execute(
            "SELECT COUNT(*) FROM products;"
        ).fetchone()[0] # type: ignore
        movement_count = conn.execute(
            "SELECT COUNT(*) FROM stock_movements;"
        ).fetchone()[0] # type: ignore

    assert product_count == 0
    assert movement_count == 0

@pytest.fixture
def created_product(client):
    response = client.post("/products/", json=PRODUCT_PAYLOAD)
    assert response.status_code == 201
    return response.json()

def test_retrieve_product_by_id_returns_expected_response(client, created_product):
    response = client.get(f"/products/{created_product['id']}")
    assert response.status_code == 200

    body = response.json()
    assert set(body) == {
        "id", "name", "description", "price", "quantity", "created_at"
    }
    assert body["id"] == created_product["id"]
    assert body["name"] == "Wireless Mouse"
    assert body["description"] is None
    assert body["price"] == "12500.00"
    assert body["quantity"] == 20
    assert body["created_at"] == created_product["created_at"]

def test_retrieve_missing_product_returns_404(client, created_product):
    missing_product_id = -1
    response = client.get(f"/products/{missing_product_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}
