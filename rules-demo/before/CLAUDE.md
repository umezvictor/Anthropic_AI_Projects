# Shop service

A small order and refund service in Python.
These instructions apply to every task in this project.

## Project layout

- `shop/` holds the order logic: totals, refunds, the refund window.
- `api/` holds the HTTP routes that call the order logic.
- `db/migrations/` holds the SQL files that change the database.
- Test files sit next to the code they test, for example `shop/test_orders.py`.

## Commands

- Run all tests: `py -m pytest`
- Run one test file: `py -m pytest shop/test_orders.py`
- Check the style: `py -m ruff check .`
- Format the code: `py -m ruff format .`
- Apply the migrations to the local database: `py -m shop.migrate`

## Dependencies

- Add a new package only when the standard library cannot do the job.
- Pin every package to one version in `requirements.txt`.
- Say why you added a package in the pull request.

## Git

- One pull request makes one change.
- The pull request title says what changed, in under 70 characters.
- Never commit a secret, a token or a `.env` file.

## Before you finish a task

- Run the tests for every file you changed.
- Run the style check.
- Say which files you changed, one line each.

# Code style

These rules apply to all Python code in this project.

## Names

- Functions and variables use snake_case: `refund_order`, `order_id`.
- Classes use PascalCase: `Order`, `RefundResult`.
- Constants use UPPER_CASE: `REFUND_WINDOW_DAYS`.
- A function name starts with a verb: `get_order`, `calculate_total`.
- A boolean name reads as a question: `is_refunded`, `has_discount`.
- Do not use one-letter names, except `i` in a short loop.
- Do not shorten words: `customer`, not `cust`.

## Functions

- One function does one job.
- Keep a function under 40 lines. Split it if it grows.
- A function takes at most four arguments. Group more into a dataclass.
- Return early for the error cases. Keep the main path at the left margin.
- Do not change an argument that the caller passed in. Return a new value.

## Types

- Every function has type hints for its arguments and its return value.
- Use `list[str]` and `dict[str, int]`, not `List` and `Dict`.
- Use `X | None`, not `Optional[X]`.
- Use a dataclass for a record with fixed fields.
- Use an Enum for a fixed set of values, such as the order status.

## Money

- Store money as whole cents in an `int`. 89.90 dollars is `8990`.
- Never use `float` for money.
- Convert to dollars only when you show the amount to a person.
- Round only once, at the end of a calculation.
- Every amount has a currency. The default is USD.

## Dates and times

- Store every time in UTC.
- Use `datetime.now(timezone.utc)`, never `datetime.now()` alone.
- Convert to local time only when you show the time to a person.
- Count the refund window in whole days, from the delivery date.

## Errors

- Raise a specific exception, such as `OrderNotFound`, never a bare `Exception`.
- Catch only the exceptions you can handle.
- Never write `except:` with no exception type.
- The error message says what went wrong and what the caller can do.

## Logging

- Use the `logging` module. Never use `print` in the service code.
- Get the logger with `logger = logging.getLogger(__name__)`.
- Log the order ID with every message about an order.
- Never log a card number, an email address or a home address.
- Use `info` for normal events, `warning` for a problem the code handled,
  and `error` for a problem the code could not handle.

## Imports

- Standard library imports first, then other packages, then this project.
- One import per line.
- Do not use `from module import *`.
- Import a module, not a function, when the name is short: `import json`.

## Comments and docstrings

- Every public function has a one-line docstring that says what it returns.
- A comment explains why the code does something, not what it does.
- Delete code you do not need. Do not leave it as a comment.
- Write a TODO only with a name and a reason: `# TODO(marco): remove after the 2027 price change`.

## Files

- One module holds one topic: `orders.py`, `refunds.py`.
- Keep a file under 300 lines.
- File names use snake_case and end in `.py`.

# API rules

These rules apply to the HTTP routes in the `api/` folder.

## Routes

- Every route lives in `api/routes.py` or in a file next to it.
- Route paths use lowercase nouns and hyphens: `/orders`, `/refund-requests`.
- Use the plural noun for a collection: `/orders`, not `/order`.
- Put the ID in the path: `/orders/{order_id}`.
- Use GET to read, POST to create, PATCH to change part of a record.
- Do not use DELETE for orders. An order is never removed, only cancelled.
- A route function stays short. It checks the input, calls `shop/`, and
  returns the result. The business logic lives in `shop/`, never in `api/`.

