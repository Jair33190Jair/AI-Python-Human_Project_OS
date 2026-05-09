---
owner: kai
status: draft  # human flips to `stable` when satisfied
---

# /ai-file2md

Convert a local file to clean markdown.

**Argument:** one file path (`.pdf`, `.docx`, `.pptx`,
`.xlsx`, `.csv`).

---

## Pre-flight

Resolve the path before anything else:

```bash
FILE=$(python3 -c "from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser().resolve())" "$ARG")
```

Fail immediately if the file doesn't exist.

---

## Format dispatch

Detect format by extension, then run the matching tier.

### PDF

**Visual check — before extraction**

Render page 1, plus one content-heavy page if obvious, and inspect
the visual layout before choosing extraction mode:

```bash
pdftoppm -f 1 -l 1 -png -r 140 "file.pdf" /tmp/file2md_page
```

If the page is multi-column, extraction must preserve reading order:
left column top-to-bottom, then right column top-to-bottom.

**Tier 1 — pdftotext raw**

Use for most text PDFs, especially multi-column or sectioned PDFs.

```bash
pdftotext -raw "file.pdf" -
```

Fail signal: output empty, < 50 words, or visibly wrong reading
order against the rendered page.

**Tier 2 — pdftotext layout**

Use when raw extraction loses important table-like structure and the
rendered page is single-column or table-heavy.

```bash
pdftotext -layout "file.pdf" -
```

Fail signal: output empty, < 50 words, or column text appears joined
across the page.

**Tier 3 — pandoc fallback**

```bash
pandoc -f pdf -t markdown "file.pdf"
```

**Tier 4 — LLM cleanup**

Run only when Tier 1-3 output is noisy. Same rule as
`ai-web2md`: strip noise, preserve content, never infer.

**Scanned PDFs** (Tiers 1-3 all empty):
Flag as `needs_ocr`. Point user to a project-specific
extractor. Never fabricate content.

---

### DOCX

```bash
pandoc -f docx -t markdown "file.docx"
```

No fallback needed. If pandoc fails, report error.

---

### PPTX

**Tier 1 — pandoc** (check support first)

```bash
pandoc --list-input-formats | grep -q pptx && \
  pandoc -f pptx -t markdown "file.pptx"
```

Fail signal: command errors or output empty.

**Tier 2 — python-pptx**

```python
import sys
from pathlib import Path
from pptx import Presentation

# idx=4294967295 is the Google Slides / generic slide-number sentinel
SKIP_IDX = {4294967295}

path = Path(sys.argv[1]).expanduser().resolve()
prs = Presentation(path)

for i, slide in enumerate(prs.slides, 1):
    print(f"## Slide {i}")
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        if shape.is_placeholder:
            ph_idx = shape.placeholder_format.idx
            if ph_idx in SKIP_IDX:
                continue
            text = shape.text_frame.text.strip()
            if text:
                print(f"### {text}")
        else:
            for para in shape.text_frame.paragraphs:
                t = para.text.strip()
                if t:
                    prefix = "  " * para.level + "-"
                    print(f"{prefix} {t}")
    if slide.has_notes_slide:
        notes = slide.notes_slide.notes_text_frame.text.strip()
        if notes:
            print(f"> {notes}")
    print()
```

If python-pptx is missing: `pip install python-pptx --break-system-packages`

**Tier 3 — LLM cleanup**

Only if Tier 1/2 output is structurally noisy.
Strip noise, preserve content, never infer.

---

### XLSX / CSV

**Tier 1 — python + openpyxl**

```python
import openpyxl, sys
wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
for ws in wb.worksheets:
    print(f"## {ws.title}\n")
    rows = list(ws.iter_rows(values_only=True))
    if not rows: continue
    header = "| " + " | ".join(str(c or "") for c in rows[0]) + " |"
    sep    = "| " + " | ".join("---" for _ in rows[0]) + " |"
    print(header); print(sep)
    for row in rows[1:]:
        print("| " + " | ".join(str(c or "") for c in row) + " |")
    print()
```

**Tier 2 — libreoffice fallback (xlsx only)**

```bash
libreoffice --headless --convert-to csv "file.xlsx"
```

Then render CSV as a markdown table.

---

## Output

Always write the markdown to a file **next to the source**
(same directory, same base name, `.md` extension) before
printing anything to chat.

Prepend a YAML frontmatter block before the content:

```yaml
---
title: "<first heading or filename>"
source_url: "file://<absolute_path>"
retrieved_at: MM-YY
extraction_method: <tier-N | needs_ocr>
warnings:
extraction_status: success
---
```

Set `extraction_status: needs_ocr` when the file is
scanned and OCR tooling is missing.

Chat summary after writing:

```
file:       <path>
title:      <filename or first heading>
format:     pdf | docx | pptx | xlsx | csv
date:       MM-YY
tier_used:  1 | 2 | 3 | 4 | needs_ocr
```

## Acceptance Gate

After writing the `.md`, stop and ask the human to review it.
Do not hand the file to a downstream analysis command yet.
This gate belongs here, not in project-specific analysis commands.

Ask for one of two decisions:

- `accepted`: the markdown is good enough for downstream use.
- `retry`: the markdown is not good enough; collect the concrete
  issue, adapt the extraction or cleanup path, rewrite the same
  `.md`, and ask again.

On `retry`, build visual awareness of the input before changing
anything:

- Inspect the source layout directly: render relevant PDF pages,
  slides, sheets, or an equivalent preview for the file type.
- Identify the concrete extraction failure against that visual
  source, not just against the flawed markdown.
- Plan the smallest extraction or cleanup adaptation that addresses
  the failure.
- Apply the adaptation only when it should not worsen results for
  earlier files processed through the same script or tier.
- If no adaptation is available without meaningful regression risk,
  tell the human and leave the script and `.md` unchanged.

When an adaptation is safe, make it, rerun `/ai-file2md` on the same
source, rewrite the `.md`, and ask for feedback again.

Repeat until the human says `accepted` or the source is blocked
(`needs_ocr`, unreadable, unsupported, or missing tooling).

If another command or agent invoked `/ai-file2md`, return
`Review: pending human acceptance` to that caller and stop there.

Optional: use a cheap AI reviewer or subagent before the human
review to catch obvious extraction defects. That reviewer may
recommend `retry`, but only the human can approve `accepted`.

Final chat output after acceptance:

```text
Created: <path>
Review: accepted by human
Tier: <tier_used>
Notes: <one sentence, only if useful>
```
