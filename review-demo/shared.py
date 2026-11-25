"""Shared pieces for the S02-L08 demo: the models, the code under review, the criteria."""

import pathlib
from anthropic import Anthropic

client = Anthropic()

STRONG = "claude-sonnet-5"
CHEAP = "claude-haiku-4-5-20251001"

MAX_TOKENS = 1000

SYSTEM = (
    "You are reviewing a Python file. Report only real problems you can point at.\n"
    "Write one finding per line. Begin the line with the name of the function or "
    "constant it is about, then a colon, then one sentence saying what is wrong.\n"
    "No headings. No blank lines. No summary."
)

CODE = pathlib.Path("review_me.py").read_text(encoding="utf-8")

CORRECTNESS = (
    "Find correctness bugs. Look for wrong results, crashes on ordinary input, "
    "lost precision, and collections changed while they are being read."
)

SECURITY = (
    "Find security problems. Look for untrusted input reaching a query, secrets "
    "written into the source, and authentication checks that can be passed without "
    "the right credential."
)

PERFORMANCE = (
    "Find performance problems. Look for work repeated inside a loop that belongs "
    "outside it, quadratic scans where a lookup would do, and growth patterns that "
    "get slower as the input gets bigger."
)

# Added only when a pass is one of several. A single call carrying all three jobs
# must not be told to ignore the other two.
ONLY_THIS_JOB = (
    " Report nothing else. If you see a problem of another kind, leave it out, "
    "because another pass is looking for it."
)


def ask(instruction, model):
    """One call. Returns the findings, the token counts, and why it stopped."""
    response = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        system=SYSTEM,
        messages=[
            {"role": "user", "content": instruction + "\n\nThe file:\n\n" + CODE}
        ],
    )
    text = "".join(b.text for b in response.content if b.type == "text").strip()
    return text, response.usage.input_tokens, response.usage.output_tokens, response.stop_reason


def report_call(tokens_in, tokens_out, stop_reason):
    """Print what the call cost, and shout if the answer was cut off."""
    print("tokens in:", tokens_in, " tokens out:", tokens_out, " stop_reason:", stop_reason)
    if stop_reason == "max_tokens":
        print("*** CUT OFF. The answer hit the", MAX_TOKENS, "token limit. ***")
