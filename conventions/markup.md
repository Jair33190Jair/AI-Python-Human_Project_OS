---
name: markup
description: Conventions for marking human-input fields and AI/human boundaries across all formats
---

**Version:** v0.1 — 2026-04-20
**Status:** Draft
**Reviewer:** unassigned

# Markup Conventions

## human_ prefix

Use `human_` prefix for any value a human must
supply before the artifact is used. Applies to
documents, JSON configs, code templates, and
scaffolding files:

```
# documents
human_company_name
human_reviewer_names

# JSON / config
"endpoint": "human_api_endpoint"

# code
API_KEY = "human_api_key"
```

Rules:
- Only where the value genuinely varies per
  context. Don't over-annotate stable values.
- Never resolve `human_` fields in copies or
  translations — keep them so the human sees
  exactly what needs their input.

## AI / human boundary

Where it isn't obvious which parts are
AI-generated vs. human-edited, mark it:

```
<!-- AI-generated — human should review -->
```

```
<!-- Human fills in from here -->
```
