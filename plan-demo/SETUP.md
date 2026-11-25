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

The latest instructions live at https://code.claude.com/docs/en/quickstart

## If something fails

| What you see | What it means |
| --- | --- |
| `claude is not recognized` | Claude Code is not installed, or your terminal started before the install finished. Open a new terminal. |
| `py is not recognized` | Python is not installed, or you are on macOS or Linux. Use `python3`. |
| `Ran 0 tests` | Your terminal is not in the demo folder. Run `cd` to the folder first. |
| The status bar does not show `plan mode on` | Press `Shift+Tab` until it does. |
