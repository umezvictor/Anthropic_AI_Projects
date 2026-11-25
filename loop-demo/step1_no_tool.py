"""Step 1. No tools. The model has no way to know."""

from anthropic import Anthropic
from shared import MODEL, SYSTEM

client = Anthropic()

response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    system=SYSTEM,
    messages=[
        {"role": "user", "content": "Where is order A-1042, and when will it arrive?"}
    ],
)

print("stop_reason:", response.stop_reason)
for block in response.content:
    if block.type == "text":
        print(block.text)
