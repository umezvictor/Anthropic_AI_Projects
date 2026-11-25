"""Step 1. One tool with an action parameter. Three different jobs."""

from shared import first_tool_call, show_input, REQUESTS
from tools import ONE_TOOL

for request, expected in REQUESTS:
    name, tool_input = first_tool_call(ONE_TOOL, request)
    print("request:", request)
    print("tool:   ", name)
    print("input:  ", show_input(tool_input))
    print()
