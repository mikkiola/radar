---
id: ADR-0010
status: Accepted
supersedes: null
superseded_by: null
source_type: verbatim
---

# 0010 — Betterleaks Over Gitleaks for Secret Scanning

## Status

Accepted.

## Context & Constraints

The `security_secrets` CI job needed a secret-scanning tool. The agent
found, mid-interview, that Betterleaks is a drop-in-compatible
successor to Gitleaks from the same author — a real fork discovered
through actual web search and GitHub API checks, not assumed.

## Decision

Betterleaks — not Gitleaks — is the secret-scanning tool for the
`security_secrets` CI job. This was an explicit owner override of the
agent's own recommendation.

## Alternatives & Rationale

**A. Gitleaks (agent's recommendation, not chosen).** Recommended by
the agent specifically for its maturity as the more established tool.

**B. Betterleaks (owner's choice, chosen).** Chosen by the owner for
its detection engine and supply-chain model. Recorded explicitly as an
owner decision made against the agent's own recommendation, not as
silent agreement with it.

## Consequences

A local baseline scan was run with both TruffleHog and Betterleaks,
across both branches, full history. Betterleaks: 0 findings. TruffleHog:
6 false positives, all a known Lob-detector class that confuses test
function names with Lob's API key format. This is one real-world data
point favoring the Betterleaks call — not a controlled comparison,
since Gitleaks itself was never run against this repo directly.
`security_secrets` goes straight to hard-fail in CI, with no baseline
allowlist file needed.

## Confirmation & Revisit

Confirmed by the local baseline run described above: zero real secrets
found by either tool, and Betterleaks producing zero false positives
where TruffleHog produced six.

Revisit if Betterleaks' detection engine or supply chain changes in a
way that no longer matches the reasoning that justified choosing it
here.

**Source.** SPEC E, closed 2026-08-07 — explicit owner override of the
agent's recommendation.
