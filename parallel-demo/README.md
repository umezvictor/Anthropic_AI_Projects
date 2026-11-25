# Run Three Subagents In Parallel And Merge The Findings

One file is under review. Three reviewers look at it at the same time, each one
with its own job. Then your own code merges their results into one report.

Read `SETUP.md` first. You need Python and Claude Code. No API key.

## Before you start Claude Code

Put the files in a short folder and open a terminal there:

```
cd "D:\parallel-demo"
```

## The files

| File | What it is |
| --- | --- |
| `review_me.py` | The file under review. A small order service with real problems in it. |
| `.claude/agents/correctness.md` | Reviewer one. Correctness bugs. Tool: `Read`. |
| `.claude/agents/security.md` | Reviewer two. Security problems. Tool: `Read`. |
| `.claude/agents/performance.md` | Reviewer three. Performance problems. Tool: `Read`. |
| `merge.py` | Your code. It merges the three result files into `report.md`. |
| `SETUP.md` | Python and Claude Code. |

The secrets in `review_me.py` are fake. They are there for the security reviewer
to find.

## Run 1. Three reviewers at the same time

```
claude
```

Then type:

```
Review review_me.py. Run the correctness, security and performance subagents at the same time, one subagent each. Save each subagent's findings to out_correctness.txt, out_security.txt and out_performance.txt, exactly as the subagent returned them. Do not print the findings in the chat. Say only which files you wrote.
```

Each reviewer reads the file on its own and returns at most 3 findings. The
coordinator writes the three files.

## Run 2. Your code merges the three files

```
py merge.py
```

On macOS and Linux, use `python3 merge.py`.

The script writes `report.md`. It keeps the sections in one order, and it drops
a finding when an earlier section already named that function. It prints every
repeat it dropped. It also skips a line that does not look like a finding, for
example a file name a reviewer adds at the end.

## Run 3. What the drop rule does

The three reviewers have separate jobs, so no function appears in two sections,
and the merge drops nothing. To see the rule work, copy one finding into a
second file by hand:

**Windows, in PowerShell:**

```
Get-Content out_security.txt -TotalCount 1 | Add-Content out_performance.txt
```

**macOS and Linux:**

```
head -n 1 out_security.txt >> out_performance.txt
```

Then run the merge again:

```
py merge.py
```

The same finding is now in two files. Security comes first in the report, so the
copy in the performance section is dropped, and the script prints it under
"Dropped".

Your wording from the reviewers will differ from the video. The three files, the
merge and the report format will be the same.

## Sources

- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/agent-sdk/subagents
