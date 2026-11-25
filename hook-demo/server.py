"""A small refunds server for the demo. Two tools: refund_order and escalate_to_human."""

from datetime import date, timedelta

from mcp.server import MCPServer
from error_contract import unknown_order, outside_refund_window

mcp = MCPServer("refunds")

REFUND_WINDOW_DAYS = 30

TODAY = date.today()

# The shop database, for this demo. Two orders, both inside the refund window.
ORDERS = {
    "A-1043": {
        "customer": "Nadia Petrova",
        "amount_usd": 89.90,
        "shipped": TODAY - timedelta(days=8),
    },
    "C-3310": {
        "customer": "Marco Silva",
        "amount_usd": 900.00,
        "shipped": TODAY - timedelta(days=5),
    },
}


@mcp.tool()
def refund_order(order_id: str, amount_usd: float) -> str:
    """Refund one order from the shop database and return what was refunded.

    Use it when a customer asks for their money back on a specific order.
    Pass the order ID exactly as the customer gives it, for example A-1043,
    and the amount to refund in US dollars.
    """
    order = ORDERS.get(order_id)

    if order is None:
        unknown_order(order_id)

    days_since_shipping = (TODAY - order["shipped"]).days
    if days_since_shipping > REFUND_WINDOW_DAYS:
        outside_refund_window(order_id, days_since_shipping, REFUND_WINDOW_DAYS)

    return (
        "Refunded "
        + format(amount_usd, ".2f")
        + " dollars for order "
        + order_id
        + " to "
        + order["customer"]
        + "."
    )


@mcp.tool()
def escalate_to_human(order_id: str, amount_usd: float, reason: str) -> str:
    """Send one refund to the human review queue instead of refunding it.

    Use it when a refund needs a decision from a person.
    """
    return (
        "Order "
        + order_id
        + ", "
        + format(amount_usd, ".2f")
        + " dollars, is in the human review queue. Reason: "
        + reason
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
