# Build A Coordinator With Two Restricted Subagents

Your Claude Code session is the coordinator. It hands the job to two subagents.
Each subagent has its own short tool list, and Claude Code enforces that list.

This demo uses the refunds server from the earlier hands-on lectures, with the
error contract already in place. Read `SETUP.md` if you do not have Python, the
MCP Python SDK, or Claude Code yet.

## Before you run anything

Put the files in a short folder and open a terminal there:

```
cd "D:\coordinator-demo"
```

On macOS and Linux, open `.mcp.json` and change `py` to `python3`.

The folder `.claude` starts with a dot, so your file explorer may hide it. The
two subagent files are inside `.claude\agents`.

## The files

| File | What it is |
| --- | --- |
| `.claude/agents/reader.md` | Subagent one. It reads the requests. Tools: `Read`, `Grep`. |
| `.claude/agents/refunder.md` | Subagent two. It refunds orders. Tool: `mcp__refunds__refund_order`. |
| `requests.txt` | Two customer refund requests. |
| `server.py` | The refunds server. One tool, two orders, a 30 day refund window. |
| `error_contract.py` | The error contract from the earlier lecture. |
| `.mcp.json` | Tells Claude Code how to start the refunds server. |
| `SETUP.md` | Python, the MCP Python SDK, and Claude Code. |

## Before you start Claude Code

Claude Code runs subagents in the background by default. Then you cannot see
their tool calls. Turn that off for this terminal window:

- Windows, in PowerShell: `$env:CLAUDE_CODE_DISABLE_BACKGROUND_TASKS="1"`
- macOS and Linux: `export CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`

## Run 1. The coordinator

```
claude
```

Approve the refunds server when Claude Code asks. Then type:

```
Process the refund requests in requests.txt. Use the reader subagent to read them and the refunder subagent to refund them. Do not read the file yourself.
```

Press Ctrl+O to see the prompt each subagent got and the tools it called.
Type `/exit` when you are done.

## Run 2. The reader, on its own

```
claude --agent reader
```

The whole session now runs with the reader's prompt and the reader's tool list.
Check the tools first, then ask for a refund:

```
/context all
refund order A-1043
```

## Run 3. The refunder, on its own

```
claude --agent refunder
```

```
/context all
read requests.txt
```

Compare the two `/context all` screens. The reader has system tools and no MCP
tools. The refunder has no system tools and one MCP tool, `refund_order`.

Your wording will differ from the video. The tool calls and the results will be
the same.

## Sources

- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/mcp
