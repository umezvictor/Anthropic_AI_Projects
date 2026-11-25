# Split One Big Review Into Three Passes, One Call Each

One Python file needs a review. You will do it twice. First as one call carrying
all three jobs. Then as three calls, one job each, with your own code putting the
results together.

The point is not that three calls find more problems. The point is what three
calls let you control that one call cannot.

Read `SETUP.md` first. Nothing here runs without it.

Commands below use `py`, the Windows launcher. On macOS and Linux use `python3`.

## Before you run anything

Your terminal has to be in the folder holding these files:

```
cd "D:\review-demo"
```

If you skip this, Python answers with `can't open file ... No such file or
directory`.

## The files

| File | What it is |
| --- | --- |
| `review_me.py` | The file under review. A small order service with real problems planted in it. |
| `shared.py` | The two models, the system prompt, the three jobs, and the one call every step makes. |
| `step1_one_call.py` | One call carrying all three jobs. |
| `step2_three_passes.py` | Three calls, one job each, saved to three files. |
| `step3_pick_a_model.py` | The same three passes, with a different model per pass. |
| `step4_rerun_one_pass.py` | Re-runs the security pass alone. |
| `step5_merge.py` | Builds `report.md` from the three files. |

## Fairness

Every call uses the same system prompt and the same `MAX_TOKENS`. Only the job
and the model change.

`ONLY_THIS_JOB` tells a pass to stay inside its own job. It is added only when a
pass is one of several. `step1_one_call.py` never gets it, because telling one
call to ignore two of its own three jobs would rig the comparison.

## Run them in order

### Step 1

```
py step1_one_call.py
```

One call, all three jobs. It works. `tokens in` counts the prompt and the file
sent once. `tokens out` counts the answer. All three jobs share one limit.

### Step 2

```
py step2_three_passes.py
```

Three calls, one job each, each with its own limit. The file goes out three
times, so input tokens go up. Three files are written.

### Step 3

```
py step3_pick_a_model.py
```

Security runs on the stronger model. Correctness and performance run on the
cheaper one. A Messages API request carries one model, so one call cannot do
this at all.

Compare these findings with step 2 before you decide the trade is worth it.

### Step 4

```
py step4_rerun_one_pass.py
```

Re-runs security alone. The file times show the other two results did not move.
One call spent instead of three.

### Step 5

```
py step5_merge.py
```

Your code builds the report. It names the model under each heading. Then it
drops any finding about a function an earlier section already covered, and
prints every finding it dropped.

Read that dropped list. The rule is deliberately simple, and a simple rule can
drop a real problem: one function can have both a security bug and a slow loop.
Your code owns the rule, so you can improve it.

## Reset

Delete your folder and unzip the download again. Steps 2, 3, 4 and 5 write files
into the folder.

## Try it yourself

1. Add a fourth pass for logging. Notice that the first three files do not change.
2. Run `step2_three_passes.py`, then `step5_merge.py`, and compare that report
   with the one built after step 3.
3. Make the drop rule smarter, so it keeps two findings about the same function
   when they describe different problems.
4. Move the security pass to the cheaper model and see what the report loses.

## Documentation

- https://platform.claude.com/docs/en/api/messages
- https://platform.claude.com/docs/en/models/overview
