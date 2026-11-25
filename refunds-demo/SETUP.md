# Setup

This demo needs three things. Two of them you already have from the earlier
hands-on demos in this course.

## 1. Python

Same as before. Python 3.10 or newer, from https://www.python.org/downloads/
On Windows, tick **Add python.exe to PATH** in the installer.

Check it:

- Windows: `py --version`
- macOS and Linux: `python3 --version`

## 2. The MCP Python SDK

This is the new one. It gives you the server class the demo uses.

- Windows: `py -m pip install "mcp[cli]"`
- macOS and Linux: `python3 -m pip install "mcp[cli]"`

## 3. Claude Code

Install it from a terminal.

**Windows, in PowerShell:**

```
irm https://claude.ai/install.ps1 | iex
```

**macOS and Linux:**

```
curl -fsSL https://claude.ai/install.sh | bash
```

Close the terminal and open a new one. Then check the install:

```
claude --version
```

Start it once with `claude`. It asks you how you want to log in. You have two
options, and either one works for this demo:

- A Claude subscription: Pro, Max, Team or Enterprise. Your plan covers the usage.
- A Claude Console account, the same account the earlier demos used. This bills
  your API credits.

If you set `ANTHROPIC_API_KEY` for the earlier demos, Claude Code sees it and asks
whether to use that key. Answer no if you want your subscription to cover this
demo. Answer yes if you want to pay from your API credits.

The latest instructions live at https://code.claude.com/docs/en/quickstart

## If something fails

| What you see | What it means |
| --- | --- |
| `py is not recognized` | Python is not installed, or you missed the PATH box. |
| `No module named mcp` | Step 2 did not run, or it ran for a different Python. |
| `claude is not recognized` | Claude Code is not installed, or your terminal started before the install finished. Open a new terminal. |
| `Failed to connect` next to the server in `/mcp` | The command in `.mcp.json` cannot start the server. Check the path and run the command by hand. |
