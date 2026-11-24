from enum import Enum
from pydantic import BaseModel, Field, StringConstraints, ConfigDict, field_validator
from typing import Annotated

class MovementType(str, Enum):
    RECEIPT = "receipt"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    DAMAGE = "damage"
    OPENING_BALANCE = "opening balance"

NonEmptystr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=250)]

class RequestModelStockAdjustment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantity_change: int
    reason: NonEmptystr

    @field_validator("quantity_change")
    @classmethod
    def validate_quantity_change(cls, value):
        if value == 0:
            raise ValueError("Quantity change cannot be zero.")

        return value