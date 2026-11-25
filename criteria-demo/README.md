# Rewrite A Vague Review Prompt Into Explicit Criteria

This folder holds one file to review, two review prompts and one checker.
The vague prompt asks Claude to find problems. The strict prompt names what to
report, what to skip, a severity for each finding and the shape of each line.
Your own code, `check.py`, reads the result.

Read `SETUP.md` if you do not have Python or Claude Code yet.

## Before you run anything

Put the folder somewhere short and open a terminal there:

```
cd "D:\criteria-demo"
```

If you set `ANTHROPIC_API_KEY` for an earlier demo, `claude -p` uses that key
and bills your API credits, even when you are logged in with a subscription.
To use your subscription, clear the key in this terminal first. On Windows:

```
Remove-Item env:ANTHROPIC_API_KEY
```

On macOS and Linux:

```
unset ANTHROPIC_API_KEY
```

This clears the key only in this terminal. Your saved setting does not change.

## The files

| File | What it is |
| --- | --- |
| `review_me.py` | A small order service with real problems in it. The keys in it are fake. |
| `.claude/skills/vague-review/SKILL.md` | The vague prompt, as a skill you start with `/vague-review`. |
| `.claude/skills/strict-review/SKILL.md` | The strict prompt, as a skill you start with `/strict-review`. |
| `check.py` | Your code. It checks every line of a review and counts the lines that pass. |
| `SETUP.md` | How to install Python and Claude Code. |

The `.claude` folder is hidden on some systems. Your editor shows it.

## Run 1. The vague prompt

```
claude -p "/vague-review" > out_vague.txt
```

The `-p` flag runs Claude Code once, with no chat. The answer goes into
`out_vague.txt`. Nothing shows on screen until the command ends.

```
py check.py out_vague.txt
```

On macOS and Linux, use `python3` instead of `py`. Few or no lines pass. The
review can still be useful for a person to read. Your code cannot use it.

## Run 2. The strict prompt

```
claude -p "/strict-review" > out_strict.txt
```

```
py check.py out_strict.txt
```

Each line should pass. If one fails, check.py prints the reason. The counts at the end show each pair of severity and category.

## Run 3. The strict prompt again

```
claude -p "/strict-review" > out_strict_2.txt
```

```
py check.py out_strict_2.txt
```

The words change from run to run. The shape, the categories and the severities
stay inside the rules, and `check.py` checks them the same way every time.

Your findings will use different words from the video.

## Sources

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- https://code.claude.com/docs/en/headless
- https://code.claude.com/docs/en/skills
