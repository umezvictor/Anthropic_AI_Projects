"""Step 5. Send the result back with the wrong id and watch what happens."""

import anthropic
from anthropic import Anthropic
from shared import MODEL, SYSTEM, TOOLS, get_order_status

client = Anthropic()

messages = [
    {"role": "user", "content": "Where is order A-1042, and when will it arrive?"}
]

response = client.messages.create(
    model=MODEL, max_tokens=1024, system=SYSTEM, tools=TOOLS, messages=messages
)

tool_use = next(b for b in response.content if b.type == "tool_use")
result = get_order_status(**tool_use.input)

messages.append({"role": "assistant", "content": response.content})
messages.append(
    {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": "toolu_this_id_answers_nothing",
                "content": result,
            }
        ],
    }
)

try:
    final = client.messages.create(
        model=MODEL, max_tokens=1024, system=SYSTEM, tools=TOOLS, messages=messages
    )
    print(final.stop_reason)
except anthropic.BadRequestError as error:
    print("The request was rejected.")
    print()
    try:
        print(error.body["error"]["message"])
    except (TypeError, KeyError):
        print(error.message)
