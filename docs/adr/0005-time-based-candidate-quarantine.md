---
id: ADR-0005
status: Accepted
supersedes: null
superseded_by: null
source_type: verbatim
---

# 0005 — Time-Based Candidate Quarantine

## Status

Accepted.

## Context & Constraints

An epistemic `CANDIDATE_LOW_CONFIDENCE` status already existed, for
cases where the model itself is unsure at assessment time. A separate
problem needed its own gate: a repo with no evidence history yet needs
time to accumulate evidence before a verdict can be trusted, and that
gate needed a causally clean trigger — not a proxy like repo age or
star count, which correlate with but don't directly cause
evidence-worthiness.

## Decision

`status: CANDIDATE` is a time-based quarantine of 14 days, triggered
when `evidence_log` is empty at assessment time — a direct, causally
clean criterion rather than a proxy. This is separate from and
independent of the existing epistemic `CANDIDATE_LOW_CONFIDENCE`.
`check_repo_alive()` returns exactly three outcomes — alive / dead /
no-data — deliberately not a fuller state machine.

## Alternatives & Rationale

**A. Full FSM with `repo_state` / `unknown_since` / `LOST` states
(rejected).** Proposed during an external-opinion review, and
explicitly rejected as violating ADR-0004's Decision B+: it would
introduce state complexity the Markov-assumption schema wasn't designed
to carry yet.

**B. 14-day time-based quarantine + three-outcome `check_repo_alive()`
(chosen).** Matches the actual need (give evidence time to accumulate)
without importing state-machine complexity the rest of the schema
isn't ready for.

## Consequences

`apply_quarantine_gate()` and `confidence_label()` were added to
`analyze.py`. `promote_candidates.py` is new, running as a daily CI
job. Rejection after the 14-day window goes straight to
`REJECTED_NOISE` with no retry cycles. Promotion posts silently to
Telegram — the same principle already used for `confirm_candidate.py`
approvals.

## Confirmation & Revisit

The three-outcome constraint on `check_repo_alive()` was confirmed as
sufficient for this gate's actual decision (quarantine vs. not) without
building the rejected full FSM.

Revisit if a future case needs to distinguish "dead" from "unknown for
a while" in a way the three-outcome function can't represent — at that
point the FSM rejected here may need re-examination on its own terms,
not folded silently back in.

**Source.** 2026-08-05, Radar 2.0 Phase 3, point 1.
