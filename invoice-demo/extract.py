"""Read one invoice and return its fields as JSON, in the shape of SCHEMA.
The schema on the request sets the shape. check.py checks the values."""

import json
import pathlib
import sys

import anthropic

MODEL = "claude-sonnet-5"

PROMPT = """Extract the fields of the invoice below.
Write every amount as a plain number, with no currency symbol and no comma.
If a field is not in the invoice, return null. Do not guess.

<invoice>
{invoice}
</invoice>"""

SCHEMA = {
    "type": "object",
    "properties": {
        "invoice_number": {"type": "string"},
        "po_number": {
            "type": ["string", "null"],
            "description": "The purchase order number. Null if the invoice has none.",
        },
        "line_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "amount": {"type": "number"},
                },
                "required": ["description", "amount"],
                "additionalProperties": False,
            },
        },
        "stated_total": {
            "type": "number",
            "description": "The total printed on the invoice.",
        },
        "calculated_total": {
            "type": "number",
            "description": "The sum of the line item amounts. Add them up yourself.",
        },
        "conflict_detected": {
            "type": "boolean",
            "description": "True if calculated_total is not equal to stated_total.",
        },
    },
    "required": [
        "invoice_number",
        "po_number",
        "line_items",
        "stated_total",
        "calculated_total",
        "conflict_detected",
    ],
    "additionalProperties": False,
}

invoice_file = pathlib.Path(sys.argv[1])
invoice = invoice_file.read_text(encoding="utf-8")

client = anthropic.Anthropic()
response = client.messages.create(
    model=MODEL,
    max_tokens=4096,
    messages=[{"role": "user", "content": PROMPT.format(invoice=invoice)}],
    output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
)

# A refusal or a cut at max_tokens can break the schema. Stop there.
if response.stop_reason != "end_turn":
    sys.exit("Stopped: " + response.stop_reason + ". Do not use this output.")

# Sonnet can think first, so the answer is the text block, not the first block.
text = next(block.text for block in response.content if block.type == "text")
out_file = invoice_file.with_suffix(".json")
out_file.write_text(text, encoding="utf-8")

print(json.dumps(json.loads(text), indent=2))
print()
print("Saved to", out_file.name)
