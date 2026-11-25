"""Refunds for the shop."""

from shop.orders import ORDERS

# Order ID and the dollars already refunded for it.
REFUNDED = {}


def check_amount(amount, remaining):
    """Validate a partial refund amount against what is left to refund.

    Return the amount if it is valid, otherwise raise ValueError.
    """
    if amount <= 0:
        raise ValueError(f"Refund amount must be positive, got {amount}")
    if amount > remaining:
        raise ValueError(
            f"Refund amount {amount} is more than the {remaining} left to refund"
        )
    return amount


def refund_order(order_id, amount=None):
    """Refund an order, fully or partially. Return the amount refunded.

    With no amount, refund everything still left on the order. With an
    amount, refund that part. Several partial refunds are allowed until
    the order total is reached.
    """
    if order_id not in ORDERS:
        raise ValueError(f"Unknown order: {order_id}")
    total = ORDERS[order_id]["total"]
    already = REFUNDED.get(order_id, 0)
    remaining = round(total - already, 2)
    if remaining <= 0:
        raise ValueError(f"Order {order_id} is already fully refunded")
    if amount is None:
        amount = remaining
    else:
        amount = check_amount(amount, remaining)
    REFUNDED[order_id] = round(already + amount, 2)
    return amount
