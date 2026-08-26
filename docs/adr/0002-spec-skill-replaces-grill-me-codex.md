---
id: ADR-0002
status: Accepted
supersedes: null
superseded_by: null
source_type: verbatim
---

# 0002 — `spec` Skill Replaces Grill Me + Dual Review / Codex

## Status

Accepted.

## Context & Constraints

The project has a standing principle: architectural decisions must go
through a mandatory pre-decision interview before implementation — see
ADR-0001 for a decision produced under the predecessor tool. That
predecessor was Grill Me + Dual Review, built on
`chaseai-yt/grill-me-codex` plus the Codex CLI — an external tool
depending on a second model provider (OpenAI) alongside Claude Code.
That dependency was itself a source of complexity and a failure point,
independent of whether the interview method it implemented was sound.

## Decision

The mandatory pre-architectural-decision interview is now performed via
the `spec` skill
(`~/.claude/skills/spec/SKILL.md`, `disable-model-invocation`,
owner-triggered only via `/spec`). The underlying principle — a
mandatory interview before architectural decisions — is unchanged; only
the tool implementing it changed.

## Alternatives & Rationale

**A. Keep grill-me-codex (rejected).** The external Codex CLI / OpenAI
dependency introduced complexity and a failure point that provided no
benefit over a native alternative.

**B. `spec` skill (chosen).** Uses native Claude Code tooling only, with
no second model provider in the loop. Owner-triggered via `/spec`,
`disable-model-invocation` set so the interview cannot fire on its own.

## Consequences

A SPEC.md produced by `/spec` must be verified line-by-line against the
real code before implementation begins. This session's own line-by-line
verification found SPEC.md wrongly assuming three things existed in the
codebase that didn't — that finding became CONSTITUTION Rule 28, a
direct product of adopting this tool.

## Confirmation & Revisit

Confirmed by use: the line-by-line verification step this ADR requires
was exercised in the same session that produced this decision, and
surfaced the three false assumptions noted above rather than letting
them reach implementation.

Revisit if the `spec` skill's own interview mechanics change in a way
that no longer produces a written, line-by-line-verifiable SPEC.md.

**Source.** Session, 2026-08-01.
