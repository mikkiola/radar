---
id: ADR-0025
status: Proposed
supersedes: null
superseded_by: null
source_type: verbatim
---

# 0025 — Integrity Guard for the ToolTempest Lock and Its Materialized File

## Status

Proposed (2026-10-20).

## Context & Constraints

`.tooltempest.lock` pins one ToolTempest file: a commit, a path
(`scripts/doc_sync.py`) and the SHA-256 of that file. The file itself is
deliberately untracked in this repository (owner decisions recorded in
`docs/BACKLOG.md` [B-019]): Radar does not distribute it, and nothing in
Radar executes it today.

Nothing compared the file's bytes with the lock. On 2026-09-18 the lock was
repinned to commit `0df1b05` and its `sha256` changed to the hash of that
commit's file, while the file on disk kept the bytes of the earlier pin
(`d35ff68`). The lock was honest; the file was not what the lock said. The
mismatch was found by hand on 2026-10-20. The existing pre-push check compares
the pinned commit with ToolTempest's `main`; that is a different property, and
its natural remedy (edit the lock) is exactly how the mismatch arose.

Three properties are easy to confuse:

| # | Property | Checked by |
|---|---|---|
| P1 | ToolTempest's manifest equals ToolTempest's own tree | ToolTempest's `check_manifest.py`, on ToolTempest only |
| P2 | The file's bytes in this working tree equal `lock.sha256` | this decision |
| P2′ | `lock.sha256` equals the upstream file's hash at `lock.commit` | not automated (see Consequences) |
| P3 | The pin is current relative to ToolTempest's `main` | the existing pre-push warning (advisory, unchanged) |

Constraints: pip-installable only, standard library, no network for ordinary
verification; Git does not clone hooks; the vendored file does not exist in a
fresh clone; commits go directly to `main`, there is no pull-request flow and
`test.yml` is non-blocking (ADR-0009) and runs after the push; the data-only
`vault` branch shares this repository's hooks and never contained the lock.

## Decision

1. Add `scripts/check_tooltempest_lock.py`, a stdlib checker for P2. It reads
   the lock from the working tree, the index (`--lock-source index`) or a
   commit (`--lock-source rev:<sha>`), validates every field and rejects
   unknown fields, and compares the SHA-256 of each covered file with the
   lock. Exit codes: 0 pass, 1 integrity violation (including a lock removed from
   the index, or from a revision whose history contained it), 2 error (fails
   closed; includes a missing lock file in worktree mode), 3 not applicable (the
   revision never had a lock).
2. Enforce it in two Git hooks whose sources are versioned in `scripts/hooks/`
   and installed by `scripts/install-hooks.sh`:
   - `pre-commit`: when `.tooltempest.lock` is staged, check the **staged**
     version of the lock.
   - `pre-push`: for each pushed ref, check the lock **as it exists in the
     pushed tip**.
3. Materialization contract (owner decision D1-a). The guard is activated
   explicitly, per clone. A clone that has not activated it behaves exactly as
   before. `install-hooks.sh` refuses to install (and changes nothing) unless
   the vendored file is present and matches the lock. Once installed, a
   missing or mismatching file blocks the commit/push, with a pointer to the
   procedure below. The file is not added to Git.
4. A tip without the lock is "not applicable" only when no commit in its
   history ever contained the lock (checked with
   `git log -1 --format=%H --full-history <tip> -- .tooltempest.lock`; without
   `--full-history`, Git's default simplification can skip a merged side branch
   that carried the lock). A lock that existed in history and
   is absent at the tip is a violation, not "not applicable". If `pre-push`
   cannot find the checker at all (for example when the main working copy is
   itself checked out on a data-only branch), it applies only this history test:
   a ref passes as "not applicable" when
   `git log -1 --format=%H --full-history <tip> -- .tooltempest.lock` succeeds and prints
   nothing; any other result, including a failing `git log`, blocks the push.

## Alternatives & Rationale

| Option | Verdict |
|---|---|
| A. Reuse an existing manifest mechanism (`check_manifest.py`, `MANIFEST.txt`, `sync-tooling.sh`) | Rejected. `check_manifest.py` verifies P1 on ToolTempest only and is unwired in article-pipeline and brain; `sync-tooling.sh` writes into `~/.claude`, is copied per repository and has already diverged between article-pipeline and brain. Brain's one lock-hash test is invoked by nothing and does not validate the lock. |
| B. Minimal lock-integrity guard (chosen) | Smallest solution that closes P2 for the one covered file. |
| C. No change | Rejected: a 32-day undetected mismatch is a demonstrated gap; "the file is not executed" does not make drift safe. |

Hook placement: a versioned source plus an explicit installer (chosen) over
editing the unversioned `.git/hooks` files (state outside the repository, the
same drift class) and over `core.hooksPath` (changes dispatch for every hook).

Materialization contract: activation-requires-materialization (chosen,
D1-a) over tolerating an absent file (silently loses the protection) and over
tracking the file (changes the owner's distribution decision; the only option
that would give a repository-side guarantee, left as a separate decision).

Lock removal: parent-commit and "ref name" signals were rejected because a
pushed range can delete the lock in a non-final commit, and the tip's parent
then also lacks it. History of the tip catches deletion anywhere in the range
and keeps the `vault` branch (328 commits, never contained the lock) not
applicable.

## Consequences

- Guarantee (P2): at commit time on this machine the lock version being
  committed, and at push time the lock version in each pushed tip, matches the
  bytes of the vendored file in this working tree.
- Not a guarantee: repository-side reproducibility. The file is not in the
  commit, so another clone, or CI, cannot verify it, and a clone that never
  activated the guard is unprotected. The lock plus the checker give any clone
  a verification procedure, not proof that anyone ran it. `git commit/push
  --no-verify`, a removed hook, or an unconfigured clone bypass it.
