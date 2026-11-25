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
