# Return A Classified Error From The Server You Just Shared

This demo continues the refunds server from the previous hands-on lecture. Same
folder, same `.mcp.json`, same tool. Only the failures change.

Copy `error_contract.py` into your demo folder, next to `server.py`.

If you no longer have that folder, this download also holds `server.py` in its
starting state, and `SETUP.md` from the previous lecture lists what to install.

## What is wrong today

`server.py` answers both failures with a short code:

- `Refund failed. ERR_4041.` when the order ID is unknown
- `Refund failed. ERR_4021.` when the order shipped outside the 30 day window

Both come back as a normal, successful result. The agent has no way to see that
the call failed, and the code says nothing it can act on.

## The three edits

**1. At the top of `server.py`, next to the other imports:**

```python
from error_contract import unknown_order, outside_refund_window
```

**2. Replace the unknown order line:**

```python
    if order is None:
        unknown_order(order_id)
```

**3. Replace the refund window line:**

```python
    if days_since_shipping > REFUND_WINDOW_DAYS:
        outside_refund_window(order_id, days_since_shipping, REFUND_WINDOW_DAYS)
```

Save the file. Then, inside the session, open `/mcp`, select refunds, and choose
Reconnect, so the server starts again with your new code.

## Try it

Order B-2277 shipped 74 days ago, so it is outside the window.

```
Refund order B-2277.
```

Ask once before the edits, and once after them.

## Sources

- https://modelcontextprotocol.io/specification/2026-07-28/server/tools
- https://py.sdk.modelcontextprotocol.io/servers/handling-errors/
