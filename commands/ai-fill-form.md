---
owner: kai
model: claude-sonnet-4-6
---

# /ai-fill-form

Fill an online form from a locally answered markdown file
produced by `/ai-web2md`.

**Argument:** path to the filled markdown file.

---

## Input format (produced by /ai-web2md)

- Text/number: `**Label** *(Pflicht)*: answer` — blank if `___`
- Checkbox: `- [x] Option` (checked) / `- [ ] Option` (unchecked)
- Radio: `- (x) Option` (selected) / `- ( ) Option` (not selected)

---

## Steps

**1. Read the markdown file.**

```bash
cat "$ARGUMENTS"
```

Extract:
- `source_url` from frontmatter
- All answers: text values, checked boxes, selected radios.
  Skip any field whose value is still `___` or blank.

**2. Inspect the live form.**

```bash
~/.claude/lib/.venv/bin/python ~/.claude/lib/form_fill.py \
  --inspect "$source_url"
```

Output: JSON array `[{label, selector, type, required, ...}]`.

Use Google Chrome when Chromium behaves differently from the
human browser:

```bash
~/.claude/lib/.venv/bin/python ~/.claude/lib/form_fill.py \
  --browser chrome \
  --inspect "$source_url"
```

If Chrome is installed outside Playwright's known channels, use
the binary directly:

```bash
~/.claude/lib/.venv/bin/python ~/.claude/lib/form_fill.py \
  --executable-path "/usr/bin/google-chrome" \
  --inspect "$source_url"
```

**3. Map answers → selectors.**

For each field in the JSON, find the matching answer from step 1
by label similarity (fuzzy — labels in the live form often
differ slightly from the markdown).

For repeated radio labels like `Ja` / `Nein`, do not match by
option label alone. Use the JSON `group` value and DOM order:
pair each selected markdown radio with the next unmatched live
radio group in the same section. If the order is unclear, skip
that radio and report it.

Produce a mapping array:

```json
[
  {"selector": "input[name='q1']", "type": "text",     "value": "25"},
  {"selector": "#sector-it",       "type": "checkbox",  "value": true},
  {"selector": "#radio-ja",        "type": "radio",     "value": true}
]
```

Rules:
- **Text/number:** value is the answer string.
- **Checkbox:** `true` if `[x]`, `false` if `[ ]`.
  Include both — the filler sets or clears them.
- **Radio:** only include the selected option (`value: true`).
  Never set `value: false` on a radio — just omit it.
- **Select:** match option text → use `option.value` from the JSON.
- Skip fields with no answer in the markdown.

**4. Write mapping to temp file.**

Write the mapping JSON to `/tmp/ai_form_fill_mapping.json`.

**5. Stop for external-fill approval.**

Before opening the browser against a third-party form, report:
- mapping file path
- number of mapped actions
- skipped or ambiguous fields
- the exact destination domain

Then stop unless the user explicitly approves filling the
external form with the local questionnaire data.

Required approval wording:

```text
I approve filling the <domain> form with the questionnaire data.
```

**6. Fill the form after approval.**

```bash
~/.claude/lib/.venv/bin/python ~/.claude/lib/form_fill.py \
  --fill "$source_url" /tmp/ai_form_fill_mapping.json
```

The browser opens visually. Fields are filled one by one.
The script pauses — the user reviews and submits in the browser.

If the site works better in Google Chrome, add
`--browser chrome` before `--fill`. Default is Playwright
Chromium. If needed, use `--executable-path` with the
local browser binary instead.

**7. Report any skipped fields** (selector not found, field blank,
or type mismatch) so the user can fill them manually.

---

## Known limitation

Multi-page/wizard forms: the inspector captures all fields
visible in the initial DOM. If the form reveals fields
progressively, later pages may not be filled automatically.
Flag this to the user if the form has a next/continue button.
