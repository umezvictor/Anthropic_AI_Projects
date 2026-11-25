import unittest

from shop import refunds


class RefundTests(unittest.TestCase):

    def setUp(self):
        refunds.REFUNDED.clear()

    # These two tests pass today.

    def test_full_refund(self):
        self.assertEqual(refunds.refund_order("A-1043"), 89.90)

    def test_unknown_order(self):
        with self.assertRaises(ValueError):
            refunds.refund_order("Z-0000")

    # These two tests need partial refunds. They fail today.

    def test_partial_refunds(self):
        self.assertEqual(refunds.refund_order("C-3310", 300), 300)
        self.assertEqual(refunds.refund_order("C-3310", 200), 200)

    def test_refund_more_than_left(self):
        refunds.refund_order("C-3310", 800)
        with self.assertRaises(ValueError):
            refunds.refund_order("C-3310", 200)
