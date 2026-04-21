---
name: markup
description: Marking human-input fields and AI/human boundaries across all formats
---

# Markup Conventions

## `human_` prefix

Use `human_` for any value a human must supply before
the artifact is usable. Works across documents, JSON,
configs, and code scaffolding:

```
# documents
human_company_name

# JSON / config
"endpoint": "human_api_endpoint"

# code
API_KEY = "human_api_key"
```

Rules:

- Only where the value genuinely varies per context.
  Don't over-annotate stable values.
- Never resolve `human_` fields in copies or translations
  — the human must see exactly what needs their input.

## AI / human boundary

Where it isn't obvious which parts are AI-generated vs.
human-edited, mark it:

```
<!-- AI-generated — human should review -->
<!-- Human fills in from here -->
```
