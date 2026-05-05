---
owner: kai
human_status:  # stable | needs-review | draft
model: claude-haiku-4-5-20251001  # mechanical: strip nav/footers,
                                   # apply explicit rules, structured
                                   # output — no deep reasoning needed.
---

# /ai-web2md

Fetch a URL and return its content as clean markdown.

**Argument:** one URL.

---

## Extraction

```bash
~/.claude/helpers/.venv/bin/python ~/.claude/helpers/fetch.py "$URL"
```

`fetch.py` selects the right path automatically:

- **Fedlex** → metadata → XML filestore → markdown.
- **EUR-Lex** → CELEX → CELLAR XHTML → markdown.
- **Basel-Stadt** → OpenDataSoft → markdown.
- **PDF URLs** → pdftotext, OCR if needed.
- **Everything else** → Firecrawl only after user
  approval. If `fetch.py` exits 2, ask before re-running:

```bash
~/.claude/helpers/.venv/bin/python ~/.claude/helpers/fetch.py "$URL" --allow-paid
```

Exit 1 means inaccessible or failed. Never fabricate
content.

---

## Verification

After changing `fetch.py`, resolvers, or extractors, run:

```bash
~/.claude/helpers/.venv/bin/python ~/.claude/helpers/smoke_fetch.py
```

---

## Content completeness rules

- **Include all appendices and annexes.** Anhänge,
  annexes, schedules, end-matter — never stop at the
  last main article.
- If an annex is only referenced, include a short stub
  with the article ref and official pointer.
- No blank numbered or lettered items.

---

## Output

Return stdout from `fetch.py` verbatim.
