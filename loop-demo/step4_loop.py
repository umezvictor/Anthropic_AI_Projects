"""Step 4. The same four steps, wrapped in a loop, driven by stop_reason."""

from anthropic import Anthropic
from shared import MODEL, SYSTEM, TOOLS, get_order_status

client = Anthropic()

messages = [
    {
        "role": "user",
        "content": "Compare order A-1042 and order A-1043. Which one arrives first?",
    }
]

while True:
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM,
        tools=TOOLS,
        messages=messages,
    )
    print("stop_reason:", response.stop_reason)

    if response.stop_reason != "tool_use":
        break

    messages.append({"role": "assistant", "content": response.content})

    results = []
    for block in response.content:
        if block.type == "tool_use":
            print("  calling", block.name, "with", block.input)
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": get_order_status(**block.input),
                }
            )

    messages.append({"role": "user", "content": results})

print()
for block in response.content:
    if block.type == "text":
        print(block.text)
