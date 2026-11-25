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

## More rules

More rules live in `.claude/rules/`, one file per topic.
Some of them load only when you work with matching files.
