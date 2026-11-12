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
            WHERE is_deleted = false;
""").fetchall()
        return row