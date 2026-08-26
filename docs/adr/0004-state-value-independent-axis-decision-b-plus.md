---
id: ADR-0004
status: Accepted
supersedes: null
superseded_by: null
source_type: verbatim
---

# 0004 — `state_value` as an Independent Axis ("Decision B+")

## Status

Accepted.

## Context & Constraints

`maturity_score` (see ADR-0003) is a snapshot of code maturity at
assessment time. It says nothing about lifecycle trend or momentum — a
mature, actively-developed project and a mature, abandoned one can look
identical on that axis alone. No transition history existed yet to fit
a proper transition-probability model against.

## Decision

`state_value` and `state_confidence` are new flat frontmatter fields,
forming an axis independent of `maturity_score` — lifecycle
trend/momentum, not a snapshot of code maturity. This is "Decision B+":
lay down the data schema now under a Markov assumption (state depends
only on the previous state), and defer transition-math until enough
history has accumulated to fit it meaningfully. `state_confidence` is
computed deterministically from `evidence_log` length at write time, not
taken from the model's self-report.

## Alternatives & Rationale

**A. Full HMM with fitted transition probabilities (rejected — not yet,
by design).** There was no history yet to fit transition probabilities
against; building the full model now would mean fitting parameters on
no data.

**B+. Lay down the schema, defer the math (chosen).** Captures the
axis and the data needed to eventually fit a real model, without
pretending a model exists before there's data to justify one.

Two independent external opinions converged on this outcome, and were
critically cross-examined for falsifiability and hidden assumptions
rather than accepted on agreement alone.

## Consequences

`analyze.py` gained a `CLASSIFICATION_TOOL` enum (Prototype / Growing /
Mature / Maintenance / Declining / Archived / Spam). `vault_write.py`
gained `append_event()`, using a single `state_transition` event type.
A new `confirm_candidate` CI job implements human-in-the-loop review:
approve moves a candidate to `VALIDATED_SHIFT`, reject to
`REJECTED_NOISE`.

Falsifiable confirmation: a real `analyze.py` call against `react` vs.
`angular.js` produced identical `maturity_score=5` for both, but
`state_value` diverged (Mature vs. Maintenance) — confirming the two
axes are actually independent, not just independent by construction.

## Confirmation & Revisit

Confirmed by the react/angular.js falsification test above: if the two
axes were not truly independent, that test would have produced matching
`state_value` for matching `maturity_score`, and did not.

Revisit once enough `evidence_log` history has accumulated to fit real
transition probabilities — at that point the deferred half of Decision
B+ becomes actionable.

**Source.** 2026-08-04, two independent external opinions, critically
cross-examined.
