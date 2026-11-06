---
id: ADR-0026
status: Accepted
supersedes: null
superseded_by: null
source_type: verbatim
---

# 0026 — Adopt the Shared ToolTempest DocOps Checker (Core Component)

## Status

Accepted (2026-11-06). Proposed 2026-11-05.

## Context & Constraints

Radar pins ToolTempest in `.tooltempest.lock`, which covers one file, the
legacy `scripts/doc_sync.py`. That file is untracked and nothing invokes it;
the lock-integrity guard (ADR-0025) checks that this file matches the lock. No DocOps
checker ran in Radar, and the commit pinned before this decision contained
no DocOps checker (`scripts/docops.py`).

ToolTempest now ships three components: core (`scripts/`, `schemas/`), a
contract file and a client (`skills/`, `rules/`). Core is installed by
ToolTempest's `scripts/tooling.py materialize --apply`, run from a ToolTempest
checkout with `--root` and `--source`; a consumer without core does not hold that
script. Consumer hooks must make no network calls (ToolTempest ADR-0017).

Observations, with the tool version named where it matters:

- The shared checker reads a prose `SPEC.md` that has no `spec-state`, such as
  Radar's, as an active SPEC and fails it for lacking a milestones section.
- Git 2.44.0 runs `pre-push` on a push that updates nothing, and sends it zero
  bytes on stdin. A hook that has drained stdin once leaves a second reader
  with zero bytes.

Constraints: commits go directly to `main` and there is no pull request; the
data-only `vault` branch shares the hooks and never carried the lock or a
`SPEC.md`; Git does not clone hooks; the vendored files are deliberately
untracked (ADR-0025, owner decision D1-a).

## Decision

Radar consumes the ToolTempest core component alongside the ADR-0025
lock-integrity guard. The guard's decision (P2) is unchanged; Decision 4 removes
the advisory freshness warning that ADR-0025 described.

1. The lock is repinned to ToolTempest's `main` as of this adoption. The pinned
   commit is recorded in `.tooltempest.lock`. Core is
   materialized with ToolTempest's `scripts/tooling.py materialize --apply`,
   run from a ToolTempest checkout that contains the pinned commit, with
   `--root` set to this repository and `--source` set to that checkout
   (without `--apply` the command only prints a plan). It stays untracked and
   is covered by `.gitignore`. The lock schema and the guard's scope do not
   change.
2. The versioned hooks run the checker after the lock guard: `pre-commit` runs
   `docops.py check --tree index`, `pre-push` runs
   `docops.py check --push-stdin`. A missing checker or any non-zero exit
   blocks, including the exit codes that mean "no verdict" or "not
   established". The checker is looked up in the working tree first, then in
   the main working tree, as the lock checker is.
3. `pre-push` reads its stdin once, at the top, into a temporary file. The lock
   guard and the checker both read that capture. A capture of zero bytes means
   a push that updates nothing, and neither the lock guard nor the checker is run.
4. The hook scripts make no network call. The advisory freshness warning of
   `pre-push` is removed; pin freshness is checked by `scripts/tooling.py`.
5. `SPEC.md` declares `spec-state: idle` in frontmatter while there is no
   active task. The checker reads that marker as "no active SPEC".
6. The core component and the contract file, which ToolTempest installs
   together, are adopted. The contract file is the single source of the consumer
   obligation. The client component (`skills/`, `rules/`) is not adopted.
7. Constitution section 7 points to the consumer contract. It no longer repeats
   the consumer obligation: it points to `docs/tooltempest/consumer-contract.md`
   in `mikkiola/tooltempest`, at the commit pinned in `.tooltempest.lock`, and a
   dated note records the replacement. The contract file is delivered with the
   core component: it is untracked, git-ignored, and absent from a fresh clone
   until core is materialized. Radar's own copy of the obligation text is
   removed because one source avoids drift.

## Alternatives & Rationale

| Option | Verdict |
|---|---|
| A. Keep only the ADR-0025 guard | Rejected: `SPEC.md` and the documents stay unchecked, and the pin keeps pointing at a commit with no checker. |
| B. Adopt core and run the checker in the hooks (chosen) | Smallest change that gives Radar the shared contract; reuses the installer and the guard. |
| C. Track the core files in Git | Rejected here: it reverses owner decision D1-a of ADR-0025 and puts a large body of third-party code into this repository. |
| D. Let the guard and the checker each read the live stdin | Rejected: a stream is consumed once, and the second reader receives nothing. |
| E. Treat the checker's "no verdict" and "not established" exits as a pass | Rejected: an exit that gives no verdict must not read as success; the hooks fail closed. |

## Consequences

- A clone that activates the hooks needs core materialized, or its commits and
  pushes are blocked with a pointer to the procedure. A clone that never
  activated the hooks behaves as before. The data-only `vault` working tree
  finds the checker in the main working tree; a push that updates nothing
  needs no checker.
- Core is not present in a fresh clone by default; it requires an explicit
  bootstrap from a ToolTempest checkout. CI does not receive it unless that
  bootstrap is performed. ADR-0025 gives the same reason for the vendored file.
- A fresh clone and CI do not have the text of the obligation until core is
  materialized.
- The hooks execute the materialized checker without a hash check: the lock
  covers only `scripts/doc_sync.py`, and no hook runs `scripts/tooling.py
  verify`, which compares each installed core file with the hash that the lock declares for it or, failing that, the receipt records.
- The ADR-0025 guard remains a separate Radar mechanism. `scripts/tooling.py
  verify` does not reproduce its contract: it needs `--source` set to a
  ToolTempest checkout that contains the pinned commit, it reads the lock only
  from a file (not from the index or from a pushed revision), it has no
  not-applicable result, and it reports a malformed or missing lock with exit
  status 1 where the guard returns 2. Replacing the guard with it would remove
  protections, so this decision does not move the verification. A move needs the
  shared mechanism to provide those behaviors first.
- This decision adds no CI job and no server-side check. The hooks are the only
  enforcement it adds; they bind only clones that installed them, and
  `--no-verify`, a removed hook, or an unactivated clone bypasses them.
- `doc_sync.py` and `doc_sync_tier2.py` are installed with core but wired into
  nothing. Hook wiring of the legacy helper remains open in the backlog.
- Pin freshness is no longer shown at push time. It is visible when
  `scripts/tooling.py status` or `verify` runs. Without a `--source` checkout
  that contains the pinned commit, `status` and `verify` report local integrity
  as not established, or as failed when an installed file is missing or edited,
  and report freshness as unknown. Freshness never changes the exit status.
- Without an impact report, `docops.py check` assesses the SPEC structure only.
  The hooks enforce no other documentation dimension.
- A later repin follows the repin evidence of the consumer contract.

## Confirmation & Revisit

Verified by `scripts/tooling.py verify`, by `docops.py check --tree index` on
the staged tree, and by the hook cases in `tests/test_lock_guard_hooks.py`
(single capture, zero-byte push, blocking exits, missing checker). The results
of the run that preceded the adopting commit are not recorded in this record.

Revisit if: the core files become tracked; the lock schema covers more than one
file; a third reader of the push stdin is added; the client component is
adopted; the shared mechanism reads the lock from the index and from a pushed
revision, reports not applicable, and separates an error from a violation in
its exit status; or the checker's exit-code contract changes.

**Source.** Radar sessions of 2026-11-05 and 2026-11-06: owner instructions for DocOps Stage 7
after a read-only reconnaissance of the same day. An external AI review of the change, run by the Owner before acceptance, found the wording of the install step and did not decide the architecture.
