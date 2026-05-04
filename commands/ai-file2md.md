---
owner: kai
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

**Tier 1 — pdftotext**

```bash
pdftotext -layout "file.pdf" -
```

Fail signal: output empty or < 50 words.

**Tier 2 — pandoc fallback**

```bash
pandoc -f pdf -t markdown "file.pdf"
```

**Tier 3 — LLM cleanup**

Run only when Tier 1/2 output is noisy. Same rule as
`ai-web2md`: strip noise, preserve content, never infer.

**Scanned PDFs** (Tiers 1–2 both empty):  
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

```
file:       <path>
title:      <filename or first heading>
format:     pdf | docx | pptx | xlsx | csv
date:       YYYY-MM-DD
tier_used:  1 | 2 | 3 | needs_ocr
content:    <markdown>
```
