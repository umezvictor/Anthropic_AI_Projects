---
paths:
  - "api/**"
---

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
