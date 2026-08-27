---
id: ADR-0024
status: Accepted
supersedes: null
superseded_by: null
source_type: inferred
---

# 0024 — Scope Boundaries: Non-Goals

## Status

Accepted.

## Context & Constraints

Radar's own verdict mechanism (`compute_status()`) is built
specifically for falsifiable knowledge claims about ecosystem
shifts (ADR-0015) — a different design target than several adjacent,
tempting directions the project could have grown toward instead.

## Decision

Radar explicitly is not: an autonomous AI agent, a trading system, a
recommendation system, a content generator, an infrastructure
logging/monitoring system, a marketing/growth tool for the channel.

## Alternatives & Rationale

**Autonomous AI agent (rejected).** No rationale recorded in the
original prose — only the boundary itself.

**Trading system (rejected).** Radar's verdict mechanism
(`compute_status()`, ADR-0003) is built for falsifiable knowledge
claims, not actionable financial signals — a trading system carries
different risk/liability requirements that Radar's design was never
built to satisfy.

**Recommendation system (rejected).** No rationale recorded — only the
boundary itself.

**Content generator (rejected).** No rationale recorded in the
original prose. Consistent with Falsifiability First (ADR-0015): a
content generator's output isn't required to be a checkable claim,
which is the opposite of what Radar's verdict mechanism is built to
produce — noted here as an observed consistency, not as the original
stated reason.

**Infrastructure logging/monitoring system (rejected).** No rationale
recorded — only the boundary itself.

**Marketing/growth tool for the channel (rejected).** The one item with
an actual recorded rationale, not just a listed boundary: the
channel's audience kill-metric (reach/subscribers) was struck down as
the wrong metric to begin with, fixed 2026-07-28. `@radar_public` is
open but not promoted; the goal stated at the time was a personal
measuring instrument for the owner's own investment/architecture
decisions, not a growth target.

## Consequences

This is the boundary that keeps Radar's design surface narrow — a
proposal that would turn Radar into one of these six things is out of
scope by default, not evaluated case-by-case.

## Confirmation & Revisit

Not mechanically enforced — this is a design intent, not a code-level
constraint. Revisit if a specific proposal genuinely blurs one of these
boundaries in a way that seems to serve Radar's actual stated purpose
(a measuring instrument) rather than mission drift — that's a case for
the owner to decide, not a default.

**Source.** Formalizes a pre-existing, previously undocumented
boundary list, found stated in prose in `docs/CONSTITUTION.md` with no
ADR of its own during that file's 2026-08-27 rewrite. No original
decision date or session is recoverable for the boundary list itself;
the marketing/growth-tool item's rationale is dated 2026-07-28 per the
original prose, though the specific interview/session that produced it
isn't otherwise documented.
