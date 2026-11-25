---
paths:
  - "db/migrations/**"
---

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
