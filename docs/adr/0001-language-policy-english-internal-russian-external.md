---
id: ADR-0001
status: Accepted
supersedes: null
superseded_by: null
source_type: verbatim
---

# 0001 — Language Policy: English Internal, Russian External

## Status

Accepted.

## Context & Constraints

Two existing rules were in direct conflict. Rule 3 called for Russian
everywhere. CONSTITUTION principle #7 called for Internal English,
External Russian. Radar's vault content spans several distinct
audiences and channels — machine-parsed structured fields, new
knowledge-base files under `01_Assessments/`, `02_Patterns/`, and
`04_Analysts/`, human-edited templates, the owner's own chat with the
agent, and the public Telegram channel — and a single blanket language
rule could not serve all of them without breaking one of the two
existing rules outright.

## Decision

New vault files under `01_Assessments/`, `02_Patterns/`, and
`04_Analysts/` are written in English. Russian machine-parsed
**Label:** fields (literal, structured key names read by code) stay
Russian literals. Chat with the owner, the Telegram channel, and
human-edited templates stay Russian.

Six forks were resolved during the interview to make this decision
concrete and implementable:
- the switch point between languages is the moment of a code edit, not
  a content-type boundary decided at read time;
- scope is limited to the body of a file, not any file-level directive;
- post generation goes through a single `generate_post()` call, so the
  language boundary is enforced in exactly one place;
- a mixed-language corpus (English vault content read from a Russian
  chat) requires no explicit marking of which language is which;
- the "Human Edit" block inside a file is always Russian, regardless of
  the rest of the file's language;
- the filename itself is unchanged by this policy.

## Alternatives & Rationale

**A. Rule 3 — Russian everywhere (rejected).** This was the status quo
default at the fork point, but it directly overrides CONSTITUTION
principle #7 without resolving the conflict, and gives no dedicated
data layer to a downstream English-reading audience.

**B. CONSTITUTION principle #7 — Internal English, External Russian
(chosen).** Resolves the same conflict by drawing the boundary at
audience: internal, structured, machine-oriented content in English;
external, human-facing, conversational content in Russian. This is the
boundary six forks above make concrete for Radar's actual files and
functions.

## Consequences

`analyze.py`, `patterns.py`, `fetch_analysts.py`,
`update_assessments.py`, and `telegram_post.py` were all changed to
respect the new boundary. A new module, `vault_language.py`, centralizes
the language-boundary logic so it isn't reimplemented per script.

Three real bugs were found and fixed before this decision was written
into code, each a concrete case of the old Russian-everywhere default
silently producing wrong behavior once English vault content existed:
`extract_shift_summary()` and `falsify_pattern()` would have ignored
English section headers; `cluster_with_sonnet()` directly contradicted
the new decision; and a `filename[:10]` date-parsing shortcut never
actually worked against the real filename format in use.

## Confirmation & Revisit

Confirmed via a full Grill Me + Dual Review interview cycle
(2026-07-28) — see ADR-0002 for that tool's own history — with all six
forks above explicitly resolved during the interview, not left to
implementation-time judgment calls.

Revisit if a new content type or audience is added to the vault that
doesn't cleanly map to either "internal/machine" or "external/human" —
the six-fork resolution above assumes exactly two buckets.

**Source.** Interview, 2026-07-28, full Grill Me + Dual Review cycle,
6 forks resolved.
