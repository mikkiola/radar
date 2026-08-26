---
id: ADR-0013
status: Accepted
supersedes: ADR-0011
superseded_by: null
source_type: verbatim
---

# 0013 — Full Platform Migration: GitLab to GitHub

## Status

Accepted.

## Context & Constraints

GitLab compute-minutes were exhausted, with no realistic path to
renewal. Separately, there was a case for consolidating repository
ownership under the `mikkiola` GitHub account, which already owns
`article-pipeline` and `tooltempest`. The session's original goal —
the DocOps/ToolTempest merge — was explicitly deferred as less urgent
than resolving the compute exhaustion.

A real secret-exposure incident was found during the migration:
GitLab's `/variables` API endpoint returned all six CI/CD secret values
in plaintext to an authorized caller with sufficient token scope —
`masked: true` only protects CI job log output, not the API response
itself.

## Decision

GitHub becomes the sole repository and source of truth; the GitLab
repository was sent to deletion. `master` was renamed to `main` on both
platforms as a new branch created from the same commit — not an
in-place rename — before switching source-of-truth. `vault` moved to
GitHub as a full branch, not via the old push-mirror mechanism (see
ADR-0011), which only ever covered protected branches — full history
preserved (1879 objects), with the SHA confirmed identical on both
platforms before the GitLab repository was deleted.

## Alternatives & Rationale

No alternative was seriously considered. The trigger — GitLab compute
exhaustion — left a full migration as the only realistic path forward;
staying on GitLab was not an option once compute was gone, and a
partial migration would have left the mirroring gap this ADR closes
still open.

## Consequences

Thirteen GitLab CI jobs became nine GitHub Actions workflow files plus
one composite action (`vault-write`), eliminating roughly 15 lines of
duplicated bash previously repeated across seven places. All six
secrets were rebuilt from scratch — not migrated — as a direct response
to the plaintext-exposure incident found above. Schedules were
recalculated from Asia/Bangkok to UTC.

`vault-write` uses a dedicated PAT (`GH_VAULT_PUSH_TOKEN`), not the
built-in `GITHUB_TOKEN` — the built-in token's events deliberately don't
cascade further workflow runs (GitHub's anti-loop protection), which
would have broken `pages.yml`'s simple `on: push` reaction to vault
pushes.

Workload Identity Federation was considered and rejected for
`ANTHROPIC_API_KEY` — a real Anthropic-supported feature, but it
requires manual RFC 7523 token-exchange logic in each hand-written
pipeline script, disproportionate to this session's actual scope.

This supersedes ADR-0011 outright: GitHub push-mirroring via GitLab is
not merely outdated but physically impossible once GitLab is gone.

## Confirmation & Revisit

Confirmed via SHA comparison of `vault`'s full history (1879 objects) on
both platforms before the GitLab repository was deleted — an
irreversible step taken only after that confirmation passed. The
secret-exposure finding was confirmed directly against GitLab's
`/variables` API response, not assumed from its documented `masked`
behavior.

Revisit if GitHub's anti-loop token-cascade behavior changes, or if
Workload Identity Federation's cost/complexity tradeoff changes enough
to reconsider it for `ANTHROPIC_API_KEY`.

**Source.** 2026-08-25, triggered by GitLab compute-minutes exhaustion.