- P2′ remains a documented limitation (owner decision D4). It is exposed in
  practice by the procedure below: materializing from upstream and running the
  checker fails if `lock.sha256` is wrong. The residual case is a wrong hash
  plus a file adjusted by hand to match.
- Only the tip of each pushed ref is verified; locks of intermediate commits
  cannot be verified (their bytes do not exist on the machine). Pushing a ref
  whose lock differs from the one the local file was materialized for is
  blocked until the matching file is materialized.
- `pre-push` changes from always exiting 0 to blocking on this one offline
  invariant. The ToolTempest freshness warning is unchanged and still advisory.
- Deliberately removing the lock (leaving ToolTempest) is blocked and needs an
  explicit owner decision.
- The history test needs complete local history. In a shallow clone a lock that
  existed only beyond the shallow boundary is invisible, so a ref may read as
  "not applicable" there (reproduced with `git clone --depth 1`). The Radar
  checkout this guard was written in is not shallow (`git rev-parse
  --is-shallow-repository` prints false); failing closed on a shallow repository
  is left as a separate decision.
- The installer replaces two hooks one after the other; the pair is not
  atomic. It backs up the previous hooks without overwriting an earlier backup,
  rolls back on failure, and prints manual restore commands before it starts.
- Worktrees share hooks: a commit that changes the lock in a worktree where the
  file is not materialized is blocked. The `vault` branch is reported as not
  applicable and pushes normally.

## Materialization procedure

Run both blocks from the repository root. `TT` is a local clone of the
ToolTempest repository that contains the pinned commit (fetch it there first
if needed). The blocks take `commit`, `path` and `sha256` from the lock, check
the exit status of every step instead of trusting a pipe, and install nothing
unless the downloaded bytes match the lock. They are exercised by
`tests/test_lock_guard_hooks.py`, which extracts them from this file.

Materialize the vendored file (refuses to overwrite an existing file; move a
stale one aside first):

```sh materialize
set -eu
TT="${TT:?set TT to a local clone of the ToolTempest repository}"
read_lock() { python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' .tooltempest.lock "$1"; }
COMMIT="$(read_lock commit)"
REL="$(read_lock path)"
EXPECTED="$(read_lock sha256)"
if [ -e "$REL" ] || [ -L "$REL" ]; then
  echo "ERROR: $REL already exists; move it aside first (for example: mv $REL $REL.stale)" >&2
  exit 1
fi
tmp="$(mktemp "$(dirname "$REL")/.materialize.XXXXXX")"
trap 'rm -f "$tmp"' EXIT
git -C "$TT" show "$COMMIT:$REL" > "$tmp" || { echo "ERROR: git show $COMMIT:$REL failed in $TT; nothing installed" >&2; exit 1; }
out="$(shasum -a 256 "$tmp")"
actual="${out%% *}"
if [ "$actual" != "$EXPECTED" ]; then
  echo "ERROR: sha256 of $COMMIT:$REL is $actual but the lock expects $EXPECTED; nothing installed" >&2
  exit 1
fi
chmod 644 "$tmp"
mv "$tmp" "$REL"
echo "OK: materialized $REL from $COMMIT (sha256 $actual)"
```

Check the lock's hash against upstream (property P2′), for example before or
after repinning:

```sh verify-upstream
set -eu
TT="${TT:?set TT to a local clone of the ToolTempest repository}"
read_lock() { python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' .tooltempest.lock "$1"; }
COMMIT="$(read_lock commit)"
REL="$(read_lock path)"
EXPECTED="$(read_lock sha256)"
tmp="$(mktemp "${TMPDIR:-/tmp}/verify-upstream.XXXXXX")"
trap 'rm -f "$tmp"' EXIT
git -C "$TT" show "$COMMIT:$REL" > "$tmp" || { echo "ERROR: git show $COMMIT:$REL failed in $TT" >&2; exit 2; }
out="$(shasum -a 256 "$tmp")"
actual="${out%% *}"
if [ "$actual" = "$EXPECTED" ]; then
  echo "MATCH: $COMMIT:$REL sha256 $actual equals the lock"
else
  echo "MISMATCH: $COMMIT:$REL sha256 is $actual but the lock says $EXPECTED" >&2
  exit 1
fi
```

Activate the guard in a clone: materialize the file, then run
`bash scripts/install-hooks.sh`. To restore a previous hook, copy its
`<hook>.pre-lockguard-backup` over the hook (`cp -p`), or delete the hook to
return to Git's default behavior.

## Confirmation & Revisit

Verified by `tests/test_check_tooltempest_lock.py` (checker behavior, exit
codes, lock validation, index and revision modes), `tests/test_lock_guard_hooks.py`
(real Git hook dispatch in disposable repositories: fresh clone, index versus
working-tree lock, lock taken from the pushed commit, removed lock versus
the data-only branch, and the materialization blocks) and
`tests/test_install_hooks.py` (installer preflight, idempotence, backups,
rollback). The results of the run that preceded the implementation commit are
recorded in that commit's report, not in this record.

Revisit if: the vendored file becomes tracked (the checker can then read it
from the same commit as the lock and CI can enforce it); the lock schema covers
more than one file (the checker rejects unknown fields on purpose); a second
consumer needs the same guard (candidate for ToolTempest as an opt-in helper);
or automatic verification of P2′ is wanted.

**Source.** Radar session of 2026-10-20: B-019 investigation, read-only
comparison of ToolTempest, article-pipeline and brain, two architect reviews,
and owner decisions D1-a, D4 and the commit-trailer choice. No external AI
cross-check.
