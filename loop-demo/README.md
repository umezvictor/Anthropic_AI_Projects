# Build A Loop That Calls A Tool And Feeds The Result Back

You write the agent loop by hand. No framework, no helper library. You define
one tool, send a request, read the stop reason, run your own function, and feed
the result back so the model can use it.

Read `SETUP.md` first. Nothing here runs without it.

Commands below use `py`, the Windows launcher. On macOS and Linux use `python3`.

## The files

| File | What it is |
| --- | --- |
| `shared.py` | The local data, our function, and the tool definition. Every step imports it. |
| `step1_no_tool.py` | The same question with no tool at all. |
| `step2_stops.py` | One request with the tool. It stops and waits. |
| `step3_feed_back.py` | One full turn, written out by hand. |
| `step4_loop.py` | The same four steps wrapped in a loop. |
| `step5_broken_id.py` | The pairing rule, broken on purpose. |

## The three parts of shared.py

`ORDERS` is the warehouse. Two orders with a status, a carrier and a delivery
date. The model has no way to know what is in it.

`get_order_status` is your code. This is the function that actually runs.

`TOOLS` is a description of that function, written for the model to read. A
name, a sentence saying when to use it, and a schema for the input. There is no
Python inside it. The model never sees your function. It only sees this text.

## Before you run anything

Your terminal has to be standing in the folder that holds these files. Change
into it with `cd` and the path to where you unzipped it. For example:

```
cd "D:\loop-demo"
```

If you skip this, Python answers with `can't open file ... No such file or
directory`. That message means the file is fine and your terminal is in the
wrong place.

The shortcut: open the folder in VS Code (File, then Open Folder) and press
Ctrl and the backtick key. The terminal that opens is already in the folder.

## Run them in order

### Step 1

```
py step1_no_tool.py
```

`stop_reason` is `end_turn`. The model answers in words and asks for nothing.
It cannot reach an order system, so it says so. That is the ceiling on a single
call.

### Step 2

```
py step2_stops.py
```

`stop_reason` is `tool_use`. The response carries a `tool_use` block holding an
`id`, the tool `name`, and the `input` the model filled in.

Your function did not run. Nothing called it. The model cannot execute your
code. It asked. A response that stops at `tool_use` is a response waiting for
you.

A text block may or may not appear before the `tool_use` block. Build nothing
that depends on it.

### Step 3

```
py step3_feed_back.py
```

Two lines do the work:

```python
messages.append({"role": "assistant", "content": response.content})

messages.append({
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": tool_use.id,
        "content": result,
    }],
})
```

The first puts the model's turn into the history exactly as it arrived. The
second sends the result back in a `tool_result` block carrying the `id` of the
call it answers.

The second `stop_reason` is `end_turn`, and the answer now names the carrier and
the date. The model keeps nothing between calls. It knows about the order only
because you put the answer in the history and sent the whole history back.

### Step 4

```
py step4_loop.py
```

The loop condition reads one field. It counts no iterations and looks for no
phrase:

```python
if response.stop_reason != "tool_use":
    break
```

The body builds a result for every `tool_use` block in the response, not just
the first. The question names two orders, and the model asks for both in one
response. Handle only the first block and the second call goes unanswered, and
the next request is rejected.

### Step 5

```
py step5_broken_id.py
```

The result goes back with an id that matches no call. The request is rejected
before the model sees it:

```
messages.2.content.0: unexpected `tool_use_id` found in `tool_result` blocks:
toolu_this_id_answers_nothing. Each `tool_result` block must have a
corresponding `tool_use` block in the previous message.
```

When several calls come back together, the ids are the only thing saying which
result answers which call.

## Reset

Delete your folder and unzip the download again. Nothing here writes files or
changes anything outside this folder.

## Try it yourself

1. Add a third order to `ORDERS` and ask about it.
2. Ask about an order id that does not exist, and watch what the model does with
   the "No order found" string. Then add `"is_error": true` to that
   `tool_result` and compare the answer.
3. Remove `system=SYSTEM` from one file and see how much longer the answers get.
4. In `step4_loop.py`, change the loop to handle only the first `tool_use` block
   and run it again.

## Documentation

- https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls
- https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons
