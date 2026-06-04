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
(same directory, same base name, `.md` extension) using a
script — never by having the LLM reconstruct the content.

```bash
OUTFILE="${FILE%.*}.md"
TITLE=$(basename "$FILE" | sed 's/\.[^.]*$//')
MONTH_YY=$(date +%m-%y)

{
cat <<FRONT
---
title: "$TITLE"
source_url: "file://$FILE"
retrieved_at: $MONTH_YY
extraction_method: <tier-N | needs_ocr>
warnings:
extraction_status: success
---
FRONT
# Fix soft-hyphen line breaks (e.g. "stipu-\nlante" → "stipulante")
<extraction_command> | perl -0pe 's/(\w)-\n(\w)/$1$2/g'
} > "$OUTFILE"
```

Replace `<extraction_command>` with the winning tier command.
Set `extraction_status: needs_ocr` when the file is scanned
and OCR tooling is missing.

**PDF only — structure formatting (run after writing)**

Applies heading markup, bullet normalisation, and blank-line
spacing. Skip if pandoc already emitted valid markdown (Tier 3).

```python
import re

src = "<OUTFILE>"
lines = open(src).readlines()
out = []
fm_count = 0
frontmatter_done = False

def heading(s):
    if re.match(r'^[A-Z] [A-ZÀÈÉÌÍÒÓÙÚ]', s):  return '## '
    if re.match(r'^\d+\.\d+\.\d+ ', s):          return '#### '
    if re.match(r'^\d+\.\d+ ', s):               return '#### '
    if re.match(r'^\d+ [A-ZÀÈÉÌÍÒÓÙÚ]', s):      return '### '
    if re.match(r'^\d{4} ', s):                   return '### '  # e.g. "0850 Cyber..."
    return None

for line in lines:
    s = line.rstrip('\n')
    if s == '---':
        fm_count += 1
        out.append(s)
        if fm_count == 2:
            frontmatter_done = True
            out.append('')
        continue
    if not frontmatter_done:
        out.append(s)
        continue

    s = s.replace('§ ', '- ')
    pfx = heading(s)
    if pfx:
        if out and out[-1] != '':
            out.append('')
        out.append(pfx + s)
        out.append('')
    else:
        out.append(s)

# collapse runs of 2+ blank lines to 1
result, blanks = [], 0
for l in out:
    if l == '':
        blanks += 1
        if blanks == 1: result.append(l)
    else:
        blanks = 0
        result.append(l)

open(src, 'w').write('\n'.join(result) + '\n')
```

Chat summary after writing:

```
file:       <path>
title:      <filename or first heading>
format:     pdf | docx | pptx | xlsx | csv
date:       MM-YY
tier_used:  1 | 2 | 3 | 4 | needs_ocr
```

---

## Visual Review & Repair (mandatory — runs before Acceptance Gate)

After writing the initial `.md`, render **every page** of the source
and compare it directly against the markdown output. This step is
not optional and is not deferred to `retry`.

**PDF — render all pages:**

```bash
pdftoppm -f 1 -l 999 -png -r 140 "file.pdf" /tmp/file2md_review
```

Read each rendered page and cross-check the corresponding section
in the `.md`. For each page, look for:

- **Fused text** — words or nav items joined without spaces
  (e.g. "How it worksPricing") → split correctly
- **Page artifacts** — running headers/footers (e.g. "Doc Title 04")
  → remove
- **Wrong heading hierarchy** — ALL CAPS labels that are subsections
  should be `###`, not flat text or auto-promoted `##`
- **Missing section headings** — section title and section label
  extracted as a single fused line → split into `## N — Title`
- **Layout structure lost** — multi-column grids (colour swatches,
  feature cards, DO/DON'T pairs) that the extractor flattened
  → reconstruct as tables, `**Label:** value` pairs, or blockquotes
- **Image-only content** (logos, illustrations, mockups) — note
  with `*[visual: description]*`; never fabricate text content
- **Noise characters** — stray symbols (✕, §, bullet artifacts)
  that do not represent real content → remove

After identifying all issues, rewrite the `.md` in one pass with
all repairs applied. Do not ask the human between discovery and
repair — complete the full fix first.

For non-PDF formats (DOCX, PPTX, XLSX), apply the same visual
check using available previews or slide/sheet structure, and repair
the same categories of issues.

---

## Acceptance Gate

After the Visual Review & Repair pass is complete, present the
`.md` to the human for final approval. Do not hand the file to a
downstream analysis command yet.

Ask for one of two decisions:

- `accepted`: the markdown is good enough for downstream use.
- `retry`: the markdown is not good enough; collect the concrete
  issue, re-inspect the relevant source pages, apply the smallest
  safe fix, rewrite the `.md`, and ask again.

Repeat until the human says `accepted` or the source is blocked
(`needs_ocr`, unreadable, unsupported, or missing tooling).

If another command or agent invoked `/ai-file2md`, return
`Review: pending human acceptance` to that caller and stop there.

Final chat output after acceptance:

```text
Created: <path>
Review: accepted by human
Tier: <tier_used>
Notes: <one sentence, only if useful>
```
