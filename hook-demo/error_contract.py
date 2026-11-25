"""The error contract of the refunds server.

The protocol gives you one flag, isError. It does not define the fields inside
the error. So the fields below are our own convention. Claude Code passes this
text to the model, and the model reads the fields.

  errorCategory   what kind of failure this is
  isRetryable     true only when the same call can succeed later
  message         the reason and the next step, in plain words
"""

import json

from mcp.server.mcpserver.exceptions import ToolError


def _fail(category, retryable, message):
    """Raise one failure. The SDK marks the result as an error and sends this text."""
    raise ToolError(
        json.dumps(
            {
                "errorCategory": category,
                "isRetryable": retryable,
                "message": message,
            }
        )
    )


def unknown_order(order_id):
    """The order ID is not in the database. Wrong argument, so another try fails too."""
    _fail(
        "validation",
        False,
        "No order with ID "
        + order_id
        + " exists. Ask the customer for the order ID again and call once more with the correct one.",
    )


def outside_refund_window(order_id, days_since_shipping, window_days):
    """The call was correct. The shop's rule refuses it. Nothing changes on a retry."""
    _fail(
        "business_rule",
        False,
        "This shop refunds an order within "
        + str(window_days)
        + " days of shipping. Order "
        + order_id
        + " shipped "
        + str(days_since_shipping)
        + " days ago, so it is outside the refund window. Tell the customer the refund window has closed.",
    )
