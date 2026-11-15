from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.product import ResponseModelGetProducts


PRODUCT_DETAILS = {
    "id": 1001,
    "name": "Wireless Mouse",
    "description": "Wireless optical mouse",
    "price": "12500.00",
    "quantity": 20,
    "created_at": "2026-01-01T12:00:00+00:00",
}


def test_product_list_response_parses_nested_product_details():
    response = ResponseModelGetProducts.model_validate({"Inventory": [PRODUCT_DETAILS]})

    product = response.Inventory[0]
    assert product.id == 1001
    assert product.price == Decimal("12500.00")
    assert product.created_at == datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


# def test_product_list_response_rejects_invalid_nested_product_details():
#     invalid_product = {**PRODUCT_DETAILS, "price": "10.001"}

#     with pytest.raises(ValidationError) as exc_info:
#         ResponseModelGetProducts.model_validate({"Inventory": [invalid_product]})

#     assert any(
#         error["loc"] == ("Inventory", 0, "price")
#         and error["type"] == "decimal_max_places"
#         for error in exc_info.value.errors()
#     )
