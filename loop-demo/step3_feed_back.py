"""Step 3. Run the function. Feed the result back. Get the answer."""

from anthropic import Anthropic
from shared import MODEL, SYSTEM, TOOLS, get_order_status

client = Anthropic()

messages = [
    {"role": "user", "content": "Where is order A-1042, and when will it arrive?"}
]

response = client.messages.create(
    model=MODEL, max_tokens=1024, system=SYSTEM, tools=TOOLS, messages=messages
)
print("first stop_reason:", response.stop_reason)

tool_use = next(b for b in response.content if b.type == "tool_use")
print("the model asked for:", tool_use.name, tool_use.input)

result = get_order_status(**tool_use.input)
print("our function returned:", result)

# The model's turn goes into the history exactly as it came back.
messages.append({"role": "assistant", "content": response.content})

# The result goes back as a user turn, carrying the id of the call it answers.
messages.append(
    {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result,
            }
        ],
    }
)

final = client.messages.create(
    model=MODEL, max_tokens=1024, system=SYSTEM, tools=TOOLS, messages=messages
)
print("second stop_reason:", final.stop_reason)
print()
for block in final.content:
    if block.type == "text":
        print(block.text)
