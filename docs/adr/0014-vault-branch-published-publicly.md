---
id: ADR-0014
status: Accepted
supersedes: null
superseded_by: null
source_type: verbatim
---

# 0014 — `vault` Branch Published Publicly

## Status

Accepted.

## Context & Constraints

Whether `vault` (the data branch) should be public was a question left
open since 2026-08-07 — SPEC C (ADR-0011) deliberately did not resolve
it, since at the time it was a side effect of the old mirroring
mechanism's own scope, not a decision made on its own terms. After
ADR-0013's full migration, `vault` exists on GitHub as a full branch,
making this a live question again on its own merits.

## Decision

The `vault` branch is published publicly on GitHub, not kept
private/unmirrored. Owner's own words, translated: "publish it — this
is a full-fledged radar; when we decide to close it, we'll close it
then."

## Alternatives & Rationale

**A. Keep `vault` private/unmirrored (the prior default, rejected).**
This was inherited from SPEC C's deliberate non-decision, not a
considered choice in its own right — it no longer serves the project's
current framing as a public measuring instrument.

**B. Publish `vault` publicly (chosen).** Matches the project's current
framing directly, per explicit owner decision.

## Consequences

Branch protection on `vault` was not explicitly configured as part of
this decision. Previously, `vault` was protected on GitLab purely as a
technical prerequisite for the old mirror's "only protected branches"
filter (see ADR-0011) — that reason no longer applies after the full
migration (ADR-0013). This is an open item: it should be recorded in
`docs/BACKLOG.md`, not treated as resolved by this ADR.

## Confirmation & Revisit

Not yet confirmed by any branch-protection configuration — the open
item above is explicitly unresolved, not silently assumed safe.

Revisit once `docs/BACKLOG.md`'s tracked item for `vault` branch
protection is addressed, or if the owner's "when we decide to close it"
condition is ever met.

**Source.** 2026-08-25, same session as ADR-0013, explicit owner
decision closing a question left open since 2026-08-07.
