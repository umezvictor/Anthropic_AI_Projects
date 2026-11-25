from datetime import datetime, timezone

from api.routes import post_refund
from shop.orders import Order

DELIVERED = datetime(2026, 9, 1, tzinfo=timezone.utc)
NOW = datetime(2026, 9, 10, tzinfo=timezone.utc)


def test_bad_order_id_is_a_validation_error():
    order = Order("A-1043", "Nadia Petrova", 8990, DELIVERED)

    body = post_refund(order, "a1043", NOW)

    assert body["errorCategory"] == "validation"


def test_refund_inside_the_window():
    order = Order("A-1043", "Nadia Petrova", 8990, DELIVERED)

    body = post_refund(order, "A-1043", NOW)

    assert body["refunded_cents"] == 8990
