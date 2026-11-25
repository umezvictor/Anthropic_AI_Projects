from datetime import datetime, timedelta, timezone

from shop.orders import Order, calculate_total, can_refund

DELIVERED = datetime(2026, 9, 1, tzinfo=timezone.utc)


def test_refund_is_allowed_on_day_30():
    order = Order("A-1043", "Nadia Petrova", 8990, DELIVERED)

    allowed = can_refund(order, DELIVERED + timedelta(days=30))

    assert allowed


def test_refund_is_refused_on_day_31():
    order = Order("A-1043", "Nadia Petrova", 8990, DELIVERED)

    allowed = can_refund(order, DELIVERED + timedelta(days=31))

    assert not allowed


def test_total_with_discount():
    total = calculate_total([5000, 3990], discount_cents=1000)

    assert total == 7990
