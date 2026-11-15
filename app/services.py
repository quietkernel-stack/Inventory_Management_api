from app.repositories.product_repo import create_initial_product, update_product_details
from app.repositories.stock_movement_repo import add_stock_movement
from app.schemas.stock_movement import MovementType


def new_product(connection, name, description, price, quantity):
    with connection.transaction():
        product = create_initial_product(
            connection,
            name,
            description,
            price,
            quantity
        )
        
        add_stock_movement(
            connection,
            product["id"],
            MovementType.OPENING_BALANCE,
            product["quantity"],
            product["quantity"],
            "Initial product entry"
        )
        
        return product

def update_product(connection, product_id: int, update_data: dict):
    allowed_fields = {
        "name",
        "description",
        "price"
        }

    data = {k : v for k, v in update_data.items() if k in allowed_fields}
    if not data:
        return None

    set_clause = ", ".join(f"{k} = %s" for k in data)
    values = list(data.values())
    values.append(product_id)

    updated_product = update_product_details(
        connection,
        set_clause,
        values
    )

    return updated_product