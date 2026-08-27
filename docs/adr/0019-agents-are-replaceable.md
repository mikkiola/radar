---
id: ADR-0019
status: Accepted
supersedes: null
superseded_by: null
source_type: inferred
---

# 0019 — Agents Are Replaceable

## Status

Accepted.

## Context & Constraints

Radar's pipeline calls Anthropic models by name through
`model_config.json` (`src/99_System/model_config.json`), the single
source for model IDs — no script hardcodes a specific model ID. This
only matters if the architecture is genuinely meant to survive a model
or provider change, not just a version bump within one provider.

## Decision

The architecture does not depend on any specific model or provider. A
model can be swapped without redesigning the pipeline around it.

## Alternatives & Rationale

**A. Design around one specific model's quirks (rejected,
implicit).** A system without this principle would hardcode model IDs
and provider-specific behavior directly into `analyze.py`/`patterns.py`/
`fetch_analysts.py`, making a future provider or model-family change a
rewrite rather than a config edit.

**B. Agents Are Replaceable (chosen).** `model_config.json` centralizes
the one place model identity is set; the pipeline's actual logic
(`compute_status()`, `apply_quarantine_gate()`, the falsification loop)
is written against structured inputs/outputs, not a specific model's
behavior.

## Consequences

`model_config.json` is only ever updated by hand, after a smoke test
and a breaking-changes check — treated as a deliberate, tested swap,
not a casual edit.

## Confirmation & Revisit

Confirmed structurally: a single config source, no hardcoded model IDs
found across the pipeline scripts during this session's
`docs/ARCHITECTURE.md` audit. Not confirmed by an actual full provider
swap — the architecture has changed models within Anthropic's own
lineup, not across providers. Revisit if a cross-provider swap is ever
attempted and something in the pipeline turns out to be
Anthropic-specific beyond `model_config.json`.

**Source.** Formalizes a pre-existing, previously undocumented
principle, found stated in prose in `docs/CONSTITUTION.md` with no ADR
of its own during that file's 2026-08-27 rewrite. No original decision
date or session is recoverable.
