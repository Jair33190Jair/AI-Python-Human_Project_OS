---
owner: kai
description: Timestamp rules for persistence design and implementation.
---

# Timestamp Policy

Load this convention when designing or changing schemas, models, migrations,
retention, or audit behavior.

- Add a timestamp only when a named person or process uses “when?” to decide or
  act.
- Keep existing `created_at` and `deleted_at` fields where soft deletion already
  uses them; do not migrate solely to remove harmless timestamps.
- Do not add `updated_at` by default. It is not an audit trail.
- Prefer event-specific names such as `expires_at`, `accepted_at`, `valid_from`,
  or `deleted_at` when the event matters.
- Use explicit audit events when the consumer needs who changed what, not more
  row timestamps.
