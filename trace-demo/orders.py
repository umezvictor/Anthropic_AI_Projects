"""Orders. This file defines calculate_total, the function we will trace."""

VAT_RATE = 0.20


def calculate_total(lines, discount=0.0):
    """Add up the order lines, take off the discount, then add VAT.

    lines is a list of dictionaries with a price and a quantity.
    discount is a share between 0 and 1, so 0.1 means ten percent off.
    """
    net = 0.0
    for line in lines:
        net = net + line["price"] * line["quantity"]

    net = net * (1.0 - discount)
    return round(net * (1.0 + VAT_RATE), 2)


def order_summary(order):
    """One line of text for an order, with its total."""
    total = calculate_total(order["lines"], order.get("discount", 0.0))
    return order["id"] + ": " + str(total) + " euro"
