"""Order totals and the refund window."""

from dataclasses import dataclass
from datetime import datetime

REFUND_WINDOW_DAYS = 30


@dataclass
class Order:
    order_id: str
    customer: str
    amount_cents: int
    delivered_at: datetime


def can_refund(order: Order, now: datetime) -> bool:
    """Return True if the order is still inside the refund window."""
    days = (now - order.delivered_at).days
    return days <= REFUND_WINDOW_DAYS


def calculate_total(line_cents: list[int], discount_cents: int = 0) -> int:
    """Return the order total in cents, after the discount."""
    total = sum(line_cents) - discount_cents
    return max(total, 0)
