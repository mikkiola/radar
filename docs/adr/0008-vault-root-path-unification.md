---
id: ADR-0008
status: Accepted
supersedes: null
superseded_by: null
source_type: verbatim
---

# 0008 — `VAULT_ROOT` Path Unification

## Status

Accepted.

## Context & Constraints

`VAULT_PATH` was resolved through four different mechanisms across five
CI jobs — inconsistent enough that the same conceptual path could be
computed differently depending on which job touched it. `VAULT_PATH` was
confirmed, via a falsifiable check, not to be set as a separate GitLab
CI/CD Variable — ruling out a hidden external dependency on the old
name.

## Decision

`VAULT_PATH`'s four resolution mechanisms are unified into a single
`VAULT_ROOT` — a deliberately breaking rename, not a backward-compatible
alias.

## Alternatives & Rationale

**A. Keep the `VAULT_PATH` name with new, unified semantics (rejected).**
Same name, different meaning over time is exactly the kind of implicit,
unverifiable contract this project's design principles reject — a
future reader or script could not tell, from the name alone, which
semantics were in effect.

**B. Breaking rename to `VAULT_ROOT` (chosen).** Makes the semantic
change visible at every call site, forcing each one to be checked
rather than silently inheriting new behavior under an old name.

## Consequences

Ten files were touched — not the five originally scoped, found through
line-by-line verification. `backfill_frontmatter.py` was the tenth,
found during this same verification pass and included in the migration
by owner decision.

A separate diff-review step (distinct from line-by-line verification)
found two further bugs that line-by-line verification alone would not
have caught: a `NameError` at `patterns.py:800`, and a stale docstring.

## Confirmation & Revisit

Confirmed via the falsifiable check that `VAULT_PATH` was not a
separate GitLab CI/CD Variable, and via two independent verification
passes (line-by-line, then diff-review) that together found all ten
affected files and the two additional bugs.

Revisit if a future path-resolution need reintroduces multiple
mechanisms for the same conceptual path — that was the exact condition
this ADR eliminated.

**Source.** SPEC A.5, closed 2026-08-07, discussed with external AI.
