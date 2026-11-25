"""Step 4. Re-run one pass. The other two stay exactly as they were."""

import pathlib, time
from shared import ask, report_call, STRONG, ONLY_THIS_JOB, SECURITY

names = ["correctness", "security", "performance"]


def show_times(label):
    print(label)
    for name in names:
        path = pathlib.Path("out_" + name + ".txt")
        stamp = time.strftime("%H:%M:%S", time.localtime(path.stat().st_mtime))
        print("  out_" + name + ".txt   last written", stamp)
    print()


show_times("before:")

findings, tokens_in, tokens_out, stop_reason = ask(SECURITY + ONLY_THIS_JOB, STRONG)
pathlib.Path("out_security.txt").write_text(
    "model: " + STRONG + "\n" + findings, encoding="utf-8"
)
print("security pass re-run on", STRONG)
report_call(tokens_in, tokens_out, stop_reason)
print()

show_times("after:")
print("One call spent. Two results untouched.")
