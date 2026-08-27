---
id: ADR-0015
status: Accepted
supersedes: null
superseded_by: null
source_type: inferred
---

# 0015 — Falsifiability First

## Status

Accepted.

## Context & Constraints

A measuring instrument that publishes ungrounded opinions is
indistinguishable from a content generator (see ADR-0024) — its value
collapses to "did the model sound convincing," not "was the claim
true." Radar's verdict mechanism already externalizes this
structurally: `compute_status()` (`src/analyze.py`) computes status
from structured, checkable fields, and `NOISE` / `CANDIDATE` /
`VALIDATED_SHIFT` are distinguishable states specifically so a claim
can be re-examined and revised rather than asserted once and left
alone. `patterns.py`'s falsification loop (`should_falsify()` /
`falsify_pattern()` / `run_falsification()`) re-examines existing
published patterns on every weekly run, and `recheck_lifecycle.py`
revisits already-`VALIDATED_SHIFT` assessments for staleness
(`FROZEN_MONTHS = 6`, `RELEASES_STOPPED_MONTHS = 12`) — none of this
machinery makes sense unless every conclusion is built to carry its
own revision criterion from the start.

## Decision

Every conclusion Radar stores or publishes carries an explicit
revision criterion — a stated condition under which it would be
considered wrong or stale. The system stores checkable claims, not
opinions.

## Alternatives & Rationale

**A. No falsifiability requirement (rejected, implicit).** A system
without this principle would store whatever verdict the model produces
on first pass and never revisit it — `patterns.py`'s falsification
loop and `recheck_lifecycle.py`'s staleness recheck would have no
reason to exist, and Radar would degrade into the "plausible-text
generator" failure mode its own CoVe mechanism is built against. A
claim that can't be shown wrong isn't information the owner can act on
with any confidence.

**B. Falsifiability First (chosen).** Every stored claim is checkable
and re-checkable, which is what makes the quarantine gate and
falsification-loop machinery meaningful investments rather than unused
code paths.

## Consequences

This principle is the reason the CoVe self-check, the quarantine gate,
and the falsification loop all exist as separate, composed mechanisms
rather than a single "ask the model and trust it" call.

## Confirmation & Revisit

Confirmed structurally — `compute_status()`, `apply_quarantine_gate()`,
and `run_falsification()` are all real, currently-implemented
mechanisms whose entire purpose is enacting this principle (see
`docs/ARCHITECTURE.md`). Revisit if a future component stores a
conclusion with no stated revision path — that would be a direct
violation, not a new interpretation.

**Source.** Formalizes a pre-existing, previously undocumented
principle, found stated in prose in `docs/CONSTITUTION.md` with no ADR
of its own during that file's 2026-08-27 rewrite. No original decision
date or session is recoverable.
