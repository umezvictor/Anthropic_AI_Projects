"""Step 5. Your code merges the three passes, names the model, drops some repeats."""

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
    rows = pathlib.Path(filename).read_text(encoding="utf-8").splitlines()

    model = "unknown"
    if rows and rows[0].startswith("model:"):
        model = rows[0].split(":", 1)[1].strip()
        rows = rows[1:]

    lines.append("## " + title)
    lines.append("")
    lines.append("Reviewed by " + model + ".")
    lines.append("")

    subjects_here = set()
    for finding in rows:
        finding = finding.strip()
        if not finding:
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
