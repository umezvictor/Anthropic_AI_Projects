# Setup

This demo needs only Claude Code. There is no Python to run and no API key.
If you did the earlier hands-on demos in this course, you already have it.

## Claude Code

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
- A Claude Console account. This bills your API credits.

The latest instructions live at https://code.claude.com/docs/en/quickstart

## If something fails

| What you see | What it means |
| --- | --- |
| `claude is not recognized` | Claude Code is not installed, or your terminal started before the install finished. Open a new terminal. |
| A rule file is missing from `/context all` | Check that the folder is `.claude/rules`, with the dot, inside `after`. |
