"""Check one extracted invoice. Your code, not the model."""

import json
import pathlib
import sys

NUMBER = (int, float)
FIELDS = {
    "invoice_number": str,
    "po_number": (str, type(None)),
    "line_items": list,
    "stated_total": NUMBER,
    "calculated_total": NUMBER,
    "conflict_detected": bool,
}

data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
problems = []

# 1. The shape. The schema on the request guarantees it.
for name, kind in FIELDS.items():
    if name not in data:
        sys.exit("Shape:  FAIL, " + name + " is missing")
    if not isinstance(data[name], kind):
        sys.exit("Shape:  FAIL, " + name + " has the wrong type")
print("Shape:  OK, every field is there, with the right type")

# 2. The total. My own sum of the line items, against the printed total.
my_sum = round(sum(item["amount"] for item in data["line_items"]), 2)
stated = data["stated_total"]
if my_sum == stated:
    print(f"Total:  OK, the line items add up to {stated:.2f}")
else:
    print(f"Total:  FAIL, the line items add up to {my_sum:.2f}, the invoice says {stated:.2f}")
    problems.append("the printed total does not match the line items")

# 3. The model's own check, next to mine.
agrees = data["conflict_detected"] == (my_sum != stated)
print("Model:  conflict_detected is", str(data["conflict_detected"]).lower(),
      "(agrees with my check)" if agrees else "(does NOT agree with my check)")

# 4. The PO number.
if data["po_number"] is None:
    print("PO:     MISSING, the invoice has no PO number")
    problems.append("the PO number is missing")
else:
    print("PO:     OK,", data["po_number"])

print()
if problems:
    print("Result: SEND TO A PERSON. Reason:", "; ".join(problems) + ".")
else:
    print("Result: PASS")
