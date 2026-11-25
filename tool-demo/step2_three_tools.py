"""Step 2. The same three requests. Three tools, one job each."""

from shared import first_tool_call, show_input, REQUESTS
from tools import THREE_TOOLS

for request, expected in REQUESTS:
    name, tool_input = first_tool_call(THREE_TOOLS, request)
    result = "PASS" if name == expected else "FAIL"
    print("request: ", request)
    print("expected:", expected)
    print("picked:  ", name, " ", result)
    print("input:   ", show_input(tool_input))
    print()
