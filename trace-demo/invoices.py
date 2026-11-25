"""Invoices. This file calls calculate_total when it builds an invoice."""

import logging

from orders import calculate_total

log = logging.getLogger("invoices")


def build_invoice(order, customer):
    """Build one invoice for one order."""
    try:
        total = calculate_total(order["lines"], order.get("discount", 0.0))
    except KeyError:
        log.error("calculate_total failed for order %s", order["id"])
        raise

    return {
        "invoice_id": "INV-" + order["id"],
        "customer": customer,
        "total": total,
    }
