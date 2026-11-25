# Setup

You need three things before any file in this folder will run. This takes about
ten minutes the first time. You will reuse the same setup for every hands-on
demo in this course that calls the Claude API.

## 1. Python

Install Python 3.10 or newer from https://www.python.org/downloads/

On Windows, tick **Add python.exe to PATH** on the first screen of the
installer. That box is easy to miss and everything fails without it.

Check it worked. Open a new terminal and run:

- Windows: `py --version`
- macOS and Linux: `python3 --version`

## 2. The Anthropic Python library

- Windows: `py -m pip install anthropic`
- macOS and Linux: `python3 -m pip install anthropic`

## 3. An API key

Create a Claude Console account at https://platform.claude.com

The Console is a developer account. It is separate from a Claude Pro, Max, Team
or Enterprise subscription, and API calls are billed separately from one. A
subscription does not cover API usage.

Add the smallest amount of credit offered. Running this whole demo, several
times over, costs a few cents. While you are there, set a monthly spend limit.

Then create a key at https://platform.claude.com/settings/keys
The key is shown once. Copy it before you close the page.

## 4. Store the key in an environment variable

The library reads a variable named `ANTHROPIC_API_KEY` on its own. Never write
the key into a source file.

**Windows**

Press Start, type "Edit the system environment variables", open it. Click
**Environment Variables**. Under **User variables**, click **New**.

- Name: `ANTHROPIC_API_KEY`
- Value: your key

Click OK twice. Close every open terminal. A terminal only reads the variable
when it starts.

Check it, without printing the key, in a new PowerShell window:

```
if ($env:ANTHROPIC_API_KEY) { "key is set" } else { "key is NOT set" }
```

**macOS and Linux**

Add this line to `~/.zshrc` or `~/.bashrc`, then open a new terminal:

```
export ANTHROPIC_API_KEY="your key here"
```

Check it with `echo ${ANTHROPIC_API_KEY:+key is set}`

## If something fails

| What you see | What it means |
| --- | --- |
| `py is not recognized` | Python is not installed, or you missed the PATH box. |
| `can't open file ... No such file or directory` | Your terminal is not in the folder holding the files. Use `cd` to change into it. |
| `No module named anthropic` | Step 2 did not run, or it ran for a different Python. |
| `Could not resolve authentication method` | The variable is not set, or the terminal started before you set it. |
| `Your credit balance is too low` | Add credit in the Console. |
