# Setup

This demo needs two things, and you have both from the earlier demos.

## 1. Python

Python 3.10 or newer, from https://www.python.org/downloads/
On Windows, tick **Add python.exe to PATH** in the installer.

Check it:

- Windows: `py --version`
- macOS and Linux: `python3 --version`

## 2. Claude Code

If you do not have it yet, install it from a terminal.

**Windows, in PowerShell:**

```
irm https://claude.ai/install.ps1 | iex
```

**macOS and Linux:**

```
curl -fsSL https://claude.ai/install.sh | bash
```

Close the terminal, open a new one, and check the install:

```
claude --version
```

There is no API key in this demo, and no server to install. Claude Code does all
the work.

The latest instructions live at https://code.claude.com/docs/en/quickstart
