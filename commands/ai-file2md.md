---
owner: kai
---

# /ai-file2md

Convert a local file to clean markdown.

**Argument:** one file path (`.pdf`, `.docx`, `.pptx`,
`.xlsx`, `.csv`).

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

```bash
pandoc -f pptx -t markdown "file.pptx"
```

Note: speaker notes are preserved as blockquotes.
No fallback needed.

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
