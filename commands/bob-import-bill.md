---
description: Import one Infomaniak, Exoscale, or spusu PDF invoice into the nearest expense register.
argument-hint: <invoice.pdf> [--dry-run]
status: draft  # human flips to `stable` when satisfied
owner: bob
---

# /bob-import-bill

Rename one supported PDF invoice and add its minimal accounting row to the
nearest ancestor `expenses_register.csv`.

## Arguments

- Required: one local `.pdf` path.
- Optional: `--dry-run` validates and prints the planned result without writes.

Reject missing files, extra paths, and unsupported options.

## Execute

Run:

```bash
python3 ~/.claude/commands/bob-import-bill/import_bill.py <invoice.pdf> [--dry-run]
```

The script owns extraction, validation, renaming, duplicate detection, register
updates, rollback, and final verification. Print its output verbatim.

## Contract

The nearest ancestor register must have exactly:

```csv
date,vendor,bill_number,category,amount_chf
```

Supported vendors: Infomaniak, Exoscale, and spusu. The script extracts text locally
with `pdftotext`; do not invoke `/ai-file2md` or infer missing invoice values.

Canonical dates and filenames use ISO format:

```text
YYYY-MM-DD_vendor_bill-number.pdf
```

## Completion

Success requires the canonical PDF to exist and exactly one matching register
row after the write. Treat `Already imported` as success.

Stop without changes when the script reports `Blocked:`. Never repair the CSV,
overwrite a destination, or add support for a changed invoice layout during an
import run.

## Output

Return only the script output. Do not restate invoice details or produce a
Markdown copy.
