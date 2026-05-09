---
owner: kai
human_status:  # stable | needs-review | draft
model: claude-haiku-4-5-20251001  # mechanical: strip nav/footers,
                                   # apply explicit rules, structured
                                   # output — no deep reasoning needed.
---

# /ai-web2md

Fetch a URL and return its content as clean markdown.

**Argument:** one http(s) URL.

---

## Extraction

Run preflight first:

```bash
python3 ~/.claude/commands/ai-web2md/preflight.py "$ARGUMENTS"
```

If preflight blocks, report its message and stop.
Set `$URL` to the validated `url:` value.

```bash
~/.claude/lib/.venv/bin/python ~/.claude/lib/fetch.py "$URL"
```

`fetch.py` selects the right resolver automatically
(Fedlex, EUR-Lex, Basel-Stadt, PDF, Firecrawl).

Firecrawl requires user approval. If `fetch.py` exits 2,
ask before re-running:

```bash
~/.claude/lib/.venv/bin/python ~/.claude/lib/fetch.py "$URL" --allow-paid
```

Exit 1 means inaccessible or failed. Never fabricate
content.

---

## Verification

After changing `fetch.py`, resolvers, or extractors, run:

```bash
~/.claude/lib/.venv/bin/python ~/.claude/lib/smoke_fetch.py
```

Exit 0 = all resolvers pass. Any other exit = stop and
report failures before proceeding.

---

## Content completeness rules

- **Include all appendices and annexes.** Anhänge,
  annexes, schedules, end-matter — never stop at the
  last main article.
- If an annex is only referenced, include a short stub
  with the article ref and official pointer.
- No blank numbered or lettered items.

## Form / survey content

When the page is a form or survey, format every field
so it is visibly fillable in markdown:

- **Text / number input** → append answer placeholder
  on same line: `**Question text**: ___`
- **Checkbox / multi-select** → `- [ ] option`
- **Radio / single-select (Ja/Nein, pick-one)**
  → each option on its own line: `- ( ) option`
- Preserve section headers and question numbering.
- Mark required fields with `*(Pflicht)*`.

---

## Output

Return stdout from `fetch.py` verbatim.
If stdout is empty, report failure — do not output anything.
