"""Step 3. A different model per pass. One call cannot do this."""

import pathlib
from shared import ask, report_call, STRONG, CHEAP, ONLY_THIS_JOB, CORRECTNESS, SECURITY, PERFORMANCE

passes = [
    ("correctness", CORRECTNESS, CHEAP),
    ("security", SECURITY, STRONG),
    ("performance", PERFORMANCE, CHEAP),
]

for name, instruction, model in passes:
    findings, tokens_in, tokens_out, stop_reason = ask(instruction + ONLY_THIS_JOB, model)
    print("=== pass:", name, " model:", model)
    report_call(tokens_in, tokens_out, stop_reason)
    print(findings)
    print()
    pathlib.Path("out_" + name + ".txt").write_text(
        "model: " + model + "\n" + findings, encoding="utf-8"
    )

print("Security ran on the stronger model. The other two ran on the cheaper one.")
print("Compare these findings with step 2 before you decide that trade is worth it.")
