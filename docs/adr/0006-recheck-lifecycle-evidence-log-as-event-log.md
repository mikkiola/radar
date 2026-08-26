---
id: ADR-0006
status: Accepted
supersedes: null
superseded_by: null
source_type: verbatim
---

# 0006 — `evidence_log` Is an Event Log, Not a Measurement Log

## Status

Accepted.

## Context & Constraints

Whether `evidence_log` should record repeated snapshots (a measurement
log) or state-transition events — entering or exiting a condition — was
a genuine open question, revised mid-interview after discussion with an
external AI. The two shapes imply different consumers: a measurement
log needs downstream logic to detect transitions itself; an event log
records only the transitions, with detection happening once, at write
time.

## Decision

`evidence_log` is an event log: it records state-transition events
(entered/exited a condition), not repeated measurement snapshots.
`detect_transition()` compares the current observation against the
pair's last recorded event *before* `append_event()` is called — the
enter/exit decision is made by the calling code, and `append_event()`
itself stays a pure append with no decision logic of its own.

## Alternatives & Rationale

**A. Extend `write_verdict_entry()` with a conditional (rejected).**
That function is tightly coupled to real verdicts (see ADR-0003);
overloading it with evidence-only logic was the wrong fit.

**B. A license-expression library for license-change detection
(rejected).** Found via line-by-line verification that the GitHub API
returns an atomic `spdx_id`, not a composite license expression — plain
string comparison is sufficient, and a library would have added
complexity for a comparison problem that doesn't exist.

**C. Event log + `detect_transition()` performed by the caller +
pure-append `append_event()` (chosen).** Matches what the data actually
needs to represent (transitions, not snapshots) and keeps the append
function free of decision logic that belongs with the caller.

## Consequences

`recheck_lifecycle.py` is new — the project's first monthly GitLab
Schedule. Only `status == VALIDATED_SHIFT` repos are in scope.
`repo.archived` is the only signal that changes status directly (to
`ARCHIVED_DEAD`, with no quarantine step — archival is treated as final
for an already-confirmed verdict). `visibility_lost` /
`visibility_restored` were added as a fifth evidence-only signal, using
a deliberately neutral name — going private is not itself a red flag.

## Confirmation & Revisit

The `spdx_id` string-comparison decision was confirmed by direct
line-by-line verification against the actual GitHub API response shape,
not assumed from documentation.

Revisit if a future evidence signal needs comparison logic more complex
than atomic-value equality — the "no library needed" conclusion here is
specific to `spdx_id`'s current shape.

**Source.** 2026-08-05, second session same day, Radar 2.0 Phase 3,
point 2.
