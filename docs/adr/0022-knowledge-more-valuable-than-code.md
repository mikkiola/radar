---
id: ADR-0022
status: Accepted
supersedes: null
superseded_by: null
source_type: inferred
---

# 0022 — Knowledge Is More Valuable Than Code

## Status

Accepted.

## Context & Constraints

Radar's vault (assessments, patterns, analyst history) accumulates
over the system's entire lifetime and can't be regenerated once
lost — a piece of code, by contrast, can always be rewritten from the
same requirements. The `vault` branch (`docs/ARCHITECTURE.md`'s
Platform row) is a separate branch specifically so vault data and
pipeline scripts have independent histories.

## Decision

In a conflict between protecting code and protecting knowledge,
knowledge wins. Stated protection priority, highest first: Knowledge,
Metadata, Infrastructure, Code.

## Alternatives & Rationale

**A. Treat code and data with equal protection priority (rejected,
implicit).** A system without this principle might, for example,
accept a risky vault-write path for the sake of a cleaner script, or
treat a vault-corrupting bug with the same urgency as a code style
issue — both wrong given that lost assessment history can't be
regenerated the way code can.

**B. Knowledge Is More Valuable Than Code (chosen).** This is the
stated reason vault write discipline (targeted edits only,
`os.path.exists()` before write, `check_frontmatter.py` as a gate) is
treated as an unconditional rule rather than an ordinary
code-quality preference.

## Consequences

This principle is the reason assessment and pattern files are governed
by an unconditional never-overwrite-wholesale rule, while code files
(outside the `README.md`/`LICENSE` exception) get ordinary editing
discipline instead of a hard block.

## Confirmation & Revisit

Confirmed by the asymmetry already encoded in `docs/CONSTITUTION.md`'s
write-discipline rules (vault files: hard, unconditional constraints;
code files: ordinary practice). Revisit if this priority order is ever
found to have caused a worse outcome than a code-first priority would
have.

**Source.** Formalizes a pre-existing, previously undocumented
principle, found stated in prose in `docs/CONSTITUTION.md` with no ADR
of its own during that file's 2026-08-27 rewrite. No original decision
date or session is recoverable.
