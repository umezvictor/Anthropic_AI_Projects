"""Shared pieces for the S02-L07 demo: the local data, our function, the tool definition."""

import json

MODEL = "claude-sonnet-5"

# Keeps the answers short enough to read on screen.
SYSTEM = "Answer in two sentences at most. Do not use bullet points."

# The warehouse system. A real one would be a database. This is enough to make
# the point: the model cannot know what is in here.
ORDERS = {
    "A-1042": {"status": "shipped", "carrier": "DHL", "eta": "2026-09-18"},
    "A-1043": {"status": "packing", "carrier": None, "eta": "2026-09-22"},
}


def get_order_status(order_id):
    """Our code. This is what actually runs."""
    order = ORDERS.get(order_id)
    if order is None:
        return f"No order found with id {order_id}."
    return json.dumps(order)


# What the model reads. Not the function. A description of the function.
TOOLS = [
    {
        "name": "get_order_status",
        "description": (
            "Look up the current status of one customer order in the warehouse "
            "system. Use this whenever the user names an order id."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order id, for example A-1042.",
                }
            },
            "required": ["order_id"],
        },
    }
]
