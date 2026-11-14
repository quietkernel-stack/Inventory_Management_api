# Inventory Management API

A REST API for managing products and recording their opening inventory balance. The project uses FastAPI, PostgreSQL, Psycopg, SQLAlchemy Core, Alembic, and pytest.

## Current capabilities

- Create a product with a validated name, optional description, price, and initial quantity.
- Record an `opening balance` stock movement whenever a product is created.
- Retrieve one active product by ID.
- List active products.
- Keep product creation and opening-movement insertion in one database transaction.
- Protect the test database setup from running against a database other than `inventory_test`.

Features such as product updates, soft deletion, stock-movement APIs, and movement history are not implemented yet. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the current development status.

## Technology stack

- Python 3.13 or later
- FastAPI
- PostgreSQL
- Psycopg 3 and Psycopg connection pooling
- SQLAlchemy Core metadata
- Alembic migrations
- Pydantic and pydantic-settings
- pytest and FastAPI's test client
- uv, using the committed `uv.lock` file

## Prerequisites

- Python 3.13+
- PostgreSQL
- [uv](https://docs.astral.sh/uv/)

Create two PostgreSQL databases before applying migrations:

```sql
CREATE DATABASE inventory_db;
CREATE DATABASE inventory_test;
```

`inventory_test` is reserved for automated tests. The test fixtures truncate its application tables before every test.

## Setup

Install all application, test, and development dependencies from the lockfile:

```powershell
uv sync --all-groups
```

Create the local environment file:

```powershell
Copy-Item .env.example .env
```

Set the database connection values in `.env`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/inventory_db
TEST_DATABASE_URL=postgresql://username:password@localhost:5432/inventory_test
```

`APP_NAME` and `DEBUG` are optional settings. Both `DATABASE_URL` and `TEST_DATABASE_URL` are required by the current settings model, including when starting the normal application.

## Database and migrations

Alembic chooses a database with `-x environment=...`:

```powershell
# Application database
uv run alembic -x environment=app upgrade head

# Test database
uv run alembic -x environment=test upgrade head
```

The migration environment rejects a test URL whose database name is not exactly `inventory_test`.

The current schema contains:

- `products`: product details, current quantity, soft-delete flag, and timestamps. Database checks prevent negative prices and quantities.
- `stock_movements`: movement details linked to a product. Its foreign key uses `ON DELETE RESTRICT`.

## Run the application

```powershell
uv run uvicorn app.main:app --reload
```

The API is served at `http://127.0.0.1:8000`; interactive documentation is at `/docs`.

## API endpoints

### Create a product

`POST /products/`

```json
{
  "name": "Wireless Mouse",
  "description": "Wireless optical mouse",
  "price": "12500.00",
  "quantity": 20
}
```

Rules:

- `name` is required, trimmed, and must contain 1–100 characters.
- `description` is optional; blank or whitespace-only input becomes `null`; non-blank input is limited to 500 characters.
- `price` is required, non-negative, has up to 10 total digits and 2 decimal places.
- `quantity` defaults to `0` and must be an integer from `0` to `1,000,000`.

Successful requests return `201 Created` and a product response with `id`, `name`, `description`, `price`, `quantity`, `created_at`, and `message`. Creation also writes one opening-balance movement in the same transaction.

### Retrieve a product

`GET /products/{id}`

Returns an active product with `200 OK`, or `404` with `{"detail": "Product not found"}`.

### List products

`GET /products/`

Returns `200 OK` with:

```json
{
  "Inventory": [
    {
      "id": 1001,
      "name": "Wireless Mouse",
      "description": "Wireless optical mouse",
      "price": "12500.00",
      "quantity": 20,
      "created_at": "2026-01-01T12:00:00+00:00"
    }
  ]
}
```

When no active products exist, the current implementation instead returns `404` with `{"detail": "No products available"}`.

## Tests

Apply migrations to `inventory_test` first, then run:

```powershell
uv run pytest
```

The test suite validates its configured URL and its live connection before truncating data. Never point `TEST_DATABASE_URL` at a database containing data you need.

Current coverage includes product creation, request validation, opening-balance creation, transaction rollback, product retrieval, and database-safety checks. Product-listing coverage has not yet been added.

## Repository guide

- `app/routers/`: HTTP endpoints and HTTP-level errors.
- `app/services.py`: transaction boundary and product-creation workflow.
- `app/repositories/`: SQL statements executed with Psycopg.
- `app/schemas/`: Pydantic request and response schemas.
- `models.py`: SQLAlchemy Core metadata for migrations.
- `migrations/`: Alembic migration scripts and environment selection.
- `app/tests/`: pytest tests and test database fixtures.

For contributor and agent guidance, read [AGENTS.md](AGENTS.md).