## Versions

- Every path starts with the version: `/v1/orders`.
- Never change the shape of a response in the same version.
- A new field in a response is allowed. Removing or renaming a field needs `/v2`.
- Keep `/v1` running for six months after `/v2` goes live.

## Input

- Check every input before you call `shop/`.
- An order ID has one capital letter, a hyphen and four digits: `A-1043`.
- An amount is a positive whole number of cents.
- Reject an unknown field in the request body. Do not ignore it.
- Trim spaces from text fields before you check them.
- Limit every text field. A reason for a refund has at most 500 characters.

## Responses

- Every response body is JSON.
- Return amounts in cents, as a whole number, with a `currency` field.
- Return times in UTC, in ISO 8601 format: `2026-09-24T10:30:00Z`.
- Use the field names from `shop/`, in snake_case.
- A list response has `items` and `next_cursor`.

## Errors

- Every error uses the error contract, with these fields:
  `isError`, `errorCategory`, `isRetryable`, `message`.
- `errorCategory` is one of: `validation`, `not_found`, `business_rule`,
  `permission`, `transient`.
- `isRetryable` is true only for `transient`.
- `message` says what went wrong in one sentence a customer can read.
- Map the category to the status code:
  - `validation`: 400
  - `permission`: 403
  - `not_found`: 404
  - `business_rule`: 422
  - `transient`: 503
- Never return a Python stack trace in a response.

## Refund routes

- `POST /v1/orders/{order_id}/refunds` creates a refund.
- The request needs an `Idempotency-Key` header.
- The same key with the same body returns the first result again.
  It never creates a second refund.
- The same key with a different body returns a `validation` error.
- Keep idempotency keys for 24 hours.
- A refund outside the refund window returns a `business_rule` error.
- A refund over 500 dollars returns `202 Accepted` and goes to a person
  for review. It does not run at once.

## Security

- Every route needs a valid token, except `GET /v1/health`.
- Read the token from the `Authorization` header only.
- A customer can read only their own orders.
- A support agent can read every order and create refunds.
- Never put a token, a password or a card number in a URL.

## Limits

- A client can send 60 requests per minute.
- Over the limit, return 429 with a `Retry-After` header.
- A list route returns at most 100 items per page.
- Use a cursor for paging, never a page number.

## Logging in routes

- Log one line per request: method, path, status code, time in milliseconds.
- Add the order ID when the path has one.
- Never log the request body of a refund. It can hold a customer's note.

## Health route

- `GET /v1/health` returns 200 and `{"status": "ok"}`.
- It never calls the database or the payment provider.
- A load balancer calls it every 10 seconds, so keep it fast.

## Documentation

- Every route has a docstring. The docstring becomes the OpenAPI summary.
- List every error category the route can return.
- Add one example request and one example response.

# Testing rules

These rules apply to every test file, in any folder.

## Where tests live

- A test file sits next to the code it tests.
- `shop/orders.py` is tested in `shop/test_orders.py`.
- `api/routes.py` is tested in `api/test_routes.py`.
- A test file name starts with `test_`.
- A test function name starts with `test_` and says what it checks:
  `test_refund_is_refused_after_30_days`.

## Tools

- Use pytest. Do not use unittest classes.
- Use plain `assert`. Do not use `self.assertEqual`.
- Use `pytest.raises` to check that code raises an exception.
- Use `pytest.mark.parametrize` when one test runs with several inputs.

## What a good test looks like

- One test checks one behavior.
- A test has three parts, in this order: set up, act, check.
- Leave one empty line between the three parts.
- A test reads from top to bottom with no loops and no if statements.
- A failing test says what went wrong. Add a message to an assert when the
  values alone do not explain it.

## Test data

- Build test orders with the helper `make_order()` in `shop/testing.py`.
- Give every test its own data. A test never depends on another test.
- Use the same two customers in every test: Nadia Petrova and Marco Silva.
- Use order IDs that look real: `A-1043`, `C-3310`.
- Write amounts in cents: `8990`, not `89.90`.

