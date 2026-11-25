"""Check every line of a review against the shape in the strict-review skill.
Your code, not the model."""

import ast
import pathlib
import sys

SEVERITIES = ["HIGH", "LOW"]
CATEGORIES = ["BUG", "SECURITY"]


def read_text(path):
    # Windows PowerShell 5.1 saves ">" output as UTF-16. PowerShell 7 saves UTF-8.
    raw = pathlib.Path(path).read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    return raw.decode("utf-8-sig", errors="replace")


def known_names():
    # Every function and constant that really exists in review_me.py.
    tree = ast.parse(read_text("review_me.py"))
    names = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def check_line(line, known):
    parts = [part.strip() for part in line.split("|")]
    if len(parts) != 4:
        return "not 4 parts"
    severity, category, name, sentence = parts
    if severity not in SEVERITIES:
        return "severity is not HIGH or LOW"
    if category not in CATEGORIES:
        return "category is not BUG or SECURITY"
    if name not in known:
        return "name is not in review_me.py"
    if not sentence:
        return "no sentence"
    return ""


known = known_names()
lines = [line.strip() for line in read_text(sys.argv[1]).splitlines() if line.strip()]
passed = []
failed = 0

for line in lines:
    problem = check_line(line, known)
    short = line if len(line) <= 70 else line[:67] + "..."
    if problem:
        failed += 1
        print("FAIL  " + short + "  (" + problem + ")")
    else:
        passed.append(line)
        print("PASS  " + short)

print()
print("Lines:", len(lines), " Passed:", len(passed), " Failed:", failed)
print()
print("Passed lines by severity and category:")
for severity in SEVERITIES:
    for category in CATEGORIES:
        count = sum(1 for line in passed if [part.strip() for part in line.split("|")][:2] == [severity, category])
        print("  " + severity + " " + category + ":", count)

sys.exit(1 if failed else 0)
