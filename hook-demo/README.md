# Block A Refund Over $500 With A PreToolUse Hook

The hook in this demo is a short Python script. Claude Code runs it before
every refund_order call. The hook reads the amount. Over 500 dollars, it
blocks the call and tells Claude what to do instead.

This demo uses the refunds server from the earlier hands-on lectures, with two
changes: refund_order now takes an amount, and there is a second tool,
escalate_to_human. Read `SETUP.md` if you do not have Python, the MCP Python
SDK, or Claude Code yet.

## Before you run anything

Put the files in a short folder and open a terminal there:

```
cd "D:\hook-demo"
```

On macOS and Linux, change `py` to `python3` in two files: `.mcp.json` and
`.claude/settings.json`.

The folder `.claude` starts with a dot, so your file explorer may hide it.

## The files

| File | What it is |
| --- | --- |
| `.claude/settings.json` | Registers the hook for `mcp__refunds__refund_order`, and allows both refunds tools. |
| `.claude/hooks/refund_limit.py` | The hook. Blocks a refund over 500 dollars and returns a reason. |
| `server.py` | The refunds server. Two orders, two tools. It knows nothing about the 500 dollar limit. |
| `error_contract.py` | The error contract from the earlier lecture. |
| `call_900.json`, `call_89.json` | Two sample inputs, to run the hook by hand. |
| `.mcp.json` | Tells Claude Code how to start the refunds server. |
| `SETUP.md` | Python, the MCP Python SDK, and Claude Code. |

The hook writes one line to `hook_log.txt` every time it runs. To start clean,
delete `hook_log.txt`.

## Run 1. The hook blocks one refund

```
claude
```

Approve the refunds server and trust the folder when Claude Code asks. Then:

```
/hooks
```

Press Esc to close it. Then type:

```
Refund order A-1043 for 89.90 dollars and order C-3310 for 900 dollars.
```

Type `/exit`, then open `hook_log.txt`.

## Run 2. The hook without Claude

Windows, in PowerShell:

```
Get-Content call_900.json | py .claude\hooks\refund_limit.py
Get-Content call_89.json | py .claude\hooks\refund_limit.py
```

macOS and Linux:

```
python3 .claude/hooks/refund_limit.py < call_900.json
python3 .claude/hooks/refund_limit.py < call_89.json
```

## Run 3. A slow hook is not a gate

Make two changes:

- `.claude/settings.json`: change `"timeout": 10` to `"timeout": 1`.
- `.claude/hooks/refund_limit.py`: change `WAIT_SECONDS = 0` to `WAIT_SECONDS = 3`.

Start `claude` again and type:

```
Refund order C-3310 for 900 dollars.
```

The hook needs 3 seconds, and Claude Code waits 1. Claude Code cancels the
hook, and the refund runs. Put both values back when you are done.

Your wording will differ from the video. The hook decisions will be the same.

## Sources

- https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/permissions
