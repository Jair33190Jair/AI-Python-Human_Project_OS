---
owner: sherlock
---

# Skill 02 — Signal gathering

> *"Data, data, data. I cannot make bricks without clay."*

**Purpose:** for each competitor in `competitors.json`,
gather the signals that tell us how serious they are, how
the market feels about them, and where they might be
vulnerable. Facts only — analysis happens in Skill 03.

**Model:** Claude Sonnet (many targeted search/extract calls).

**Inputs:**
- `<project>/03_competition/competitors.json`
- `<project>/03_competition/README.md` (for market context,
  especially regulatory/compliance cues)

**Output:**
- `<project>/03_competition/signals/<slug>.json` — one file
  per competitor (so the user can re-run one competitor
  without redoing the rest)

**Search contract:** follow
`00_agents/00_toolbox/web_search.md` for every query.

---

## Invocation modes

The skill can be invoked for **all competitors** (default)
or for a **subset** (user names specific slugs, or tells
Sherlock to redo only competitors marked `possibly_irrelevant`).
Ask the user which mode when entering the skill. Default to
all if they do not answer.

## Per-competitor procedure

For each competitor, run the following inquiries. Record
every non-trivial claim with a source URL. When a signal is
genuinely unavailable, record `"unknown"` — never invent.

1. **Reviews & sentiment**
   - G2, Capterra, Trustpilot, Product Hunt, Reddit,
     HackerNews, App Store / Play Store (if applicable).
   - Capture: aggregate rating, review count, 3–5
     representative quotes (positive and negative), common
     complaints, common praise.
2. **Traction proxies**
   - Funding rounds (Crunchbase, press releases), approximate
     headcount (LinkedIn), customer counts if publicly
     claimed, press mentions in last 12 months.
3. **Regulatory & compliance posture**
   - Certifications relevant to the project's domain
     (e.g. HIPAA, GDPR, SOC2, Swiss DPA, FINMA, ISO 27001 —
     pick what matters for the project).
   - Explicit compliance claims on their site.
4. **Market position**
   - Rough category positioning: leader / challenger /
     niche / new entrant. Evidence only — if unclear, say so.
   - Geographic coverage (countries served).
5. **Recent product moves (last 12 months)**
   - Feature launches, pricing changes, partnerships,
     acquisitions, layoffs, pivots.
6. **Red flags**
   - Lawsuits, data breaches, regulatory actions, sudden
     team changes, app store delisting, dead blog, broken
     signup flow, etc.

## Output schema (per competitor)

```json
{
  "slug": "kebab-case-id",
  "name": "",
  "collected_on": "YYYY-MM-DD",
  "reviews": {
    "g2":        { "rating": null, "count": null, "url": "" },
    "capterra":  { "rating": null, "count": null, "url": "" },
    "trustpilot":{ "rating": null, "count": null, "url": "" },
    "other":     [ { "platform": "", "rating": null, "count": null, "url": "" } ],
    "sentiment_summary": "",
    "quotes": [
      { "text": "", "stance": "positive|negative|neutral", "source": "" }
    ],
    "common_complaints": [],
    "common_praise": []
  },
  "traction": {
    "funding_total_usd": null,
    "last_round": { "stage": "", "amount_usd": null, "date": "", "source": "" },
    "headcount_estimate": null,
    "customers_claimed": null,
    "press_mentions_12mo": [ { "title": "", "url": "", "date": "" } ]
  },
  "compliance": {
    "certifications": [],
    "claimed_on_site": [],
    "sources": []
  },
  "position": {
    "category_role": "leader|challenger|niche|new_entrant|unknown",
    "geographies": [],
    "evidence": []
  },
  "recent_moves": [
    { "date": "YYYY-MM", "type": "launch|pricing|partnership|acquisition|layoffs|pivot|other", "summary": "", "source": "" }
  ],
  "red_flags": [
    { "severity": "low|medium|high", "summary": "", "source": "" }
  ],
  "unknowns": [
    "fields that could not be verified and why"
  ]
}
```

## Rules

- One file per competitor, named `<slug>.json`.
- Every numeric claim carries a source URL. No URL → the
  field is `"unknown"`.
- Do not score, rank, or recommend anything. That is Skill 03's job.
- At the end, confirm to the user in one line:
  *"Signals gathered for N/M competitors. M-N could not be
  completed — see `unknowns` in each file."*
