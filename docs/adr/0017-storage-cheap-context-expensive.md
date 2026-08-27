---
id: ADR-0017
status: Accepted
supersedes: null
superseded_by: null
source_type: inferred
---

# 0017 — Storage Is Cheap, Context Is Expensive

## Status

Accepted.

## Context & Constraints

Radar's assessments accumulate in `01_Assessments/` over the system's
whole lifetime, and its LLM calls (`analyze.py`, `patterns.py`,
`fetch_analysts.py`) each cost real, metered spend per call. Sending
every prior assessment as context to every new call would make cost
scale with the length of accumulated history, not with the size of the
actual decision being made.

## Decision

Store almost everything durably; send an LLM only the minimum context
it actually needs for the decision at hand.

## Alternatives & Rationale

**A. Minimize storage, maximize context per call (rejected,
implicit).** A system without this principle would either discard
history to save storage (losing the falsifiability/recheck machinery
ADR-0015 depends on) or feed growing history into every call (scaling
cost with the system's own age, not its workload) — both worse for a
system meant to run indefinitely.

**B. Storage Is Cheap, Context Is Expensive (chosen).** Storage cost is
roughly flat and small (markdown files in a git-backed vault); LLM
context cost scales per call and per token. Treating them
asymmetrically matches their actual asymmetric cost.

## Consequences

Assessment and pattern files are retained permanently (targeted edits
only, never wholesale overwrites) rather than pruned; each LLM call is
scoped to the specific candidate or pattern under evaluation, not the
full vault history.

## Confirmation & Revisit

Not independently load-tested against real cost data. Revisit if a
future call site is found sending unbounded historical context to an
LLM call, or if storage growth itself becomes a real operational cost.

**Source.** Formalizes a pre-existing, previously undocumented
principle, found stated in prose in `docs/CONSTITUTION.md` with no ADR
of its own during that file's 2026-08-27 rewrite. No original decision
date or session is recoverable.
