---
owner: kai
---

# Video conference provider

**Date:** 2026-04-29
**Context:** Choose a video API for embedding in web
applications under Swiss nDSG/GDPR, with no end-user
install required.

---

## Options

| Dimension | Whereby Embedded | Daily.co | Jitsi (self-hosted) |
|---|---|---|---|
| GDPR / nDSG fit | EU-native, ISO 27001 | GDPR + EU-US DPF | Full — data stays on your server |
| BAA included | Yes, free | Yes, $500/mo Healthcare tier | No (you own everything) |
| API embeddability | iFrame or JS SDK | Prebuilt UI or custom | iFrame API |
| End-user experience | Link-based, zero install | Browser-based | Yes |
| AI transcription | Bring your own | Built-in API | DIY only |
| Cost | Free tier; ~$9/mo usage | Pay-per-minute; $500/mo HIPAA | Infrastructure only |
| Key risk | AI notes require extra work | Expensive at small scale | Requires DevOps capacity |

---

## Decision: Whereby Embedded

Whereby is EU-native by design (Norway), ISO 27001 certified,
and includes a BAA at no extra cost — satisfying nDSG Art. 9
without extra negotiation. Users join via a link with no
install, keeping friction minimal. AI transcription is
bring-your-own, which preserves flexibility across projects.
Daily.co is the upgrade path if built-in transcription
becomes a hard requirement.

---

## Revisit if

- Daily.co drops below ~$100/mo for the HIPAA tier
- A project requires built-in transcription that
  bring-your-own can't satisfy cost-effectively
- Whereby changes its EU data-residency guarantees

---

## Notes

- nDSG Art. 9 mandates a DPA with any video vendor —
  request it before go-live.
- HIPAA is a US law; it's used here only as a compliance
  benchmark for health-data vendor vetting in Switzerland.
- Doxy.me and Zoom (free) are not suitable for platform
  embedding.