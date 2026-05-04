---
owner: kai
---

# Competitive Intelligence Tool Decision
**Date:** April 15, 2026  
**Context:** Selecting web search tooling for AI-powered competitive analysis across medical device products built with Claude.

---

## Decision

**Start simple: Claude built-in search + Exa MCP (free tier). Do not build a pipeline yet.**

Run 3–4 real competitive analyses manually first. Let the pain of doing it by hand define what's actually worth automating. The pipeline architecture becomes obvious after that — right now it would be overengineering.

---

## Tool Comparison

| Dimension | Tavily | Exa AI | Perplexity Sonar | Brave Search | Firecrawl | Claude Built-in |
|---|---|---|---|---|---|---|
| **Best for** | RAG pipelines, LangChain workflows | **Competitor discovery (semantic)** | Cited Q&A answers | High-volume, cost-predictable search | **Extracting known pages** | Ad-hoc research + reasoning |
| **Search type** | Keyword | Neural / semantic | LLM-synthesized | Keyword | URL-targeted extraction only | Keyword + synthesis |
| **Finds unknown competitors?** | Moderate | **Strong** | Moderate | Moderate | No | Moderate |
| **Reads competitor pages?** | Yes | Yes | Partial | Partial | Excellent | Yes |
| **Finds Reddit / Trustpilot reviews?** | Yes | Yes | Yes (synthesized) | Yes | Only if URL known | Yes |
| **Latency** | ~998ms | ~425ms | ~11,000ms ❌ | ~669ms | Varies | Seconds |
| **Free tier** | 1,000 credits/mo | $10 credits | Limited | 2,000 queries/mo | 500 credits/mo | Included in subscription |
| **Paid pricing** | $30/mo (10K credits) → $500/mo | $49/mo (8K credits) | $5–14/1K requests + tokens | $5–9/1K requests | $83/100K pages | $0 extra |
| **Founded** | 2024 | 2021 | 2022 | 2012 | 2024 | Anthropic 2021 |
| **Funding / status** | Acquired by Nebius for $275–400M (Feb 2026) | $111M raised, $700M valuation | $1.5B raised, $20B valuation | Private | Series A | $7B+ (Anthropic) |
| **Key risk** | Post-acquisition roadmap uncertainty | More expensive at scale | Slowest latency, dual pricing complexity | Keyword-only, no semantic discovery | Not a search tool | No cross-session memory |
| **MCP for Claude** | ✅ | ✅ | ✅ | ✅ | ✅ | Built-in |

---

## Key Insights from Discussion

### Discovery: Exa > Tavily
Tavily is keyword-based. Exa uses neural/semantic search — it finds companies doing similar things even when they use completely different terminology. In medical devices, where the same category has wildly different naming conventions across geographies and regulatory contexts, this is a meaningful difference. **For finding competitors you don't know about, Exa wins on quality.**

### Extraction: Firecrawl > Tavily / Exa
Firecrawl was purpose-built for clean content extraction from arbitrary pages (JavaScript rendering included, 80.9% coverage). Tavily and Exa both do extraction, but it's secondary to their search function. If you already know the URL — because Exa found it — Firecrawl gives cleaner output. Also dramatically cheaper at scale ($83 vs $800 per 100K pages vs Tavily).

### Keep reasoning on Claude
The correct architecture separates concerns:
- **Exa** → finds unknown competitors (data retrieval problem)
- **Firecrawl** → extracts their pages cleanly (data retrieval problem)
- **Claude** → reads the content and does the analyst work (reasoning problem)

Perplexity bundles retrieval + reasoning into one API call. For competitive intelligence this is a downside — you lose control over the analysis framework and get a pre-baked answer instead of a proper analyst workflow. Claude reasoning over raw content is more flexible and thorough.

### Claude subscription covers most of it
For non-automated, occasional research, Claude's built-in search is high quality and costs nothing extra. The gap it can't fill is *semantic discovery* — finding competitors you haven't named. That's the one place a dedicated tool like Exa adds something qualitatively different.

### Don't build the pipeline yet
The hardest part of competitive intelligence in medtech is not data retrieval — it's defining what "good analysis" looks like for your specific product category. That's a prompt engineering and judgment problem. Spend time on that first. Build automation only after you've done it manually enough times to know exactly what you'd be automating.

---

## Recommended Workflow (Manual Phase)

1. Connect **Exa as MCP tool** in Claude.ai (free tier, no card required)
2. Describe your product category to Claude — let Exa surface unknown competitors semantically
3. Claude fetches their pages, checks Reddit/Trustpilot, synthesizes analyst-style profile
4. After 3–4 runs: identify what's slow, missing, or repetitive → that defines the pipeline

---

## Medical Device Considerations

- Claude can search FDA 510(k) databases, EU MDR/IVDR filings, and clinical trial registries directly — most search APIs add no special value there
- For data privacy: Exa offers Zero Data Retention; Tavily/Nebius has EU-based infrastructure (GDPR-friendly)
- Competitive analysis and regulatory status profiling = fine. Clinical recommendations or device selection for specific patients = always flag for professional review
- Key review communities beyond Reddit: Medscape, regulatory forums, industry LinkedIn groups — Claude's search handles these natively

---

## If/When You Do Build a Pipeline

```
Exa (discover) → Firecrawl (extract) → Claude API (reason + output)
```

Trigger this only when: weekly+ frequency, 5+ products, structured output needed (JSON/report). Until then, the manual workflow above is faster to start and teaches you what the pipeline actually needs to do.
