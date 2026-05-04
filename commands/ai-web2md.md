---
owner: kai
---

# /ai-web2md

Fetch a URL and return its content as clean markdown.

**Argument:** one URL.

---

## Tier escalation

Always start at Tier 1. Step up only when the previous
tier fails. Stop at the first tier that returns usable
content.

### Tier 1 — curl + pandoc + self-cleanup

```bash
curl -sL "URL" | pandoc -f html -t markdown_strict --strip-comments
```

Always run this first. After conversion, **self-clean
inline**: strip nav, social icons, duplicate blocks,
dropdown option lists, footers. Keep all substantive
content. No external tool, no extra model call.

**Fail signal:** raw output < 30 words (JS skeleton).

---

### Tier 2 — WebFetch (JS-rendered pages)

Use `WebFetch`. Covers pages where Tier 1 returns empty.
Apply the same inline self-cleanup to the result.

---

### Tier 3 — Firecrawl / Bright Data (not configured)

Not yet available. Add provider details here when ready.

---

## Fallback behaviour

- Tier 1 < 30w → go to Tier 2.
- Tier 2 empty → mark `"inaccessible"`, report to user.
- Paywalled / login-walled → mark `"inaccessible"`.
  Never fabricate content.

---

## Output

Return as a markdown block:

```
url:        <string>
title:      <string>
fetch_date: YYYY-MM-DD
tier_used:  1 | 2
content:    <markdown string>
```
