from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.product import RequestModelUpdateProduct


@pytest.mark.parametrize(
    ("payload", "expected_values"),
    [
        ({"name": "  Updated Mouse  "}, {"name": "Updated Mouse"}),
        (
            {"description": "Updated product description"},
            {"description": "Updated product description"},
        ),
        ({"price": "12500.50"}, {"price": Decimal("12500.50")}),
    ],
)
def test_update_product_accepts_valid_partial_updates(payload, expected_values):
    update = RequestModelUpdateProduct.model_validate(payload)

    assert update.model_dump(exclude_unset=True) == expected_values
    assert update.model_fields_set == set(expected_values)


def test_update_product_accepts_explicit_null_description():
    update = RequestModelUpdateProduct.model_validate({"description": None})

    assert update.description is None
    assert update.model_fields_set == {"description"}
    assert update.model_dump(exclude_unset=True) == {"description": None}


def test_update_product_rejects_empty_payload():
    with pytest.raises(ValidationError) as exc_info:
        RequestModelUpdateProduct.model_validate({})

    assert any(
        error["loc"] == () and error["type"] == "value_error"
        for error in exc_info.value.errors()
    )


def test_update_product_rejects_quantity_field():
    with pytest.raises(ValidationError) as exc_info:
        RequestModelUpdateProduct.model_validate({"quantity": 1})

    assert any(
        error["loc"] == ("quantity",) and error["type"] == "extra_forbidden"
        for error in exc_info.value.errors()
    )


@pytest.mark.parametrize(
    ("payload", "expected_location", "expected_type"),
    [
        ({"name": "   "}, ("name",), "string_too_short"),
        ({"description": "   "}, ("description",), "string_too_short"),
        ({"price": "-0.01"}, ("price",), "greater_than_equal"),
        ({"price": "10.001"}, ("price",), "decimal_max_places"),
    ],
)
def test_update_product_rejects_invalid_field_values(
    payload, expected_location, expected_type
):
    with pytest.raises(ValidationError) as exc_info:
        RequestModelUpdateProduct.model_validate(payload)

    assert any(
        error["loc"] == expected_location and error["type"] == expected_type
        for error in exc_info.value.errors()
    )
