"""Step 1. One call carrying all three jobs. One answer, one budget."""

from shared import ask, report_call, STRONG, CORRECTNESS, SECURITY, PERFORMANCE

instruction = CORRECTNESS + "\n\n" + SECURITY + "\n\n" + PERFORMANCE

findings, tokens_in, tokens_out, stop_reason = ask(instruction, STRONG)

print("model:", STRONG)
report_call(tokens_in, tokens_out, stop_reason)
print()
print(findings)