## Time

- Never call the real clock in a test.
- Pass a fixed time into the code under test.
- For the refund window, test the last day inside the window and the first
  day outside it. Day 30 is inside. Day 31 is outside.

## Money

- Test a total with a discount, without a discount, and with a zero amount.
- Test that rounding happens once, at the end.
- Test a refund of the full amount and a refund of part of the amount.
- Test that a refund can never be more than the amount paid.

## The database

- Tests use a new SQLite database in memory for every test.
- Apply all migrations to that database before the test runs.
- Never connect a test to the shared development database.

## Network

- Tests never call the network.
- Replace the payment provider with the fake in `shop/fake_payments.py`.
- The fake records every call, so a test can check what was sent.

## API tests

- Test the routes through the test client, not by calling the functions.
- Check the status code and the whole response body.
- For every error category a route can return, write one test.
- Test that the same `Idempotency-Key` does not create a second refund.

## Slow tests

- A single test runs in under one second.
- Mark a slower test with `@pytest.mark.slow`, and say why in a comment.

## What not to test

- Do not test the Python standard library.
- Do not test private functions whose name starts with an underscore.
  Test them through the public function that calls them.
- Do not write a test that only repeats the code line by line.

## Before you finish

- Run the tests for the file you changed: `py -m pytest shop/test_orders.py`
- Then run all tests: `py -m pytest`
- A new function needs at least one test for the normal case and one for
  an error case.
- Never delete or skip a failing test to make the suite pass.
  Fix the code, or ask.

# Migration rules

These rules apply to the SQL files in `db/migrations/`.
A mistake here can lock the orders table or lose data, so follow every rule.

## Files

- One migration is one SQL file.
- The name starts with a four-digit number, then a short description:
  `0002_add_refund_reason.sql`.
- The next number is one more than the highest number in the folder.
- Never reuse a number, even after you delete a file.

## Never change an applied migration

- A migration that is on the main branch has run on the production database.
- Never edit it. Never rename it. Never delete it.
- To fix a mistake, write a new migration.

## One change per migration

- One migration makes one change to the database.
- Do not mix a change to a table with a change to the data in it.
- A data change goes in its own migration, after the table change.

## Adding a column

- A new column must allow NULL, or it must have a default value.
- Add a NOT NULL column in three steps, in three migrations:
  1. Add the column and allow NULL.
  2. Fill the column for the old rows.
  3. Add the NOT NULL rule.
- Money columns are `INTEGER` and hold cents.
- Time columns are `TIMESTAMP` and hold UTC.

## Removing a column

- First, remove every use of the column from the code, and release that code.
- Only then write the migration that drops the column.
- Never drop a column in the same release that stops using it.

## Renaming

- Do not rename a column or a table in one step.
- Add the new column, copy the data, move the code to the new column,
  then drop the old column. That is four releases.

## Indexes

- Add an index for every column that the code uses in a WHERE clause.
- Name the index `idx_<table>_<column>`: `idx_orders_customer_id`.
- On a large table, create the index in its own migration.

## Large tables

- The orders table has millions of rows.
- A change that rewrites the whole table can lock it for minutes.
- Before you change the orders table, check how long the change takes on a
  copy of the production data.
- Update old rows in batches of 1,000, never all at once.

## Data that must not change

- Never update or delete rows in the refunds table. A refund is a record of
  money that moved. To correct a refund, add a new row.
- Never change the amount of an order after it is paid.

## Rollback

- Every migration has a plan to undo it.
- Write the plan as a comment at the top of the file.
- If a migration cannot be undone, say so in that comment and say why.

## Review

- A migration needs a review from a second person before it merges.
- The review checks the lock time, the rollback plan and the order of the
  releases.

## Testing a migration

- Apply all migrations to an empty database: `py -m shop.migrate`.
- Run all tests after that. The tests build their database from the
  migrations, so a broken migration breaks the tests.
- Apply the new migration to a copy of the production data before you merge.

## Seed data

- Seed data for local work lives in `db/seed.sql`, not in a migration.
- Never put real customer data in a seed file.
