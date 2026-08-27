---
id: ADR-0020
status: Accepted
supersedes: null
superseded_by: null
source_type: inferred
---

# 0020 — Graceful Degradation

## Status

Accepted.

## Context & Constraints

Radar's pipeline runs as 9 separate GitHub Actions workflow files
(`docs/ARCHITECTURE.md`'s CI/CD row) rather than one monolithic job —
collection, assessment, pattern clustering, external analyst input,
lifecycle recheck, and publishing all run as distinct,
independently-scheduled steps.

## Decision

One component failing doesn't stop the whole system. A single stage's
failure is contained to that stage, not propagated into unrelated
stages.

## Alternatives & Rationale

**A. One monolithic pipeline run (rejected, implicit).** A system
without this principle would run collection through publishing as one
atomic job — a single failure (e.g. one bad API response in
`fetch_analysts.py`) would block collection, assessment, and publishing
together, even though those are logically independent concerns.

**B. Graceful Degradation (chosen).** Splitting into 9 workflow files,
each independently scheduled and triggerable, means a failure in one
(e.g. `weekly-patterns.yml`) doesn't block `daily-run.yml` or
`publish.yml` from running on their own schedules.

## Consequences

The `needs:` dependency declared between `patterns`/`analysts`/
`check_models` in `weekly-patterns.yml` is a deliberate, narrow
exception — an intentional ordering dependency, not a sign the whole
pipeline is coupled.

## Confirmation & Revisit

Confirmed structurally by the current 9-workflow CI/CD split itself.
Not confirmed by an actual observed partial-failure incident within
this session. Revisit if a real production failure is found to have
cascaded across workflow boundaries despite this design.

**Source.** Formalizes a pre-existing, previously undocumented
principle, found stated in prose in `docs/CONSTITUTION.md` with no ADR
of its own during that file's 2026-08-27 rewrite. No original decision
date or session is recoverable.
