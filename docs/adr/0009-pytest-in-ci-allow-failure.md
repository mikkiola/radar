---
id: ADR-0009
status: Accepted
supersedes: null
superseded_by: null
source_type: verbatim
---

# 0009 — pytest in CI with `allow_failure: true`

## Status

Accepted.

## Context & Constraints

A genuine tension existed between two goals: `test` should be the
pipeline's first stage, and a test failure must not block the `pages`
job. Making `test` a real, first-stage, blocking job would satisfy the
first goal at the cost of the second.

## Decision

`pytest` runs as a real CI job (`test`), first stage in the pipeline,
push-triggered, with `allow_failure: true`.

## Alternatives & Rationale

The tension above was found and resolved by the agent itself, before
implementation — not discovered after a failure blocked something in
production. `allow_failure: true` resolves the conflict directly: `test`
stays first and real, without either revisiting its stage position or
weakening `pages`'s independence from it.

`allow_failure`'s behavior was deliberately not verified with a
separate dummy job — it was trusted as documented, stable GitLab
platform behavior, not treated as a project-specific configuration
assumption requiring its own test.

## Consequences

This is the first push-trigger in the project that fires automatically
with no namespace-variable gate in front of it.

## Confirmation & Revisit

Confirmed by GitLab's own documented semantics for `allow_failure`,
relied on directly rather than re-verified locally.

Revisit if GitLab's documented `allow_failure` semantics change, or if
`pages` ever needs to depend on `test` actually passing — at that point
the platform-behavior assumption this ADR relies on should be
re-checked, not assumed to still hold.

**Source.** SPEC A.6, closed 2026-08-07.
