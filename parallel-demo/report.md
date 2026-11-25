# Review of review_me.py

## Security

- API_KEY: Live API key is hardcoded in the source.
- SESSION_TOKEN: Admin session token is hardcoded in the source.
- find_order: order_id is concatenated into the SQL string, which allows SQL injection.

## Correctness

- verify_token: an empty or None token returns True, so a caller with no token is authenticated.
- split_full_name: a single-word name makes parts[1] raise IndexError, and double spaces between words return an empty string as the last name.
- merge_orders: it calls orders.remove while looping over the same list, so the element after each removed one is skipped and consecutive cancelled orders stay in.

## Performance

- find_duplicates: Nested loop over all index pairs is O(n^2) with a list membership check on top, so use a Counter or a seen set instead.
- get_customer_names: Opens a new database connection and runs one query per order id, so reuse one connection and fetch all ids with a single IN query.
