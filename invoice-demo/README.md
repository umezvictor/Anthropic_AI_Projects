# Extract Invoice Data And Catch A Total That Does Not Add Up

This folder holds three invoices, one extraction script and one checker.
`extract.py` sends one invoice to the Claude API with a JSON schema on the
request, so the answer always comes back in that shape. `check.py` is your own
code. It checks the values that a schema cannot check.

Read `SETUP.md` first if you do not have Python, the Anthropic library or an
API key yet. This demo calls the API. Each run costs less than one cent.

## Before you run anything

Put the folder somewhere short and open a terminal there:

```
cd "D:\invoice-demo"
```

Check that your key is set, without printing it. On Windows:

```
if ($env:ANTHROPIC_API_KEY) { "key is set" } else { "key is NOT set" }
```

On macOS and Linux:

```
echo ${ANTHROPIC_API_KEY:+key is set}
```

## The files

| File | What it is |
| --- | --- |
| `extract.py` | One API call. The schema goes in `output_config.format`. It saves the answer as a JSON file and prints it. |
| `check.py` | Your code, no model. It checks the shape, adds up the line items, and checks the PO number. |
| `invoice_ok.txt` | An invoice with nothing wrong. |
| `invoice_bad_total.txt` | The line items add up to 1,430.00. The invoice prints 1,450.00. |
| `invoice_no_po.txt` | An invoice with no PO number. |
| `SETUP.md` | How to install Python and the library, and set the key. |

## Run 1. A clean invoice

```
py extract.py invoice_ok.txt
```

On macOS and Linux, use `python3` instead of `py`. The answer is saved to
`invoice_ok.json`.

```
py check.py invoice_ok.json
```

Every check is OK, and the result is PASS.

## Run 2. A total that does not add up

```
py extract.py invoice_bad_total.txt
```

```
py check.py invoice_bad_total.json
```

The shape is OK. The schema guarantees that. The total fails: the line items
add up to 1,430.00, and the invoice says 1,450.00. Open the invoice and add
the items yourself: the printed total is wrong. A retry cannot fix a wrong
invoice. A person has to look.

The line that starts with `Model:` shows the model's own check, the
`conflict_detected` field, next to yours.

## Run 3. A value that is not in the invoice

```
py extract.py invoice_no_po.txt
```

```
py check.py invoice_no_po.json
```

`po_number` comes back as null, because the prompt allows null and says do not
guess. A retry cannot find a value that is not in the document. A person has to
look.

Your JSON can use different words in `description` from the video. The numbers
and the check results should be the same.

## Sources

- https://platform.claude.com/docs/en/build-with-claude/structured-outputs
- https://platform.claude.com/docs/en/build-with-claude/thinking
- https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations
