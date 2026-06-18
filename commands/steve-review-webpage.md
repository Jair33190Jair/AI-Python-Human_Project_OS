---
description: Screenshot an HTML page and review each section for tone, visuals, consistency, duplication, conversion fit, and drift from the content source.
argument-hint: <html_file> <written_guide> <visual_guide> [content_file]
status: draft
owner: steve
---

# steve-review-webpage

Review a webpage section by section. Screenshot the HTML via
Playwright, compare visible copy and visuals against the written and
visual guides, and optionally check drift from the canonical content
source file.

This command was created and should be maintained through
`/bob-create-command`; patch this file instead of inventing a parallel
review workflow.

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

## Phase 3 — Section Map

Create a short section map from the visible page and the HTML:

- section name / anchor / approximate scroll position;
- main decision-stage job;
- primary promise, proof, objection, or CTA;
- matching content-source section if `$CONTENT_FILE` exists.

Use this map to keep findings grounded. Review only the page in front
of you, not an imagined future page.

## Phase 4 — Review

Use the guides as sources, but apply product judgment. If the guide is
too conservative, vague, or mismatched to the page's buyer, say so
instead of blindly enforcing it. Do not invent legal, privacy, hosting,
processor, or security facts.

### Trim And Duplication
Check before anything else. Trim findings outweigh additive
recommendations.

- Identify sections that say the same thing at the same decision stage with no new information. Apply the rule: same emotional stage + adjacent + no new info = flag for cut.
- Identify lists or labels repeated verbatim across adjacent sections.
- Decide whether repeated ideas earn their place because they catch the
  visitor at a different decision stage.
- Flag defensive FAQs or edge-case answers that block no realistic
  first-time visitor.
- Healthy repetition is fine — note why it works instead of flagging it.

### Section Fit
For each reviewed section, ask:

- What job does this section do at this scroll depth?
- Is that job already done better by a previous or later section?
- Is the section understandable without knowing the internal product
  architecture?
- Does it make the next section feel natural, or does it stall the page?

### Tone And Wording

- Check whether the copy sounds calm, human, and confident, not timid,
  generic, defensive, or machine-translated.
- Prefer clear product language over abstract SaaS labels.
- For AI products, check whether AI is named plainly where trust needs
  it. Do not hide AI to seem safer; do not add AI spectacle.
- Check micro-phrasing for awkward repetition, e.g. adjacent words with
  the same stem or translated compounds that sound unnatural.

### Trust And Claims

- Identify the visitor's real anxiety in this section.
- Check whether trust claims are specific enough to reassure without
  over-explaining.
- Flag any privacy, client-data, clinical-responsibility, hosting,
  processor, retention, encryption, or compliance claim that needs Saul
  review before publish.
- When a technical explanation is needed, prefer one plain visitor-facing
  sentence over architecture detail or diagrams unless the page is
  explicitly a technical trust page.

### Visuals

- Does the visual support the section's job, or does it imply a larger
  promise than the copy can support?
- Does the section read as proof, emotion, product function, or trust?
  Is that the intended job?
- Check focal clarity, hierarchy, brand palette, typography, density,
  image subject, and whether visual claims match V1 scope.

### Conversion
Rate 1–5 with one-sentence rationale. Focus on what blocks the target persona from acting — not what could be added.

- What specific anxiety or objection does this persona carry that the page hasn't resolved above the fold?
- Is the CTA ask proportionate to the trust built so far?

### Persona fit
- Does the copy speak to the specific ICP or generic SaaS?
- Are trust signals appropriate to the persona? Derive expected signals from `$WRITTEN_GUIDE` if it defines them.

### Written content (against `$WRITTEN_GUIDE`)
- Voice and tone compliance
- Preferred vs. avoided vocabulary used correctly?
- Grammar and spelling

### Visual brand (against `$VISUAL_GUIDE`, from screenshot)
- Colour palette and typography
- Composition and focal clarity
- Brand violations (wrong colours, stock photos, AI imagery, dense layouts)

### Content drift (only if `$CONTENT_FILE` provided)
- Sections in HTML missing from content file, or vice versa
- Wording differences between rendered HTML and content source
- FAQ visible text must match FAQ JSON-LD when the page includes
  structured data.

## Output rules

- Lead with one line: **Pass / Needs work / Blocked** and a one-sentence summary
- Follow with the rubric sections; omit sections with no findings
- For targeted reviews, lead with the requested sections and keep global
  findings short.
- For each finding, name the section and quote the exact text or describe
  the specific visual.
- **Trim and duplication findings come before additive recommendations.**
  Surface what to cut first.
- Separate `Change now`, `Maybe later`, and `Needs Saul/Bob review` when
  that distinction matters.
- Flag conversion blockers and safety-line violations prominently
- Do not restate what passed unless it informs a fix

## Hard rules

- Default to review only. Edit files only when the user explicitly asks
  you to apply the changes after the review.
- Do not invent factual claims. If a guide rule seems wrong for the
  buyer or page, flag it as a recommendation instead of treating it as
  settled policy.
- Screenshot file is a review artefact; warn the user if it already exists and will be overwritten
- Prefer the canonical content source over editing HTML directly when a
  content file is provided.
