# Setup

This demo needs Python and Claude Code. There is no API key and nothing else
to install. If you did the earlier hands-on demos in this course, you already
have both.

## Python

Install Python 3.10 or newer from https://www.python.org/downloads/

Check it in a new terminal. On Windows:

```
py --version
```

On macOS and Linux:

```
python3 --version
```

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

This demo runs `claude -p`. In that mode, Claude Code always uses
`ANTHROPIC_API_KEY` when it is set, even when you are logged in with a
subscription. If you set the key for an earlier demo, clear it in your terminal
before the runs. README.md shows the command.

The latest instructions live at https://code.claude.com/docs/en/quickstart

## If something fails

| What you see | What it means |
| --- | --- |
| `claude is not recognized` | Claude Code is not installed, or your terminal started before the install finished. Open a new terminal. |
| `py is not recognized` | Python is not installed, or you are on macOS or Linux. Use `python3`. |
| `No such file or directory: 'review_me.py'` | Your terminal is not in the demo folder. Run `cd` to the folder first. |
| Claude does not run the review, or says it cannot find the command | Claude Code did not find the skill. Check that the `.claude` folder is in the demo folder. |
| Strange characters in the answer, such as `ΓÇö` in place of a dash | Windows PowerShell 5.1 read the answer with the wrong encoding. The PASS and FAIL results do not change. To fix the text, run `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8` once in that window, then run the command again. |
