# Add A Server To .mcp.json And Share It

You have one file, `server.py`. It is a small MCP server with one tool,
`refund_order`. In this demo you tell Claude Code how to start it, approve it,
and use it inside a session.

There is no `.mcp.json` in this download. You create it with one command, and
that is part of the demo.

Read `SETUP.md` first. Nothing here runs without it.

Commands below use `py`, the Windows launcher. On macOS and Linux use `python3`.

## Before you run anything

Put the files in a short folder and open a terminal there:

```
cd "D:\refunds-demo"
```

## The files

| File | What it is |
| --- | --- |
| `server.py` | The refunds server. One tool, two orders, and a 30 day refund window. |
| `SETUP.md` | Python, the MCP Python SDK, and Claude Code. |

## Step 1. Write .mcp.json

```
claude mcp add --scope project --transport stdio refunds -- py server.py
```

On macOS and Linux, use `python3 server.py` at the end instead of `py server.py`.

The command writes `.mcp.json` in this folder. Open it and read it. It holds the
server name, the command that starts the server, and its arguments. Project
scope means the file belongs in your repository, so everyone who clones it gets
the same server. Keep secrets out of this file.

## Step 2. Use the server

```
claude
```

Claude Code asks you to approve the project server the first time. Approve it,
then check it:

```
/mcp
```

Then ask for a refund in plain words:

```
Refund order A-1043.
```

## What the tool does

`refund_order` takes an order ID. It refunds an order that shipped inside the
30 day window. Order `A-1043` shipped 8 days ago. Order `B-2277` shipped 74 days
ago. Any other ID is unknown to the server.

The two failure answers in `server.py` are poor on purpose. The next hands-on
lecture gives them a real error contract.

## Sources

- https://code.claude.com/docs/en/mcp
- https://modelcontextprotocol.io/specification/2026-07-28/server/tools
- https://py.sdk.modelcontextprotocol.io/
