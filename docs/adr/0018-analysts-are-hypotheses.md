---
id: ADR-0018
status: Accepted
supersedes: null
superseded_by: null
source_type: inferred
---

# 0018 — Analysts Are Hypotheses

## Status

Accepted.

## Context & Constraints

`fetch_analysts.py` feeds `patterns.py` a second, independent input
alongside internal assessments. If an external analyst's opinion were
treated as authoritative, it would short-circuit Radar's own
falsification loop — the whole point of comparing internal signal
against external analyst opinion is to find where they diverge, not to
defer to whichever source spoke first.

## Decision

No external analyst is treated as an authority. An analyst's weight in
Radar's own reasoning is set by that analyst's track record over time,
not assigned by hand at ingestion time.

## Alternatives & Rationale

**A. Treat external analyst opinion as authoritative (rejected,
implicit).** A system without this principle would let an analyst's
stated conclusion override Radar's own `compute_status()`-derived
verdict, defeating the principle that a verdict is computed in code
from structured evidence, never from anyone's self-report — model's or
analyst's.

**B. Analysts Are Hypotheses (chosen).** External analyst input is
treated the same way Radar treats its own model output: a checkable
claim, not a trusted authority — Falsifiability First (ADR-0015)
applied to a second data source, not just the primary one.

## Consequences

`patterns.py` looks for where Radar's own signal and external analyst
opinion align or diverge, rather than substituting one for the other.

## Confirmation & Revisit

Track-record-based weighting is not yet implemented as an explicit
mechanism — `fetch_analysts.py` currently ingests analyst input without
a scored weighting system. Revisit once enough analyst-track-record
history accumulates to make weighting concrete, the same
lay-the-schema-defer-the-math pattern `state_value` used before its own
transition math existed.

**Source.** Formalizes a pre-existing, previously undocumented
principle, found stated in prose in `docs/CONSTITUTION.md` with no ADR
of its own during that file's 2026-08-27 rewrite. No original decision
date or session is recoverable.
