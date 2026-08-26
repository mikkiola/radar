---
id: ADR-0007
status: Accepted
supersedes: null
superseded_by: null
source_type: verbatim
---

# 0007 — SPEC A: `src/` + `tests/` Reorganization

## Status

Accepted.

## Context & Constraints

All Python modules lived at the flat repo root. This SPEC's original
interview decision was to move them into a nested `src/radar/` package.
That decision did not survive contact with a real `pytest` run, which
produced a `ModuleNotFoundError` against the nested-package layout.

## Decision

All Python modules moved into a `src/` + `tests/` layout, without a
nested `src/radar/` package — flat imports are preserved, since Radar
is not an installable package. `99_System/` moved alongside the code,
to `src/99_System/`.

## Alternatives & Rationale

**A. `src/radar/` nested package (originally decided, then reversed).**
This was the interview's original decision. It was reversed during
implementation after a real `pytest` run failed against it. The
reversal was proposed and insisted on by the owner personally — not
found through the project's usual line-by-line SPEC-vs-code
verification, because that method catches textual mismatches between a
SPEC and the code, not an architectural mismatch between an accepted
folder-structure decision and physical runtime reality.

**B. Flat `src/` + `tests/`, no nested package (chosen).** Matches how
Radar is actually run and tested; avoids the import errors the nested
layout produced.

## Consequences

Six scripts resolve `model_config.json` via a `__file__`-relative path,
not `cwd` — moving them without finding this would have silently broken
CONSTITUTION Absolute Rule 6. `vault_write.py` (a hub with nine
dependents) was migrated last, in isolation, per the project's
risk-asymmetry principle for high-fan-in modules. This produced the
first real GitLab MR in the project's history for a merge of this kind.

## Confirmation & Revisit

The reversal from nested to flat layout was confirmed the only way an
architecture-vs-runtime mismatch can be: by actually running `pytest`
against the accepted design and observing the failure, not by
re-reading the SPEC text.

Revisit if Radar is ever packaged for installation — the "no nested
package" decision is explicitly conditioned on Radar staying
non-installable.

**Source.** SPEC A, closed 2026-08-06.
