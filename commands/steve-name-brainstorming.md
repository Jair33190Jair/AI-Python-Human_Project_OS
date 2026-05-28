---
description: Discover brand names from project sources and present only exact-match domain-available, collision-screened finalists.
argument-hint: <project repo; brand discovery questionnaire; ten guiding words; domain and market constraints>
status: draft  # human flips to `stable` when satisfied
owner: steve
---

You are running a **source-grounded brand-name discovery** workflow.

Use this command when a product or company needs name candidates
and exact-match domain availability is a hard requirement.

Anchor: `$ARGUMENTS` - the project/source material and naming
constraints supplied by the user.

Return recommendations in chat only. Do not write into the project
unless the user separately requests a saved deliverable.

---

## Resolve

Extract from `$ARGUMENTS`:

- project repository path;
- brand questionnaire path or supplied questionnaire answers;
- ten guiding words for brainstorming;
- additional positioning, market, legal, or competitor context;
- existing working names to reconsider, if any;
- exact required domain extension;
- allowed length or construction constraints;
- required languages or markets.

If the project repository path, brand questionnaire, or exactly ten
guiding words are missing, ask for the missing inputs and stop:

```text
To start the naming pass, please provide:
1. Project repo path: <path>
2. Brand discovery questionnaire: <path, link, or pasted answers>
3. Ten guiding words: <word 1, ..., word 10>
```

After receiving them, read the project repository's relevant product
context and each supplied local source before generating names. For
referenced URLs, retrieve the current source before using it.

Stop before naming if product context or the required domain
extension remains missing after the required intake:

```text
Blocked: naming requires product context and an exact-match domain
extension.
Missing: <fields>
```

If an optional source is named but cannot be read, state the missing
source and stop unless the user explicitly removes it from scope.

If sources conflict, record the conflict and use the most
authoritative or most recently approved product source.

## Naming Brief

Before brainstorming, determine:

- what the product does and does not do;
- primary customer, painful problem, and desired emotional outcome;
- what the brand must be trusted with;
- desired personality and traits to avoid;
- unsupported positioning or claims to avoid;
- future expansion the name must accommodate;
- language, cultural, legal, or regulatory sensitivities;
- useful territory in any working names;
- how the ten guiding words translate into naming direction, without
  forcing candidates that fail the product brief.

Do not surface name candidates until this brief is complete.

## Territories

Define three to six strategic naming territories from the brief.
For each, identify its relevance, suitable name style, and main risk.
Exclude directions that contradict trust, audience, scope, or
expansion requirements.

## Private Candidate Pass

Generate a broad private set across the approved territories.
Do not display raw candidates or names rejected in screening.

Reject a candidate before domain checking when it:

- violates explicit construction or length rules;
- is difficult to pronounce or spell in a required market;
- has an unwanted meaning in a required language;
- feels wrong for the audience or brand personality;
- implies an unsupported product or compliance claim;
- narrows credible future expansion unnecessarily;
- resembles a known competitor too closely.

Do not create awkward spelling changes solely to obtain a domain.

## Domain Gate

For each conceptually acceptable candidate, check the exact-match
required domain live on the day of the run.
Never reuse availability findings from an earlier run.

Required method:

1. Use the authoritative registry RDAP service for the required TLD,
   or an equivalent live authoritative registry lookup.
2. Confirm registry-empty names through a live registrar result that
   identifies the exact domain as available for ordinary registration
   and does not label it premium, aftermarket, resale, broker-only,
   or reserved.
3. Record the exact screening date and sources used.

Reject domains that are registered, parked for sale, premium-priced,
broker-only, reserved, confusingly unavailable, or not verifiable.
Website loading or DNS absence is never an availability check.

If no high-quality candidate survives, state that no recommendation
survived rather than lowering the naming bar.

## Collision Gate

For each domain-available survivor, run current public searches for
the exact candidate, focusing on companies, products, software,
regulated-sector products, competitors, trademarks visible in
public results, and prominent uses in launch or expansion markets.

Reject clear brand-confusion risks. Retain minor unrelated uses only
when they do not create likely confusion, and disclose them as a
concern.

State that this is preliminary collision screening, not formal
trademark clearance.

## Evaluate

Rank only survivors. Weight criteria from the source brief rather
than assigning equal importance automatically:

- fit with personality and emotional promise;
- credibility for audience and product role;
- pronunciation and spelling across required markets;
- distinctiveness and expandability;
- verified domain status;
- collision risk and unwanted connotations.

Recommend one leading candidate only when it clearly deserves it.

## Output

Return only screened, exact-match domain-available candidates in
this structure:

```markdown
### Naming Brief
- <up to 8 concise bullets>

### Naming Territories
| Territory | Strategic idea | Strength | Risk |
| --- | --- | --- | --- |

### Available Candidates
| Name | Exact-Match Domain | Pronunciation | Territory | Why It Fits | Concern | Initial Collision Screen |
| --- | --- | --- | --- | --- | --- | --- |

### Top Recommendations
1. **<Name>** - <strength>; **open question:** <weakness>.
   *<short positioning line>*

### Recommendation
<one short paragraph, or state that no candidate is strong enough>

### Verification Note
- Required domain extension screened: `<extension>`
- Live screening date: `<YYYY-MM-DD>`
- Availability method/source: <registry plus ordinary-registration confirmation>
- Availability remains provisional until registration is completed.
- Preliminary collision screening is not formal trademark clearance.

### Sources
- <source links or paths actually used>
```

Present at most ten candidates. Do not mention unavailable or
otherwise rejected names as suggestions.

## Final Validation

Before responding, verify that every displayed candidate:

- passed the stated construction and language constraints;
- has a same-session exact-match domain check and ordinary-price
  registration confirmation;
- passed the public collision gate or discloses a minor unrelated use;
- appears with its exact domain in the candidate table.

If any check is missing, remove the candidate or complete the check
before returning the response.

## Hard Rules

- Source material precedes ideation.
- Domain availability is necessary, not sufficient.
- Never imply domain ownership before registration.
- Never imply legal clearance from public searching.
- Never expose the private candidate set or unavailable candidates.
