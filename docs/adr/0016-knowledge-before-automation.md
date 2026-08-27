---
id: ADR-0016
status: Accepted
supersedes: null
superseded_by: null
source_type: inferred
---

# 0016 — Knowledge Before Automation

## Status

Accepted.

## Context & Constraints

Radar could automate more than it does today — auto-publishing without
human review, auto-adjusting quarantine days, auto-tuning filter
keywords. Layer 4's `Forecasts`/`Decisions`/`Outcomes` and the gated
`Observability`/`Trust & Security`/`Optimization & Evolution` layers
are all explicitly "Not started" in `docs/ARCHITECTURE.md`, not
because they're technically hard, but because the knowledge structure
they'd automate against (accumulated pattern/outcome history) doesn't
exist yet.

## Decision

New automation is added only after a stable knowledge structure exists
to automate against — not because a capability seems useful or is easy
to build.

## Alternatives & Rationale

**A. Build automation ahead of the data (rejected, implicit).** A
system without this principle would have built the gated layers
(`Observability`, `Trust & Security`, `Optimization & Evolution` —
tracked `docs/BACKLOG.md` [B-010]-[B-012]) speculatively, before
there's any accumulated signal to optimize against — automation with
nothing real to act on.

**B. Knowledge Before Automation (chosen).** Matches the gated-layer
sequencing already in force (`docs/ROADMAP.md`'s dependency chain):
those layers wait on an explicit trigger from data, not a
build-it-and-see approach.

## Consequences

This is the stated reason the gated layers (`Observability`/`Trust &
Security`/`Optimization`) remain deliberately unbuilt rather than being
treated as a backlog gap.

## Confirmation & Revisit

Confirmed by the current state of `docs/ARCHITECTURE.md` itself —
three layers are explicitly "Not started, gated" rather than partially
built. Revisit when one of those layers' data trigger condition is
actually met (see `docs/BACKLOG.md` [B-010]-[B-012]) — that's the point
this principle says "now automate."

**Source.** Formalizes a pre-existing, previously undocumented
principle, found stated in prose in `docs/CONSTITUTION.md` with no ADR
of its own during that file's 2026-08-27 rewrite. No original decision
date or session is recoverable.
