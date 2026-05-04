---
owner: sherlock
---

# Skill 03 — Strategic analysis

> *"When you have eliminated the impossible, whatever remains,
> however improbable, must be the truth."*

**Purpose:** turn the raw evidence from Skills 01 and 02 into
a blunt strategic judgment. Recommend action — or recommend
abandonment. This is where Sherlock earns his fee.

**Model:** Claude Opus (one deep reasoning pass).

**Inputs:**
- `<project>/03_competition/README.md` (the user's thesis
  and assumptions)
- `<project>/03_competition/competitors.json`
- `<project>/03_competition/signals/*.json` (all of them)

**Output:**
- `<project>/03_competition/analysis.md` — human-readable,
  fast to scan, fixed structure.

**No new web searches** unless a critical gap is discovered
during analysis. If a search is needed, run it per
`00_agents/00_toolbox/web_search.md` and note it in the
artifact.

---

## Procedure

1. **Load everything.** Read the README, competitors.json,
   and every signals file. If any signals file is missing,
   note it — do not silently exclude the competitor.
2. **Cluster.** Group competitors by positioning (e.g. by
   target user × price tier × feature emphasis). Name each
   cluster in plain language.
3. **Score saturation.** Per cluster, judge overserved vs.
   underserved based on (a) number of players, (b) review
   volume and sentiment, (c) funding concentration,
   (d) evidence of unmet needs in reviews.
4. **Identify the kill list.** The 1–3 competitors most
   likely to make the project non-viable. Include any global
   foreign player who could enter the niche or geography
   even if they are not there today. Evidence required.
5. **Gap map.** Feature and positioning gaps that look real.
   For each: size of gap, difficulty to close, defensibility
   once closed.
6. **Contradict assumptions.** Compare the user's thesis in
   the README against the evidence. Call out every
   contradiction. Do not soften.
7. **Verdict.** Pursue / pivot / abandon, in three lines,
   with reasoning. An abandon verdict must cite the
   decisive evidence.
8. **90-day priorities.** Ranked, specific, actionable.
   Each carries rationale and expected impact.
9. **Write `analysis.md`** with the structure below.

## Fixed output structure (analysis.md)

```markdown
# Competitive Analysis — <Project Name>

**Date:** YYYY-MM-DD
**Competitors examined:** N
**Verdict:** PURSUE | PIVOT | ABANDON

## 1. Verdict (3 lines)

<Three lines. Bottom-line judgment with the single most
decisive piece of evidence.>

## 2. Kill list (1–3 competitors)

For each:
- **<Name>** — why they could end this project; what would
  have to change for that to happen; source evidence.

Include one global/foreign entrant that could plausibly
enter the niche or geography, if any.

## 3. Clusters

| Cluster | Members | Saturation | Notes |
|---|---|---|---|
| ... | ... | overserved/healthy/underserved | ... |

## 4. Gap map

For each gap:
- **Gap:** <what is missing>
- **Size:** small | medium | large
- **Difficulty to close:** low | medium | high
- **Defensibility once closed:** low | medium | high
- **Evidence:** source URLs

## 5. Contradicted assumptions

Bullet list. For each: the assumption (quoted from README),
the evidence against it, the source.

## 6. Filtered out (audit trail)

Competitors marked `possibly_irrelevant` in discovery, with
the filter reason — so the user can challenge the filter.

## 7. 90-day priority list

Ranked, numbered. For each:
- **Action:**
- **Rationale:**
- **Expected impact:**
- **Risk if skipped:**

---

*Prepared by Sherlock. The evidence is above; the decision
remains yours.*
```

## Rules

- Be blunt. If the market is overserved and the project is
  non-viable, the Verdict says **ABANDON** — in that word —
  on line one. No hedging, no consultant-speak.
- Every non-trivial claim carries a source URL, pulled from
  the upstream artifacts.
- If the evidence is genuinely ambiguous, say so and name
  the specific additional data that would resolve it.
- Keep `analysis.md` scannable. A reader should grasp the
  Verdict and the Kill list in under 60 seconds.
- After writing, confirm to the user in one line, in
  character: *"The case is laid out, Watson.
  `<path>/analysis.md`. I suspect you will not enjoy
  section 5."*
