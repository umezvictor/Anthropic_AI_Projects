"""Step 2. Give it the tool. Send one request. Look at what comes back."""

from anthropic import Anthropic
from shared import MODEL, SYSTEM, TOOLS

client = Anthropic()

response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    system=SYSTEM,
    tools=TOOLS,
    messages=[
        {"role": "user", "content": "Where is order A-1042, and when will it arrive?"}
    ],
)

print("stop_reason:", response.stop_reason)
print()

for block in response.content:
    if block.type == "text":
        print("text block:", block.text)
    elif block.type == "tool_use":
        print("tool_use block")
        print("  id:   ", block.id)
        print("  name: ", block.name)
        print("  input:", block.input)

print()
print("Our function did not run. Nothing called it.")
