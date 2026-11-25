"""Tests for the order totals."""

from orders import calculate_total

LINES = [
    {"price": 10.0, "quantity": 2},
    {"price": 5.5, "quantity": 4},
]


def test_total_with_no_discount():
    assert calculate_total(LINES) == 50.4


def test_total_with_discount():
    assert calculate_total(LINES, 0.1) == 45.36
