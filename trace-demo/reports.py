"""Monthly reports. Careful: the function here only looks like the one we trace."""

from orders import VAT_RATE


def recalculate_total(rows):
    """Add up rows that already carry a net value, then add VAT."""
    net = 0.0
    for row in rows:
        net = net + row["net"]
    return round(net * (1.0 + VAT_RATE), 2)


def monthly_report(month, rows):
    """A short report line for one month."""
    return month + ": " + str(recalculate_total(rows)) + " euro"
