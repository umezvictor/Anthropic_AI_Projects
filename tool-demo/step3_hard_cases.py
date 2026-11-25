"""Step 3. Requests that fit two tools. Short descriptions, then full descriptions."""

from shared import first_tool_call, HARD_CASES
from tools import SHORT_TOOLS, THREE_TOOLS

for request, expected in HARD_CASES:
    short_pick, _ = first_tool_call(SHORT_TOOLS, request)
    full_pick, _ = first_tool_call(THREE_TOOLS, request)
    print("request: ", request)
    print("expected:", expected)
    print("short:   ", short_pick, " ", "PASS" if short_pick == expected else "FAIL")
    print("full:    ", full_pick, " ", "PASS" if full_pick == expected else "FAIL")
    print()
