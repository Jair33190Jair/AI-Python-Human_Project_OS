---
owner: leo
name: naming_conventions
description: Name and place things by what they are — code actions, disposable pipeline artifacts, permanent business records.
---

# Naming Conventions

Applies to all projects when working in a code repo. Both humans and AI agents
follow this. For the folder tree itself — what lives where, when to create a
folder — see [11_project_structure.md](11_project_structure.md). This file
governs *naming*: code, runtime data, and business records.

## Underlying principle

Name and place things by **what they are**, not what produced them or when they
were last touched.

- Code describes actions → `verb_object`.
- Pipeline artifacts describe data, and are disposable → overwritable, gitignored.
- Business records describe events, and are permanent → dated, immutable.

Each category gets rules matching its lifecycle. Never force one rule onto
everything.

## Repo layout

The folder tree is [11_project_structure.md](11_project_structure.md). Two
placement rules live here because they are naming-adjacent:

- **Nest vs. sibling:** code invoked by only one app nests inside it
  (`apps/backend/pipeline/`). Code with more than one caller — e.g. run from a
  CLI locally *and* called by the backend in production — stays a top-level
  sibling of `apps/`, importable by whoever needs it.
- **New top-level folder?** Update `README.md` first.

## `apps/` — product code

Each app follows its own framework's idioms (React component conventions, route
conventions). The naming rules below do **not** apply inside `apps/` — don't
force `verb_object()` onto a React component.

### Product-code files — name the business object

File and module names must say which product object or workflow they operate
on. Avoid layer buckets such as `crud.py`, `helpers.py`, `utils.py`,
`manager.py`, or broad domain names when the file really owns one object.

- Good: `playground_runs.py`, `reset_playground_runs.py`,
  `test_playground_run_visibility.py`
- Bad: `playground.py` for run persistence, `reset_playground.py` for a run
  wipe, `test_playground_crud.py`

Use the layer folder to say the layer (`crud/`, `routers/`, `scripts/`);
use the filename to say the business object and, for scripts/tests, the action
or behavior.

## `pipeline/` — data-pipeline code

### Functions — `verb_object()`

Name the action, not the types: `transcribe_audio()`, `extract_observations()`,
`generate_summary()`.

**Exception — pure format conversion:** use `object_to_object()` only when the
conversion is lossless with zero domain logic (`json_to_dict()`,
`bytes_to_base64()`). Any filtering, validation, or real logic → use a verb
(`parse_json()`, not `json_to_validated_dict()`).

### Modules

- Action module → same name as its function: `transcribe_audio.py` exposes
  `transcribe_audio()`.
- Concept/infra module → noun: `models.py`, `config.py`, `database.py`.

### Variables — nouns

Name the concept: `transcript = transcribe_audio(audio)`. Never `result`,
`output`, `data`, `item`.

### Types/Classes — `PascalCase` nouns

`Audio`, `Transcript`, `Observations`, `Summary`.

### Artifacts — nouns describing contents

`transcript.json`, `observations.json`, `summary.json`. Never
`extract_observations_output.json`.

### Failed / partial stages

Never silently write a bad artifact. Either omit it, or write
`<artifact>.error.json` with the failure info. `is_valid(artifact)` must be able
to tell "missing" from "invalid".

### Layout — one directory per stage

Code is stable and lives in `pipeline/`. No numbering — order comes from which
function calls which, not from filenames. Everything a stage needs lives in the
stage's directory: its module, its `<artifact>.schema.json` (co-located because
it changes with the code), and any prompt/template/catalog assets it loads. A
helper used by two or more stages goes in `pipeline/common.py`, not in one
stage's folder.

A stage that is a single action names its **directory after that action** —
`transcribe_audio/transcribe_audio.py` exposing `transcribe_audio()`, run as
`make transcribe_audio`. Use a concept noun for the directory (`transcription/`)
only when the stage genuinely holds several sibling modules.

```
pipeline/
├── common.py                       # cross-stage helpers only
├── transcribe_audio/
│   ├── transcribe_audio.py
│   ├── transcript.schema.json
│   └── example/                    # committed golden input + output, refreshed on purpose
├── pseudonymize_transcript/
│   ├── pseudonymize_transcript.py
│   ├── ptranscript.schema.json
│   └── key_list.schema.json
├── extract_observations/
│   ├── extract_observations.py
│   └── observations.schema.json
└── generate_summary/
    ├── generate_summary.py
    ├── summary.schema.json
    ├── system_prompt.md            # hand-edited asset
    └── summary.template.md         # generated asset — header says so
```

### Schemas — `<artifact>.schema.json`

Static, hand-maintained, always committed. Defines the contract for an artifact.

### Boolean functions — `is_/has_/can_/should_`

`is_valid(session)`, `has_transcript(session)`.

## `runs/` — pipeline runtime data

Input and every generated artifact for a run live together in
`runs/<session_id>/`. `runs/` is gitignored. A run is self-contained: delete or
zip the folder and you have the full story, input through final output.

```
runs/
└── session_2026-09-01_143012/
    ├── audio.wav                       # original input — never mutated
    ├── transcript.json
    ├── pseudonymized_transcript.json
    ├── observations.json
    └── summary.json
```

- The original input is artifact zero; never edited in place. A stage needing a
  modified version writes a new artifact (`audio_cleaned.wav`), never an
  overwrite of `audio.wav`.
- A run is created by a small setup function, e.g.
  `init_session(audio_path) -> Session`, which generates `session_id`, creates
  the directory, and copies the input in.
- Test fixtures (`tests/fixtures/sample_audio.wav`) are committed and reused —
  never confused with `runs/` data.
- Never put runtime data in `pipeline/`.

**The chain:** `verb_object.py` → `verb_object()` → `Type` → `artifact.json`
(in `runs/<session_id>/`) → `artifact.schema.json` (in `pipeline/<stage>/`).

## `business/` — finance, legal, compliance

Authoritative records, not disposable state. **Never overwritten, always dated.**

```
business/
├── finance/{records,filings,templates}/    2026-08-31_invoice_acme-corp.pdf
├── legal/{contracts,policies,templates}/    acme-corp_msa.pdf + acme-corp_msa.meta.json
└── compliance/{records,policies}/
```

- Filenames carry a date (`YYYY-MM-DD` or `YYYY-Qn`) — never a version word like
  `final` or `v3`.
- A correction is a new dated file, never an edit of the filed one.
- Contracts get a metadata sidecar `<name>.meta.json` (status, signed_date,
  renewal_date, counterparty) so "which contracts renew this quarter" is
  answerable without opening a PDF.

## `architecture/` — shared reference

Architecture notes, decisions log, ADRs — knowledge, not code or records.
Freeform, low ceremony.

## Writing this doc for AI agents

- The repo README is the single source of truth for structure and naming.
  `CLAUDE.md` only points to it — a stub, not a copy. Update one file so the two
  never drift.
- State routing rules directly ("contract? → `business/legal/contracts/`"), not
  as a passive folder list. An agent acts on instructions, not on inferred
  intent.
- State the **don'ts** explicitly ("never put runtime data in `pipeline/`",
  "never overwrite a filed business document"). Under ambiguity an agent invents
  a new pattern; an explicit rule removes the ambiguity.
- Consistency matters more than for a human: one inconsistently named file
  teaches the wrong pattern as strongly as ten consistent ones teach the right
  one.
