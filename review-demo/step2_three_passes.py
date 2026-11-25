"""Step 2. The same job as three calls. One job each, and a budget each."""

import pathlib
from shared import ask, report_call, STRONG, ONLY_THIS_JOB, CORRECTNESS, SECURITY, PERFORMANCE

passes = [
    ("correctness", CORRECTNESS),
    ("security", SECURITY),
    ("performance", PERFORMANCE),
]

for name, instruction in passes:
    findings, tokens_in, tokens_out, stop_reason = ask(instruction + ONLY_THIS_JOB, STRONG)
    print("=== pass:", name, " model:", STRONG)
    report_call(tokens_in, tokens_out, stop_reason)
    print(findings)
    print()
    pathlib.Path("out_" + name + ".txt").write_text(
        "model: " + STRONG + "\n" + findings, encoding="utf-8"
    )

print("Three files written. Each pass now has its own result on disk.")
