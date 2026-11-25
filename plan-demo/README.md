# Run One Feature Through Plan Mode, Then Execute

This folder holds a small shop project. `refund_order` can give only a full
refund today. You ask Claude Code to add partial refunds, first in plan mode,
then for real.

Your own tests show the before and the after. Read `SETUP.md` if you do not
have Python or Claude Code yet.

## Before you run anything

Put the folder somewhere short and open a terminal there:

```
cd "D:\plan-demo"
```

Open a second terminal and go to the same folder. You use it in run 2.

## The files

| File | What it is |
| --- | --- |
| `shop/orders.py` | The two orders in the shop. |
| `shop/refunds.py` | `refund_order`. Today it refunds the full total only. |
| `tests/test_refunds.py` | Four tests. Two pass today. Two need partial refunds and fail today. |
| `SETUP.md` | How to install Python and Claude Code. |

## Run 1. The tests, then plan mode

```
py -m unittest
```

On macOS and Linux, use `python3 -m unittest`. The last line is
`FAILED (errors=2)`.

Start Claude Code in plan mode:

```
claude --permission-mode plan
```

Start Claude Code with the plan flag only. If you use a bypass flag, or your
settings set `defaultMode` to `bypassPermissions`, plan mode does not block
edits.

The status bar shows `plan mode on`. Type:

```
Add partial refunds to refund_order. A caller can pass an amount. Several partial refunds are allowed until the order total is reached. Make the tests in tests/test_refunds.py pass. Do not run the tests. I run them myself.
```

Claude reads the files and shows a plan. Then it asks how to proceed.

## Run 2. Review the plan, then approve it

Pick **Tell Claude what to change** (some versions show **No, keep planning**), and type:

```
Put the amount checks in their own function, called check_amount.
```

Claude shows a new plan. Before you approve it, go to the second terminal and
run the tests again:

```
py -m unittest
```

Still `FAILED (errors=2)`. Plan mode wrote nothing to your code.

Back in Claude Code, pick **Yes, manually approve edits**. The status bar
changes, and Claude Code asks you before each edit. Read each change, then
approve it.

## Run 3. The tests again

Type `/exit`, then:

```
py -m unittest
```

The last line is `OK`.

Your plan and your edits will use different words from the video. The test
results will be the same.

## Sources

- https://code.claude.com/docs/en/permission-modes
- https://code.claude.com/docs/en/common-workflows
