# Contributor and Agent Guide

## Start with inspection

Before proposing or making a change, inspect the relevant router, schema, service, repository, migration, configuration, and tests. Treat the implementation as the source of truth when documentation and code differ. State assumptions and identify behavior that needs runtime verification.

Do not infer unimplemented functionality from filenames, models, enums, or planned work. In particular, the stock-movement router is currently empty and is not registered with the FastAPI application.

## Architecture and layer responsibilities

The application has a small layered architecture:

1. `app/main.py` creates FastAPI, opens and closes the shared Psycopg pool through the lifespan hook, and registers routers.
2. `app/routers/` owns HTTP routing, dependency injection, request/response schemas, and HTTP exceptions.
3. `app/services.py` owns business workflows and transaction boundaries. `new_product` creates the product and its opening movement in one transaction.
4. `app/repositories/` owns parameterized SQL and database reads/writes. Repositories should not make HTTP decisions.
5. `app/schemas/` contains Pydantic request and response models.
6. `models.py` contains SQLAlchemy Core table metadata used as Alembic's migration metadata. It is not an ORM model layer.
7. `migrations/` contains Alembic revisions and migration-environment selection.

Keep responsibilities at their existing layer when changing the application. Do not move SQL into routers or HTTP response decisions into repositories.

## Technology and implementation conventions

- Python 3.13+ is required by `pyproject.toml`.
- The repository is locked with `uv.lock`; use `uv` commands for installation and execution unless the task explicitly asks for another workflow.
- PostgreSQL access uses Psycopg 3 and a shared `ConnectionPool` in `app/database.py`.
- Repository SQL must remain parameterized; do not interpolate user input into SQL strings.
- Pydantic schemas validate HTTP input and shape HTTP output. Preserve their declared constraints when adding tests or routes.
- Product reads filter `is_deleted = false`; no product soft-delete workflow is implemented yet.
- Product creation writes an `opening balance` movement with matching initial and resulting quantities. Preserve its transaction boundary.

## Database and migration conventions

- Define schema metadata in `models.py`; generate or write matching Alembic revisions under `migrations/versions/` for schema changes.
- Use `uv run alembic -x environment=app upgrade head` for the application database.
- Use `uv run alembic -x environment=test upgrade head` for the test database.
- `migrations/env.py` selects the URL from `DATABASE_URL` or `TEST_DATABASE_URL`; do not rely on the placeholder `sqlalchemy.url` in `alembic.ini`.
- The test migration environment requires the target database name to be exactly `inventory_test`.
- Current database guarantees include non-negative product price/quantity and `ON DELETE RESTRICT` from `stock_movements.product_id` to `products.id`.

## Testing conventions and database safety

- Tests live in `app/tests/` and use FastAPI's `TestClient` with the real PostgreSQL test database.
- `app/tests/conftest.py` verifies `TEST_DATABASE_URL`, redirects the app pool to it, and truncates `stock_movements` and `products` before every test.
- The cleanup is destructive. Never point `TEST_DATABASE_URL` at a database with data that must be retained.
- Test validation responses through FastAPI's `detail` list: assert the status code, field location (`loc`), and error type. Avoid brittle exact error-message checks unless the message is part of the application contract.
- Use the canonical trailing-slash routes (`/products/`) in endpoint tests.
- Prefer response-derived IDs over reset-sequence or arbitrary ID assumptions.
- For transaction tests, assert the intended persistence outcome in both `products` and `stock_movements`.
- Before adding tests, identify the implementation behavior and edge cases being tested. Do not change production behavior merely to satisfy a test unless the task explicitly authorizes it.

## Workflow boundaries

- If asked to work only on tests, do not modify production code, configuration, migrations, dependencies, or documentation without explicit permission.
- If asked to diagnose or review, do not implement a fix unless asked.
- Do not commit, push, merge, or modify remote repositories without explicit permission.
- Keep edits within the files the user has authorized. Ask before widening that scope.
- Run the narrowest relevant verification command when the local environment supports it, and report anything that prevented verification.
