# Split A Generic Tool Into Three

A legal team asks an agent about a supplier contract. You will give the agent its
tools in two ways. First as one tool, `analyze_document`, with an `action`
parameter. Then as three tools with one job each: `extract_data_points`,
`summarize_content` and `verify_claim_against_source`.

The script stops at the tool call. The tool call is where the model makes its
choice, so that is the part you test.

Read `SETUP.md` first. Nothing here runs without it.

Commands below use `py`, the Windows launcher. On macOS and Linux use `python3`.

## Before you run anything

Your terminal has to be in the folder holding these files:

```
cd "D:\tool-demo"
```

## The files

| File | What it is |
| --- | --- |
| `tools.py` | The one tool, the three tools, and a short version of the three tools. |
| `shared.py` | The model, the system prompt, the requests, and the one call every step makes. |
| `step1_one_tool.py` | Three requests, one tool. |
| `step2_three_tools.py` | The same three requests, three tools. Checks each pick. |
| `step3_hard_cases.py` | Two requests that fit two tools. Short descriptions against full descriptions. |

## Run it

```
py step1_one_tool.py
py step2_three_tools.py
py step3_hard_cases.py
```

## One tool or several: what the documentation says

The Claude tool use documentation gives this advice: group related operations
into one tool with an `action` parameter. Its example is `create_pr`,
`review_pr` and `merge_pr` in one tool. Fewer tools mean fewer similar names to
choose between.

Anthropic's guide on writing tools for agents also says each tool needs a clear,
distinct purpose.

Both rules are true. They cover different cases.

- **One tool with an action parameter** gives the model fewer names to choose
  from. All three pull request actions work on pull requests, so the
  documentation groups them.
- **Separate tools** give each job its own required inputs, its own description,
  and its own name your code can check. Choose them when those matter more than
  a shorter list. In this demo, extract needs a list of fields, summarize needs a
  length, and verify needs a claim. Extract returns values, summarize returns
  prose, and verify returns a verdict.

Look at the schema of `analyze_document` in `tools.py`. The field `claim` is
optional, because only one of the three actions uses it. So the schema accepts a
verify call with no claim. A longer schema could require it for verify only. In `verify_claim_against_source`, `claim`
is required.

## Sources

- https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use
- https://www.anthropic.com/engineering/writing-tools-for-agents
