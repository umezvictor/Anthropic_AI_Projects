"""PreToolUse hook. Blocks any refund over the limit and tells Claude what to do instead."""

import json
import sys
import time
from datetime import datetime

LIMIT_USD = 500
WAIT_SECONDS = 0

call = json.load(sys.stdin)
order_id = call["tool_input"]["order_id"]
amount = float(call["tool_input"]["amount_usd"])

if amount > LIMIT_USD:
    decision = "deny"
else:
    decision = "pass"

with open("hook_log.txt", "a") as log:
    log.write(datetime.now().strftime("%H:%M:%S") + " " + decision + " " + order_id + " " + format(amount, ".2f") + "\n")

time.sleep(WAIT_SECONDS)

if decision == "deny":
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Refunds over 500 dollars need a human reviewer. "
            "Do not retry refund_order for this order, and do not split the amount. "
            "Call escalate_to_human with the order ID, the amount and this reason.",
        }
    }))

sys.exit(0)
