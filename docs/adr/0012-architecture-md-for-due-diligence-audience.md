---
id: ADR-0012
status: Accepted
supersedes: null
superseded_by: null
source_type: verbatim
---

# 0012 — ARCHITECTURE.md for a Due-Diligence Audience

## Status

Accepted.

## Context & Constraints

An explicit owner clarification, mid-interview, set the audience for
architecture documentation wider than previously stated anywhere: a
technical due-diligence audience (investor/partner), not only external
developers reading the code.

## Decision

`ARCHITECTURE.md` is a separate file, not a README extension, aimed
explicitly at that due-diligence audience. Its core content is three
structural mechanisms that guard against the "LLM generates
plausible-sounding text" failure mode: verdict decided by code
(`compute_status()`, with a real incident referenced directly in the
code's own docstring), the two-gate quarantine (see ADR-0005), and the
falsification cycle. It includes a mermaid diagram of trust gates
specifically — verdict → quarantine → confirm/promote — not a
duplicate of README's data-flow ASCII diagram.

## Alternatives & Rationale

**A. Text-only, no diagram (agent's own initial recommendation,
rejected).** Overridden by the owner: a diagram showing the
verification protocol specifically is not redundant with README's
already-visible data-flow view, and the due-diligence audience benefits
from seeing the trust mechanism, not just the pipeline shape.

**B. Separate ARCHITECTURE.md with a trust-gate diagram (chosen).**
Directly serves the due-diligence audience's actual question — why does
this pattern work as a measuring instrument — rather than restating
what README already shows.

## Consequences

The Roadmap section is deliberately kept to one line per item,
undetailed — spelling out unimplemented work in more depth risks
reading as a promise with no code behind it, which would work against
the due-diligence audience's actual need to trust what's documented.

A second README audit pass, separate from ADR-0007's SPEC B audit,
found a second real inaccuracy: the Layer 4 diagram claimed Forecasts
was implemented, with zero matches on `grep src/*.py`. Fixed with an
explicit "(planned, not implemented)" label rather than removing the
claim silently.

## Confirmation & Revisit

The Forecasts inaccuracy was confirmed via direct grep against the
source tree, not assumed from the diagram's own claim.

Revisit if Forecasts is ever actually implemented — the "(planned, not
implemented)" label should be removed at that point, not left stale.

**Source.** SPEC D, closed 2026-08-07.
