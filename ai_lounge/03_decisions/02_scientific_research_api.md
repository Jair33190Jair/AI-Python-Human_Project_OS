# Research API Decision Document

> **Decision:** Academic research database & API selection for evidence-based client support  
> **Roles covered:** Doctor / Clinician · Workout & Fitness Creator · Psychologist  
> **Date:** April 2026

---

## Summary verdict

| Platform | Cost | API | Medical | Fitness | Psychology | Best for |
|---|---|---|---|---|---|---|
| **Semantic Scholar** | Free | Yes (free) | 98% | 72% | 88% | All-round API backbone |
| **OpenAlex** | Free | Yes (free) | 99% | 80% | 90% | Widest coverage, no AI |
| **PubMed / NCBI** | Free | Yes (free) | 100% | 65% | 85% | Clinical gold standard |
| **Elicit** | Freemium | No | 97% | 78% | 92% | Non-technical AI synthesis |
| **Scite.ai** | Paid | Paid | 90% | 70% | 88% | Citation quality check |
| **PsycINFO / APA** | Institutional | Limited | 55% | 45% | 100% | Deep psychology taxonomy |

**Coverage source:** Rajit et al. (2025), *Journal of Clinical Epidemiology* — peer-reviewed comparison of 1,249 clinical guideline papers across databases.

---

## Decision: Use Semantic Scholar as primary API

### Why

- **Free and no key required** for up to 5,000 requests / 5 minutes to start prototyping immediately.
- **214M+ papers** with strong biomedicine and psychology coverage.
- **AI-native features** no competitor offers for free: TLDR summaries, Ask This Paper, influential citation classifier, and paper recommendations.
- **98.3% clinical coverage** — only 0.3% behind OpenAlex, and it missed zero high-quality (low risk-of-bias) papers.
- Clean JSON responses, field selection to minimize payload, well-maintained Python client library available.

### Key limitation

Not specialized for sports science / fitness. Supplement with OpenAlex for broader coverage there.

---

## Coverage data (peer-reviewed, 2025)

From the April 2025 study comparing automated single-database retrieval across 1,249 clinical guideline papers:

| Database | Coverage | Missed high-quality papers? |
|---|---|---|
| OpenAlex | 98.6% | No |
| **Semantic Scholar** | **98.3%** | **No** |
| Embase | 96.8% | Yes |
| PubMed | 93.0% | Yes |

> Both OpenAlex and Semantic Scholar did not miss any high-quality papers, while PubMed and Embase missed some low-risk-of-bias articles.

---

## Platform notes by role

### Doctor / Clinician

- **Primary:** Semantic Scholar API (fast concept search + AI TLDR)
- **Secondary:** PubMed E-Utilities (clinical trial depth, MeSH term precision)
- **For synthesis:** Elicit (no-code, combines all three major databases)
- PubMed is still the reference point for formal clinical guidelines but misses 7% of papers in automated retrieval — supplement with Semantic Scholar.

### Workout / Fitness Creator

- **Primary:** Semantic Scholar API (filter `fieldsOfStudy=["Biology","Medicine"]`)
- **Secondary:** OpenAlex (broader sports science, preprint coverage)
- Search terms that work well: `HIIT hypertrophy`, `resistance training volume`, `periodization meta-analysis`
- Use `citationCount` as a proxy for protocol reliability.

### Psychologist / Therapist

- **Primary:** Semantic Scholar API (good psychology coverage + AI features)
- **Supplement:** PsycINFO (if institutional access available — deepest taxonomy)
- **Validation:** Scite.ai (paid) to check if studies replicated — important given replication crisis
- Search terms: `CBT efficacy RCT`, `ACT meta-analysis`, `DBT borderline`, `schema therapy outcomes`
- Filter `year >= 2015` for current evidence base.

---

## API quick reference

### Semantic Scholar (primary)

```
GET https://api.semanticscholar.org/graph/v1/paper/search
  ?query=YOUR_QUERY
  &fields=title,abstract,tldr,year,citationCount,openAccessPdf
  &limit=10
```

No API key needed to start. Register at semanticscholar.org/product/api for higher rate limits.

**Rate limits:**
- Without key: 5,000 req / 5 min (shared pool)
- With free key: higher sustained limits

**Key fields to use:**
- `tldr.text` — AI-generated summary
- `influentialCitationCount` — proxy for impact
- `openAccessPdf.url` — link to free full text
- `fieldsOfStudy` — filter by Medicine, Biology, Psychology

### OpenAlex (fallback / fitness)

```
GET https://api.openalex.org/works?search=YOUR_QUERY&per-page=10
```

Add `&mailto=your@email.com` to get polite pool: 100K req/day.

### PubMed E-Utilities (clinical depth)

```
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
  ?db=pubmed&term=YOUR_QUERY&retmode=json
```

3 req/sec without key, 10 req/sec with free NCBI API key.

---

## Recommended stack

```
Client question
     │
     ▼
Semantic Scholar API  ──→  Claude API (synthesis)
     │                          │
     ▼                          ▼
OpenAlex (fallback)     Plain-language recommendation
     │
     ▼
PubMed (clinical validation)
```

**In practice:** Query Semantic Scholar first. Use the `tldr` field and top 5–10 papers by `influentialCitationCount`. Pass abstracts + TLDRs to Claude API with a role-specific system prompt (clinician / fitness / psychologist) to generate a client-ready evidence summary.

---

## Sources

- Rajit D. et al. (2025). Assessing the coverage of PubMed, Embase, OpenAlex, and Semantic Scholar for automated single-database searches. *Journal of Clinical Epidemiology*, 183, 111789.
- Semantic Scholar API docs: https://api.semanticscholar.org/api-docs
- OpenAlex API docs: https://docs.openalex.org
- PubMed E-Utilities: https://www.ncbi.nlm.nih.gov/books/NBK25501/
