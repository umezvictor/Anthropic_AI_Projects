# Split A 400-Line CLAUDE.md Into Scoped Rules

This folder holds one small project in two layouts.

- `before` has one CLAUDE.md with 400 lines. Every rule loads in every session.
- `after` has the same rules, split into a short CLAUDE.md and four rule files
  in `.claude/rules`. Three of the rule files load only when Claude reads a
  file they match.

You do not run the code in this demo. You only start Claude Code and check
which instruction files it loaded. Read `SETUP.md` if you do not have Claude
Code yet.

## Before you run anything

Put the folder somewhere short and open a terminal there:

```
cd "D:\rules-demo"
```

The folder `.claude` starts with a dot, so your file explorer may hide it.

If you have your own `~/.claude/CLAUDE.md` or `~/.claude/rules`, Claude Code
loads them too, and you see them in the lists below. That is normal.

## The files

| File | What it is |
| --- | --- |
| `before/CLAUDE.md` | All the rules in one file, 400 lines. |
| `after/CLAUDE.md` | The rules for every task: layout, commands, git. |
| `after/.claude/rules/style.md` | Code style. No `paths` field, so it loads at launch. |
| `after/.claude/rules/api.md` | API rules. Loads when Claude reads a file under `api/`. |
| `after/.claude/rules/testing.md` | Testing rules. Loads when Claude reads a file named `test_*.py`, in any folder. |
| `after/.claude/rules/migrations.md` | Migration rules. Loads when Claude reads a file under `db/migrations/`. |
| `shop/`, `api/`, `db/` | A small order and refund service, the same in both folders. |
| `SETUP.md` | How to install Claude Code. |

## Run 1. One big file

```
cd before
claude
```

Trust the folder when Claude Code asks. Then:

```
/context all
```

Look at Memory files. Then type `/exit`.

## Run 2. The split, and one API file

```
cd ..\after
claude
```

On macOS and Linux, use `cd ../after`. Then:

```
/context all
```

Now type:

```
Read api/routes.py and tell me in one line what it does. Do not open any other file.
```

Look under the read. Claude Code prints one line: `Loaded .claude\rules\api.md`.
Then `/exit`.

## Run 3. One test file, in a new session

```
claude
```

Type:

```
Read shop/test_orders.py and tell me in one line what it tests. Do not open any other file.
```

This time the line is `Loaded .claude\rules\testing.md`, and api.md does not
load. Then `/exit`.

The migrations rule never loads, because no run reads a file under
`db/migrations/`.

`/context all` lists only the files that loaded at launch under Memory files.
A rule with `paths` goes into the conversation, so it does not appear in that
list. The `Loaded` line is where you see it.

Your wording will differ from the video. The files that load will be the same.

## Sources

- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/context-window
