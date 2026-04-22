# Web search contract (shared toolbox)

**This file is the single swap point for the web-search
provider across all agents.** Any agent (Sherlock, Warren,
Saul, Leo, …) that needs web research reads this file and
follows its rules. If the provider changes, edit *only*
this file — nothing in the individual agent skill files
should need to change.

Agents reference this file by saying:
*"Run searches per `00_agents/00_toolbox/web_search.md`."*

---

## Current provider: Tavily (via MCP)

- MCP server name: `tavily` (configured in `~/.claude/settings.json`)
- Primary tool: `tavily-search` — general web search
- Secondary tool: `tavily-extract` — fetch & extract page
  contents from a URL when a search snippet is insufficient
- The full tool identifier typically appears in the tool list
  as `mcp__tavily__tavily-search` / `mcp__tavily__tavily-extract`.
  Use whichever exact name is exposed at call time.

## How to call search (rules every agent must follow)

1. **Language first.** Compose queries in the project's
   actual market language(s), not only English. A Swiss
   project → English + German + French (+ Italian if
   relevant). A Brazilian project → Portuguese + English.
   Read the project's context file(s) for language cues.
2. **One concept per query.** Never stuff multiple ideas
   into one search string. 8–15 focused queries beat 3 fat
   ones.
3. **Freshness:** prefer results from the last 18 months
   unless historical context is explicitly needed. If the
   provider exposes a `search_depth` or `time_range` knob,
   use the recent/advanced option.
4. **Result count:** request 5–10 results per query by
   default; raise to 15–20 only when a query is central.
5. **Extract when snippets are thin.** If a search result
   looks promising but the snippet is too terse to answer
   the question, follow up with `tavily-extract` on that
   URL rather than guessing.
6. **Cite everything.** Every non-trivial claim written into
   an artifact must carry its source URL. No URL → no claim.

## Expected result shape

Search results yield at minimum:
`{ url, title, snippet, published_date? }`

Extracts yield:
`{ url, title, content, published_date? }`

Agents normalise into their own artifact schemas; they should
not assume Tavily-specific fields beyond these.

## Fallback behaviour

- **Empty results:** retry once with a reformulated query
  (synonyms, different language). If still empty, record
  `"unknown"` in the artifact — never invent data.
- **Rate limit / tool failure:** stop the current task
  cleanly, report what was collected so far, and ask the
  user whether to resume.
- **Paywalled or blocked content:** note the URL and mark
  the relevant field `"inaccessible"`. Do not fabricate
  contents.

## Swapping the provider (future)

To replace Tavily (e.g. Brave, Exa, SerpAPI, Claude's
built-in `WebSearch`):

1. Update the *Current provider* section above with the new
   tool name(s) and any calling quirks.
2. Keep *Expected result shape* identical, or document a
   normalisation step so downstream agents need no edits.
3. Do not rename this file — agents reference it by path.
