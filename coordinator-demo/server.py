"""A small refunds server for the demo. One tool: refund_order."""

from datetime import date, timedelta

from mcp.server import MCPServer
from error_contract import unknown_order, outside_refund_window

mcp = MCPServer("refunds")

REFUND_WINDOW_DAYS = 30

TODAY = date.today()

# The shop database, for this demo. Two orders, and one of them is old.
ORDERS = {
    "A-1043": {
        "customer": "Nadia Petrova",
        "amount_eur": 89.90,
        "shipped": TODAY - timedelta(days=8),
    },
    "B-2277": {
        "customer": "Tomas Lind",
        "amount_eur": 142.50,
        "shipped": TODAY - timedelta(days=74),
    },
}


@mcp.tool()
def refund_order(order_id: str) -> str:
    """Refund one order from the shop database and return what was refunded.

    Use it when a customer asks for their money back on a specific order.
    The shop refunds an order only inside the refund window, counted from the
    day the order shipped. Pass the order ID exactly as the customer gives it,
    for example A-1043.
    """
    order = ORDERS.get(order_id)

    if order is None:
        unknown_order(order_id)

    days_since_shipping = (TODAY - order["shipped"]).days
    if days_since_shipping > REFUND_WINDOW_DAYS:
        outside_refund_window(order_id, days_since_shipping, REFUND_WINDOW_DAYS)

    return (
        "Refunded "
        + str(order["amount_eur"])
        + " euro for order "
        + order_id
        + " to "
        + order["customer"]
        + "."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
