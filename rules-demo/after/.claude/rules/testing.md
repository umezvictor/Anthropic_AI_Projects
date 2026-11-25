---
paths:
  - "**/test_*.py"
---

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
