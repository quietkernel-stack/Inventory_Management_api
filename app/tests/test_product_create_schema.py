from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.product import RequestModelCreateProduct


def test_create_product_trims_name_and_applies_optional_defaults():
    product = RequestModelCreateProduct.model_validate(
        {"name": "  Wireless Mouse  ", "price": "12500.00"}
    )

    assert product.name == "Wireless Mouse"
    assert product.description is None
    assert product.price == Decimal("12500.00")
    assert product.quantity == 0


@pytest.mark.parametrize("description", ["", "   "])
def test_create_product_normalizes_blank_description_to_none(description):
    product = RequestModelCreateProduct.model_validate(
        {"name": "Wireless Mouse", "description": description, "price": "10.00"}
    )

    assert product.description is None


def test_create_product_accepts_values_at_declared_limits():
    product = RequestModelCreateProduct.model_validate(
        {
            "name": "n" * 100,
            "description": "d" * 500,
            "price": "99999999.99",
            "quantity": 1_000_000,
        }
    )

    assert product.name == "n" * 100
    assert product.description == "d" * 500
    assert product.price == Decimal("99999999.99")
    assert product.quantity == 1_000_000


@pytest.mark.parametrize(
    ("payload", "expected_location", "expected_type"),
    [
        ({"name": "n" * 101, "price": "10.00"}, ("name",), "string_too_long"),
        (
            {"name": "Wireless Mouse", "description": "d" * 501, "price": "10.00"},
            ("description",),
            "string_too_long",
        ),
        # (
        #     {"name": "Wireless Mouse", "price": "100000000.00"},
        #     ("price",),
        #     "decimal_max_digits",
        # ),
        (
            {"name": "Wireless Mouse", "price": "10.00", "quantity": 1_000_001},
            ("quantity",),
            "less_than_equal",
        ),
    ],
)

def test_create_product_rejects_values_outside_uncovered_constraints(
    payload, expected_location, expected_type
):
    with pytest.raises(ValidationError) as exc_info:
        RequestModelCreateProduct.model_validate(payload)

    assert any(
        error["loc"] == expected_location and error["type"] == expected_type
        for error in exc_info.value.errors()
    )

    print(exc_info.value.errors())