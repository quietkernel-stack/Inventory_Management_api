from psycopg.rows import dict_row

def create_initial_product (connection, name, description, price, quantity):
    with connection.cursor(row_factory=dict_row) as cur:
        row = cur.execute("""
            INSERT INTO products (name, description, price, quantity)
            VALUES (%s, %s, %s, %s)
            RETURNING *;
""", (name, description, price, quantity)).fetchone()
        return row

def retreive_product_details_by_id(connection, id):
    with connection.cursor(row_factory=dict_row) as cur:
        row = cur.execute("""
            SELECT * FROM products
            WHERE id = %s and is_deleted = false;
""", (id,)).fetchone()
        return row
    
def get_products_collectively(connection):
    with connection.cursor(row_factory=dict_row) as cur:
        row = cur.execute("""
            SELECT * FROM products
            WHERE is_deleted = false
            ORDER BY id ASC;
""").fetchall()
        return row

def update_product_details(connection, set_clause, values):
    query = f"""
        UPDATE products
        SET {set_clause}, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND is_deleted = false
        RETURNING *;
"""
    with connection.cursor(row_factory=dict_row) as cur:
        row = cur.execute(query, values).fetchone()
        return row
