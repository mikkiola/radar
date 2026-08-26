---
id: ADR-0003
status: Accepted
supersedes: null
superseded_by: null
source_type: verbatim
---

# 0003 — Frontmatter Status, README/Manifest Signal, and 2D Matrix with CoVe

## Status

Accepted.

## Context & Constraints

`01_Assessments/` needed a single, unambiguous, machine-readable source
of a candidate's status. A binary SHIFT/NOISE text field, with a
separate human-readable `**Оценка:**` field, created a split-brain
between the machine-readable and human-readable representations of the
same status — the two could drift out of agreement with nothing to
catch it. Separately, `analyze.py` was only given a repo's title,
description, and URL — no data against which to actually verify
source claims made in those fields.

## Decision

`01_Assessments/` uses YAML frontmatter — not a binary SHIFT/NOISE text
field — as the single machine-readable source of status.
`analyze.py` now receives a repo's README, manifest, and root file tree
via `ghapi`, not just title/description/url. Assessment itself uses a
2D Maturity × Novelty matrix, scored with a single-pass Chain-of-
Verification (CoVe). The final status is always computed in code via
`compute_status()`, never taken directly from the model's self-report.

## Alternatives & Rationale

**A. Binary SHIFT/NOISE + text field `**Оценка:**` (rejected).**
Created exactly the split-brain problem described above between
machine-readable and human-readable status. Also, without README and
manifest data in the prompt, the model had nothing to verify its own
claims against.

**B. Frontmatter status + 2D matrix + CoVe + code-computed status
(chosen).** A single machine-readable field eliminates the split-brain.
Feeding real README/manifest/file-tree data gives the model something
concrete to check claims against. Computing final status in code, not
via model self-report, keeps the verdict auditable and independent of
whatever the model says about itself.

## Consequences

`vault_write.py` is new, built around a single `write_verdict_entry()`
function. `backfill_frontmatter.py` migrated 86 existing files to the
new frontmatter shape.

Three real bugs were found during testing before this shipped: a
backfill idempotency bug that produced a duplicate frontmatter block on
re-run; a directory-listing bug in `fetch_repo_signal()` where root
directories weren't actually passed into the prompt; and a production
cron conflict, resolved via `git merge --no-commit --no-ff`.

## Confirmation & Revisit

Confirmed by the three bugs above being found and fixed in testing
before rollout, not discovered later in production. The
production-cron conflict was resolved without discarding either side's
work.

Revisit if a future signal source needs data `ghapi`'s README/manifest/
file-tree call doesn't cover — the 2D matrix and CoVe scoring assume
this specific input shape.

**Source.** Radar 2.0 Phase 2, 2026-08-03.
