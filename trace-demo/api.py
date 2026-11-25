"""The public surface of the billing package."""

from invoices import build_invoice
from orders import calculate_total, order_summary

__all__ = ["calculate_total", "order_summary", "build_invoice"]


def quote(lines):
    """A quote is the total of the lines, with no discount."""
    return calculate_total(lines)
