---
description: Review review_me.py with explicit criteria. Run it only when the user asks.
disable-model-invocation: true
---

Review the file review_me.py. Read only that file.

Report two kinds of problems:

- BUG: the code crashes or returns a wrong result for an input the function should handle.
- SECURITY: untrusted input reaches a query, a secret is written in the source, or a check gives a caller access without the right credential.

Skip style, naming, comments, docstrings, type hints and performance. A linter checks those in a later step. In this review, they make the real problems harder to find.

Give each finding a severity:

- HIGH: an attacker can use it, or it breaks the function for normal input. Example, a shell command built by joining user input into a string:

  os.system("ping " + host)

- LOW: it breaks the function only for an unusual input. Example, a division that fails only when the list is empty:

  return sum(values) / len(values)

Return at most 6 findings. Write one finding per line, in this shape:

SEVERITY | CATEGORY | name | one sentence

The name is the function or constant in review_me.py. Here is one finished line:

<example>
LOW | BUG | parse_date | Returns None for every date in December, because the month check stops at 11.
</example>

Return only the finding lines. No headings, no numbers, no blank lines, no text before or after the lines. A script reads every line.
