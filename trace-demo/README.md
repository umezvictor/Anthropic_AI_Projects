# Trace One Function Across A Codebase

A small billing project. Nothing here runs, and nothing needs to be installed
except Claude Code. You only read and search.

Put the files in a short folder and open a session there:

```
cd "D:\trace-demo"
claude
```

## The files

| File | What is in it |
| --- | --- |
| `orders.py` | Defines `calculate_total`, and calls it once in `order_summary`. |
| `invoices.py` | Calls `calculate_total`, and writes its name inside a log message. |
| `api.py` | Imports `calculate_total`, lists it in `__all__`, and calls it once in `quote`. |
| `reports.py` | Defines `recalculate_total`, a different function with a similar name. |
| `tests/test_orders.py` | Two tests that call `calculate_total`. |

## What to ask

```
Trace calculate_total in this project. Where is it defined, where is it called, and what breaks if I add a parameter?
```

Then, for the pattern rule:

```
Search with this exact pattern, do not change it: calculate_total(
```

## The pattern rule

Claude Code searches file contents with ripgrep. A pattern is a regular
expression, so a bracket, a dot, a star or a question mark carries a special
meaning. To search for one of those characters as text, put a backslash before
it: `calculate_total\(`
