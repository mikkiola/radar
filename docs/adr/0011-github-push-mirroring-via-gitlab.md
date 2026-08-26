---
id: ADR-0011
status: Superseded
supersedes: null
superseded_by: ADR-0013
source_type: verbatim
---

# 0011 — GitHub Push-Mirroring via GitLab

## Status

Superseded by ADR-0013 (2026-08-25 full platform migration eliminated
GitLab entirely — this mechanism no longer physically exists).

## Context & Constraints

Radar needed a public GitHub presence while GitLab remained the
project's source of truth. GitLab's mirroring feature offers no
blacklist option — only a whitelist, via "Only mirror protected
branches" — so any mirroring design had to work within that
constraint.

## Decision

GitHub push-mirroring was configured entirely through GitLab's UI, with
no CI code involved. Only the protected default branch was mirrored to
`mikkiola/radar` (public), using "Only mirror protected branches" — the
only available whitelist mechanism GitLab offers. `vault` was
deliberately not mirrored at this point.

## Alternatives & Rationale

**A. A CI-job-based mirror (plan B, not needed).** GitLab's built-in UI
mirroring was sufficient for the whitelist scope needed, so a
custom CI-based mirror was never built.

**B. GitLab UI mirroring, protected-branches-only (chosen).** Matched
the actual requirement (mirror only the default branch, not `vault`)
using a built-in platform feature rather than custom code.

## Consequences (at the time)

A new fine-grained GitHub PAT was created, scoped only to
`mikkiola/radar`. GitHub's classic branch protection had lost the
"Restrict who can push" function — since moved to Rulesets — which was
found and fixed as a real discrepancy between SPEC.md and the actual
GitHub UI, not assumed from stale documentation.

## Confirmation & Revisit

Confirmed at the time via the real GitHub UI, which surfaced the
"Restrict who can push" / Rulesets discrepancy directly.

Superseded outright by ADR-0013's full GitLab-to-GitHub migration: with
GitLab no longer part of the project, this mirroring mechanism has no
remaining referent, not merely an outdated one.

**Source.** SPEC C, closed 2026-08-07.
