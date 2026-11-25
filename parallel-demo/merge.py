"""Merge the three result files into one report. Your code, not the model."""

import pathlib

sections = [
    ("Security", "out_security.txt"),
    ("Correctness", "out_correctness.txt"),
    ("Performance", "out_performance.txt"),
]

covered = set()
dropped = []
lines = ["# Review of review_me.py", ""]

for title, filename in sections:
    path = pathlib.Path(filename)
    if not path.exists():
        print("Missing file:", filename)
        continue

    lines.append("## " + title)
    lines.append("")

    subjects_here = set()
    for finding in path.read_text(encoding="utf-8").splitlines():
        finding = finding.strip()
        if not finding:
            continue
        # A finding starts with a name. Skip anything else a reviewer added.
        if finding.startswith("(") or ":" not in finding:
            continue
        subject = finding.split(":")[0].strip().lower()
        # Only drop it when an EARLIER section already covered that function.
        if subject in covered:
            dropped.append((title, finding))
            continue
        subjects_here.add(subject)
        lines.append("- " + finding)

    covered |= subjects_here
    lines.append("")

report = "\n".join(lines)
pathlib.Path("report.md").write_text(report, encoding="utf-8")
print(report)
print("Saved to report.md")
print()
print("Dropped, because an earlier section already covered that function:")
for title, finding in dropped:
    print("  [" + title + "] " + finding)
print("Total dropped:", len(dropped))
