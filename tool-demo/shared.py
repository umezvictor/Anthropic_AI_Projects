"""Shared pieces for the tool demo: the model, the requests, and one call."""

import json
from anthropic import Anthropic

client = Anthropic()

MODEL = "claude-sonnet-5"
MAX_TOKENS = 500

SYSTEM = (
    "You help a legal team work with supplier contracts. "
    "The user has contract-2041 open."
)

# Three ordinary requests, one for each job, and the tool that should answer each.
REQUESTS = [
    ("What is the late fee in this contract?", "extract_data_points"),
    ("Give me a short overview of this contract.", "summarize_content"),
    ("The supplier email says we can end this contract with 30 days notice. "
     "Is that right?", "verify_claim_against_source"),
]

# Two requests that fit two tools. The expected tool follows our team rule:
# plain questions go to extract_data_points, even yes or no questions.
HARD_CASES = [
    ("Is payment due in 30 days?", "extract_data_points"),
    ("Can we end this contract early?", "extract_data_points"),
]


def first_tool_call(tools, request):
    """One call. Returns the name of the tool the model picked, and its input."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM,
        tools=tools,
        tool_choice={"type": "any"},
        messages=[{"role": "user", "content": request}],
    )
    call = next(block for block in response.content if block.type == "tool_use")
    return call.name, call.input


def show_input(tool_input):
    """Print the tool input on one line."""
    return json.dumps(tool_input)
