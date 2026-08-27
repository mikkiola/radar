---
id: ADR-0021
status: Accepted
supersedes: null
superseded_by: null
source_type: inferred
---

# 0021 — Feedback-Driven Evolution

## Status

Accepted.

## Context & Constraints

`check_model_updates.py` is `docs/ARCHITECTURE.md`'s "Model-update
feedback check" row — explicitly the first implemented step of a
planned Feedback layer, with `Decisions`/`Outcomes` still "Not
started." This mirrors ADR-0016's (Knowledge Before Automation) gating
logic, applied specifically to when new functionality is added rather
than when automation is added.

## Decision

New functionality appears only after accumulated feedback identifies a
specific, observed cause — never added on assumption or because a
feature seems generally useful.

## Alternatives & Rationale

**A. Add functionality speculatively (rejected, implicit).** A system
without this principle would build out `Forecasts`/`Decisions`/
`Outcomes` (`docs/ARCHITECTURE.md`, all "Not started") ahead of having
real Feedback-layer data to justify their specific shape — the same
risk ADR-0016 names for automation generally, but specifically about
what new features get built at all.

**B. Feedback-Driven Evolution (chosen).** `check_model_updates.py`
exists as a first, narrow, concrete step precisely because it responds
to an observed, specific need (tracking model updates), not a general
"the Feedback layer would be nice" motivation.

## Consequences

`Forecasts`, `Decisions`, and `Outcomes` stay unbuilt until
`check_model_updates.py` (or a similar concrete signal) surfaces an
observed cause that specifically motivates them.

## Confirmation & Revisit

Confirmed by `check_model_updates.py`'s own narrow, single-purpose
scope as currently implemented. Revisit when the next piece of the
Feedback layer is proposed — check whether it's responding to an
observed cause or being added speculatively.

**Source.** Formalizes a pre-existing, previously undocumented
principle, found stated in prose in `docs/CONSTITUTION.md` with no ADR
of its own during that file's 2026-08-27 rewrite. No original decision
date or session is recoverable.
