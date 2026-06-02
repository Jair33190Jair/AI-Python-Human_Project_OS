---
owner: sherlock
---

# Skill 01 — Discovery

> *"Before any theory, Watson, the facts. Let us see who already
> occupies this room."*

**Purpose:** build a structured list of competitors for the
current project. No analysis, no opinions — evidence only.

**Model:** Claude Sonnet (many cheap search/extract calls).

**Inputs:**
- `<project>/03_competition/README.md` (project context:
  product, target user, geography, language(s), user's
  current assumptions)

**Output:**
- `<project>/03_competition/competitors.json`

**Search contract:** follow
`00_agents/00_toolbox/web_search.md` for every query.

---

## Procedure

1. **Read the README.** Extract: product description, target
   user, market geography, product language(s), and any
   competitor names the user already suspects.
2. **Generate 8–15 queries** — not fixed, *derived* from the
   README. Distribute across the project's languages:
   - Core category queries (what the product *is*)
   - Target-user queries (who it serves)
   - Geography-specific queries (local market names)
   - Adjacent-category queries (tools that could pivot in)
   - Queries for any competitor names the user already
     flagged (to find their ecosystem)
3. **Run the searches.** Use `tavily-search` per the toolbox
   contract. Extract with `tavily-extract` when snippets are
   too thin to capture positioning.
4. **Deduplicate.** If the same company appears under
   multiple queries, merge into one entry and list every
   query that surfaced it.
5. **Filter, don't silently drop.** If a result looks out of
   scope (wrong region, wrong segment, obvious false
   positive), include it with
   `"relevance": "possibly_irrelevant"` and a one-line
   reason. Sherlock does not hide evidence; the user audits
   the filter later.
6. **Target size:** 10–25 competitors. If fewer than 10,
   broaden queries once and retry. If still fewer, stop and
   report — a thin market is itself a finding.
7. **Write the artifact** to
   `<project>/03_competition/competitors.json`.

## Output schema

```json
{
  "search_date": "MM-YY",
  "project_languages": ["en", "de", "fr"],
  "queries_run": [
    {
      "query": "string",
      "language": "en|de|fr|...",
      "rationale": "why this query was chosen"
    }
  ],
  "total_competitors_found": 0,
  "competitors": [
    {
      "slug": "kebab-case-unique-id",
      "name": "",
      "url": "",
      "country": "",
      "product_language": ["en"],
      "one_line_positioning": "",
      "target_user": "",
      "pricing_model": "free|freemium|subscription|enterprise|unknown",
      "relevance": "direct|adjacent|possibly_irrelevant",
      "relevance_reason": "one line",
      "found_via": [
        { "query": "string", "language": "en" }
      ],
      "sources": ["https://..."]
    }
  ]
}
```

## Rules

- No fabricated entries. If a competitor's site cannot be
  verified, do not include it.
- `slug` must be stable and unique (used as filename key by
  Skill 02). Use kebab-case of the product name.
- Every competitor carries at least one source URL.
- Do not produce any narrative output alongside the JSON.
  Terse tool use, then the file, then a one-sentence
  confirmation to the user: *"Discovery complete — N
  competitors, written to `<path>`."*
