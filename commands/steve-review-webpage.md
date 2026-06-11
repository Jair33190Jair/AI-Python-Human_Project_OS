---
description: Screenshot an HTML page and review it against written and visual content guides. Reports above-fold clarity, conversion likelihood, persona fit, brand compliance, and content drift.
argument-hint: <html_file> <written_guide> <visual_guide> [content_file]
status: draft
owner: steve
---

# steve-review-webpage

Review a webpage against its content guides. Screenshots the HTML via Playwright, evaluates written voice and visual brand against the loaded guides, and optionally checks for drift from the canonical content source file.

## Arguments

| Pos | Name | Required | Description |
|---|---|---|---|
| 1 | `$HTML_FILE` | yes | Path to the HTML file (absolute or project-relative) |
| 2 | `$WRITTEN_GUIDE` | yes | Path to the written content guide |
| 3 | `$VISUAL_GUIDE` | yes | Path to the visual content guide |
| 4 | `$CONTENT_FILE` | no | Canonical content source file (for drift check) |

## Phase 0 — Preflight

Run:
```bash
python3 ~/.claude/commands/steve-review-webpage/preflight.py "$HTML_FILE" "$WRITTEN_GUIDE" "$VISUAL_GUIDE" "$CONTENT_FILE"
```

If preflight exits non-zero, stop and print its output verbatim.

If preflight reports `screenshot_exists: yes — will overwrite`, warn the user before continuing.

Read `$HTML_ABS` and `$SCREENSHOT_DESKTOP` from preflight output.

## Phase 1 — Screenshot

Run:
```bash
~/.claude/lib/.venv/bin/python ~/.claude/commands/steve-review-webpage/screenshot.py "$HTML_ABS" "$SCREENSHOT_DESKTOP" 1440 900
```

If the venv is unavailable:
```
Blocked: venv not found — run: bash ~/.claude/lib/bootstrap.sh
```

If `$SCREENSHOT_DESKTOP` was not created after the run, stop:
```
Blocked: screenshot failed — check playwright output above
```

## Phase 2 — Load sources

Load in parallel:
- HTML file (source text for written review)
- `$WRITTEN_GUIDE`
- `$VISUAL_GUIDE`
- `$CONTENT_FILE` if provided
- `$SCREENSHOT_DESKTOP` PNG (visual review)

## Phase 3 — Review

Evaluate using the loaded guides only. Do not invent rules not present in the guides.

### Above the fold
- Value proposition legible within 3 seconds?
- CTA visible and unambiguous before scroll?

### Conversion
Rate 1–5 with one-sentence rationale: how likely is a first-time visitor matching the target persona (as defined in `$WRITTEN_GUIDE`) to take the primary CTA action?

### Persona fit
- Does the copy speak to the specific ICP or generic SaaS?
- Are trust signals appropriate to the persona? Derive expected signals from `$WRITTEN_GUIDE` if it defines them.

### Written content (against `$WRITTEN_GUIDE`)
- Voice and tone compliance
- Preferred vs. avoided vocabulary used correctly?
- Grammar and spelling
- Redundancies that dilute the message

### Visual brand (against `$VISUAL_GUIDE`, from screenshot)
- Colour palette and typography
- Composition and focal clarity
- Brand violations (wrong colours, stock photos, AI imagery, dense layouts)

### Content drift (only if `$CONTENT_FILE` provided)
- Sections in HTML missing from content file, or vice versa
- Wording differences between rendered HTML and content source

## Output rules

- Lead with one line: **Pass / Needs work / Blocked** and a one-sentence summary
- Follow with the rubric sections; omit sections with no findings
- Flag conversion blockers and safety-line violations prominently
- Quote offending text or describe the visual element specifically — no vague observations
- Do not restate what passed unless it informs a fix

## Hard rules

- Never edit the HTML, content, or guide files
- Do not add guide rules beyond what the loaded files contain
- Screenshot file is a review artefact; warn the user if it already exists and will be overwritten
