"""HTTP routes for orders. Each route checks the input and calls shop/."""

import re

from shop.orders import Order, can_refund

ORDER_ID = re.compile(r"^[A-Z]-\d{4}$")


def error(category: str, message: str) -> dict:
    """Return an error body in the shape of the error contract."""
    return {
        "isError": True,
        "errorCategory": category,
        "isRetryable": category == "transient",
        "message": message,
    }


def post_refund(order: Order, order_id: str, now) -> dict:
    """POST /v1/orders/{order_id}/refunds: refund one order."""
    if not ORDER_ID.match(order_id):
        return error("validation", "The order ID must look like A-1043.")
    if not can_refund(order, now):
        return error("business_rule", "This order is outside the refund window.")
    return {"order_id": order_id, "refunded_cents": order.amount_cents, "currency": "USD"}
