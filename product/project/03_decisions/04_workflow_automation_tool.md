---
owner: kai
---

# Workflow Automation: Tool Selection

**Date:** 2026-04-27
**Context:** Choosing a workflow automation layer for the AI-assisted session note pipeline (voice memo → STT → structured note) in a Swiss therapist practice management product, where DSG compliance and pseudonymization are non-negotiable constraints from day one.

---

## Options

| Dimension | n8n (self-hosted) | Activepieces (self-hosted) | Custom solution |
|---|---|---|---|
| DSG / data sovereignty | Full — runs on Swiss VPS, no data leaves infra | Full — same self-host posture as n8n | Full — you control every layer by definition |
| Integration ecosystem | 400+ connectors, strong AI/HTTP/webhook support | ~150 connectors, growing fast, HTTP nodes cover gaps | Zero out-of-box; every integration is custom code |
| Code extensibility | Code nodes (JS/Python), arbitrary npm packages | Code nodes (JS), slightly narrower than n8n | Unlimited — it's all code |
| Time to first pipeline | Hours — visual builder + community templates | Hours — cleaner UX, fewer templates | Weeks — retry logic, queues, monitoring all DIY |
| Maintenance burden | Moderate — Docker upgrade cadence ~monthly | Low-moderate — newer, less battle-tested | High — you own all infra and debugging |
| Monthly infra cost | ~CHF 20–40 (2–4 vCPU VPS) | ~CHF 20–40 (same footprint) | ~CHF 50–150+ (queue, workers, storage, monitoring) |
| Community / support | Large: forums, Discord, 800+ templates | Small but responsive; founder-accessible | None — internal docs only |
| Key risk | Occasional breaking changes on self-hosted upgrades | Smaller ecosystem; betting on a younger project | Engineering bottleneck; bus factor if solo dev |

---

## Decision: n8n, self-hosted on Swiss infrastructure

n8n is the strongest fit. It provides the broadest integration ecosystem and the most mature code-node capability (including arbitrary npm packages), which matters for the STT → pseudonymization → AI structuring pipeline where each step needs precise control over what data is sent where. The self-hosted deployment on a Swiss VPS (Infomaniak or Exoscale) satisfies DSG requirements and becomes a concrete sales argument with psychologists: patient audio and session content never leave a Swiss server. Activepieces is a credible alternative if the n8n UX proves too rough for future non-technical collaborators, but its smaller community is a meaningful risk at this stage. A custom solution is ruled out because it would shift weeks of engineering toward queue management and retry logic that n8n provides for free, delaying the core product.

---

## Revisit if

- n8n's upgrade cadence causes repeated breaking changes on self-hosted in the first 6 months — switch to Activepieces or pin a stable version.
- Therapist onboarding requires non-technical workflow editing (e.g. customizing note templates) — re-evaluate Activepieces for its cleaner UX.
- Pipeline volume exceeds ~500 concurrent therapists with complex branching — evaluate Temporal.io for durable execution at that scale.
- A Swiss-hosted managed n8n offering emerges — removes the self-host maintenance burden without sacrificing data residency.

---

## Notes

- Swiss VPS providers with DPA agreements suitable for health-adjacent data: Infomaniak (Geneva), Exoscale (CH-GVA-2), nine.ch.
- Build a dead-letter queue early — a Postgres table + alert flow catches failed transcription jobs before they silently disappear. n8n's built-in error handling alone is not sufficient for production.
- The pseudonymization node should live as a code node *before* any HTTP call to STT or AI APIs, so that identifiable patient data (name, date of birth, AHV number) is never present in outbound API payloads.
- Reference: comparison analysis run 2026-04-27 covering n8n, Zapier, Make.com, Pipedream, Activepieces, Power Automate, Temporal.io, Prefect/Airflow, and custom solutions.