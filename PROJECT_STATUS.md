# Project Status

## Implementation status

The application is in an early product-inventory stage. It supports creating products and recording their opening balances, plus basic retrieval of active products. The current design uses a FastAPI router, a service-layer transaction, Psycopg repositories, PostgreSQL, and Alembic migrations.

## Implemented endpoints

| Endpoint | Status | Behavior |
| --- | --- | --- |
| `POST /products/` | Implemented | Validates and creates a product, then records one `opening balance` stock movement in the same transaction. Returns `201`. |
| `GET /products/{id}` | Implemented | Returns a non-deleted product or `404 Product not found`. |
| `GET /products/` | Implemented | Returns non-deleted products under `Inventory`; returns `404 No products available` when none exist. |

## Implemented data behavior

- Product price and quantity are constrained to non-negative values in the database.
- Product creation accepts quantity from 0 through 1,000,000 and defaults it to 0.
- Creation always inserts an opening movement, including for zero quantity.
- The opening movement uses `opening balance`, with `quantity_change` and `new_quantity` equal to the product's initial quantity.
- Product reads exclude rows where `is_deleted` is true.
- A product with stock movements cannot be hard-deleted because the movement foreign key uses `ON DELETE RESTRICT`.

## Current test coverage

| Area | Coverage status |
| --- | --- |
| Test database URL safety | Covered: accepts only `inventory_test` as the configured test database name. |
| Live test database safety | Used by fixture cleanup; no direct test currently covers the live-connection validation function. |
| Product creation response | Covered: status, response fields, core values, generated ID type, timestamp format, and success message. |
| Request validation | Covered: missing name/price and individual invalid name, price precision, and quantity cases. |
| Opening stock movement | Covered: exactly one movement with expected product ID, type, quantities, and reason. |
| Transaction rollback | Covered with a mocked movement-write failure; asserts no products or movements remain. |
| Product detail retrieval | Covered for successful retrieval and missing-product `404`. |
| Product listing | Not covered. |
| Database constraints and migrations | Not covered directly. |

The tests use a real PostgreSQL test database and truncate both application tables before each test. Apply the test migrations before running them.

## Known limitations

- No API endpoints exist for stock movements or movement history; `app/routers/stock_movements.py` is empty.
- No product update endpoint exists.
- No soft-delete endpoint exists, even though `is_deleted` is present and reads filter it.
- `updated_at` is set on creation but is not automatically maintained on future updates.
- `movement_type` is free text in the database; the application enum is not enforced by a database constraint.
- The database does not enforce a relationship between `quantity_change`, `new_quantity`, and a product's recorded quantity.
- The product-listing query has no explicit ordering.
- An empty inventory currently produces `404`, not `200` with an empty list.
- Settings require `TEST_DATABASE_URL` even when starting the non-test application.

## Recommended next tasks

1. Add tests for `GET /products/`, including populated and empty inventory behavior.
2. Add boundary tests for name length/whitespace, description normalization and limits, price limits, and quantity limits.
3. Decide and document whether an empty inventory should return `404` or `200` with an empty collection.
4. Add direct tests for migration/schema constraints, including `ON DELETE RESTRICT`.
5. Design stock-movement operations and history before adding routes; define allowed movement types and quantity-invariant rules.
6. Implement and test product updates, including how updates create adjustment movements and maintain `updated_at`.
7. Design and implement soft deletion, including inventory rules and movement-history effects.
