---
id: ADR-0023
status: Accepted
supersedes: null
superseded_by: null
source_type: inferred
---

# 0023 — SHIFT: Content Selection Criterion for the Channel

## Status

Accepted.

## Context & Constraints

The Telegram channel (`@radar_public`) publishes a filtered subset of
what Radar tracks — not everything that passes assessment becomes a
post. `README.md` explicitly disclaims Radar as "not a news
aggregator, not a GitHub scraper," so the channel needs its own
selection criterion distinct from "did this pass novelty assessment."

## Decision

Content is published only if it carries a SHIFT — a change in how
knowledge or value is organized in the ecosystem, caught before it
becomes common knowledge.

Passes: a new ecosystem behavior pattern, a change in who knowledge is
addressed to, a change in decision-making structure, a shift in what
becomes infrastructure.

Doesn't pass: product news, a release feature rundown, "an interesting
tool," this week's popular topic.

## Alternatives & Rationale

**A. Publish any AI/tooling news that clears the novelty-assessment bar
(rejected, implicit).** Treating `VALIDATED_SHIFT` status alone as
sufficient grounds to publish. Rejected because it collapses the
channel into a generic news aggregator/GitHub-tool-tracker, which
`README.md` explicitly disclaims Radar being; a system-level novelty
verdict and a channel-worthy SHIFT are different questions, and
conflating them would flood the channel with tool announcements that
pass technical novelty but carry no structural signal.

**B. SHIFT as a separate, additional filter (chosen).**
`VALIDATED_SHIFT` status answers "is this claim true and confirmed";
the SHIFT criterion answers a different question — "does this specific
confirmed claim matter to how the ecosystem is organized" — a second
gate, not a restatement of the first.

## Consequences

`telegram_post.py`'s publishing decision is not simply "post every
`VALIDATED_SHIFT`" — the SHIFT criterion is an additional editorial
filter applied on top of the pipeline's own verdict machinery.

## Confirmation & Revisit

Not mechanically enforced in code as a separate function — currently
applied as an editorial judgment at posting time, not a
`compute_status()`-style structural gate. Revisit if the channel's
actual published history shows drift toward general AI/tooling news
despite this stated criterion — that would be evidence the criterion
isn't actually being applied, not evidence it should change.

**Source.** Formalizes a pre-existing, previously undocumented
criterion, found stated in prose in `docs/CONSTITUTION.md` with no ADR
of its own during that file's 2026-08-27 rewrite. No original decision
date or session is recoverable.
