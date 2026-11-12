---
id: ADR-0030
status: Accepted
supersedes: ADR-0026
superseded_by: null
source_type: inferred
---

# 0030 — Retire the doc_sync Contour in Radar

## Status

Accepted by the Owner, 2026-11-12. Supersedes ADR-0026 on one point: what ADR-0026 Consequences state about the retired scripts and the checker's hash verification, which are the statements named in this record's Decision item 3. ADR-0026 stays unedited, its `superseded_by` stays null and it stays Accepted (universal rule DR-6; the same point-level form as ADR-0029).

## Context & Constraints

The doc_sync contour is the legacy ToolTempest DocOps path: `scripts/doc_sync.py` (Tier 1), `scripts/doc_sync_tier2.py` (Tier 2) and `schemas/execution-record.schema.json` (the execution-record schema). Radar never tracked any of them: they reached a clone only as untracked core files, and `.gitignore` listed the two scripts until commit `1c9d30d` (`git show 1c9d30d -- .gitignore`).

Observations, taken at commit `b73971c` of this repository unless a ToolTempest commit is named:

- No commit on any ref touches the three paths: `git log --all --oneline -- scripts/doc_sync.py scripts/doc_sync_tier2.py schemas/execution-record.schema.json | wc -l` prints 0.
- ToolTempest ADR-0019 defines how a path leaves an installed root, and states that a repin across a removal is an Owner decision. ToolTempest commit `00493dc` removed the three paths from its manifest. At ToolTempest `d2172e7` and `a55d6c0`, `git show <commit>:MANIFEST.txt | grep -c "doc_sync\|execution-record"` prints 0.
- Radar commit `1c9d30d` repinned across that removal: the lock moved from `scripts/doc_sync.py` to `scripts/docops.py`, and the two ignore entries for the scripts were dropped. `b73971c` pins `a55d6c0` (`git show b73971c:.tooltempest.lock`).
- The Owner's decision to repin Radar across the removal is not recorded in any file of this repository. It is not established from the repository.
- Nothing tracked here calls the contour: `git grep -n -i -I -E 'doc[_-]sync|execution[-_ ]record|tier[ _-]*[12]' b73971c -- . ':!docs'` prints one line, a docstring in `scripts/verify.py` that uses the word "doc-sync".
- The tracked hook sources `scripts/hooks/pre-commit` and `scripts/hooks/pre-push` run `docops.py check` (`--tree index`, `--push-stdin`). `git grep -n -i -E 'doc[_-]sync|docops' b73971c -- .github | wc -l` prints 0: no workflow runs a DocOps check.
- Hooks are installed per clone by `scripts/install-hooks.sh`; Git does not clone hooks (ADR-0026, Context). The check therefore binds only clones that installed them.
- ADR-0026 Consequences states that the hooks run the checker without a hash check, because the lock covers only `scripts/doc_sync.py`. At `b73971c` the lock declares `scripts/docops.py` with a sha256 (`git show b73971c:.tooltempest.lock`). `scripts/check_tooltempest_lock.py` compares that sha256 with the materialized file (`git grep -n -F 'hashlib.sha256(' b73971c -- scripts/check_tooltempest_lock.py`), and the hooks call it (`git grep -n check_tooltempest_lock b73971c -- scripts/hooks`): `pre-commit` when the lock is staged, `pre-push` for each pushed revision. The comparison runs then, not before every checker run.
- Backlog entry B-019 asks to wire `scripts/doc_sync.py` into hooks. The pinned manifest no longer installs that script.

## Decision

1. The doc_sync contour (`scripts/doc_sync.py`, `scripts/doc_sync_tier2.py`, the execution-record schema, Tier 2) is retired in Radar. The tracked repository keeps no copy, hook, workflow or check for it.
2. The DocOps check that Radar's hooks run is the ToolTempest checker `docops.py`, at the commit pinned in `.tooltempest.lock`. The lock declares that script and its sha256, which the lock guard compares with the materialized file when the lock is staged in a commit and for each pushed revision, not before every checker run. The check is local to clones that installed the hooks.
3. One point of ADR-0026, its Consequences about the retired scripts and the checker's hash verification, is superseded in three statements; the rest of ADR-0026, including its Decision, stays in force. The Consequences statement that no hook runs `scripts/tooling.py verify` is not among them and still holds:
   - the Consequences statement that the hooks execute the materialized checker without a hash check;
   - the Consequences statement that the lock covers only `scripts/doc_sync.py`;
   - the Consequences statement that `doc_sync.py` and `doc_sync_tier2.py` are installed with core but wired into nothing, and that hook wiring of the legacy helper remains open in the backlog.
4. Backlog entry B-019 is closed as obsolete: the script it wires is retired, and its purpose, the shared ToolTempest DocOps hooks, is met by item 2.

## Alternatives & Rationale

| Option | Verdict | Why |
|---|---|---|
| Wire `doc_sync.py` into the hooks, as B-019 asks | Rejected | The pinned manifest does not install it, and a lock that declares a removed path fails closed. |
| Keep B-019 open | Rejected | Its subject no longer exists in the pinned core; an open entry would keep naming a tool that cannot be wired. |
| Edit ADR-0026 in place | Rejected | These statements were true when written. Changing them is not a correction of the record (universal rule DR-4); DR-6 supersedes a point without an edit. |
| Mark ADR-0026 Superseded in full | Rejected | Its Decision (consume the core checker through the hooks) still holds; only statements about the retired scripts and the checker's hash verification changed. |
| Delete the leftover local copies in this change | Not done | Outside this record's scope; deletion is a per-clone action (see Consequences). |

## Consequences

- A clone that materialized core before the removal may still hold untracked copies of the retired files. ToolTempest does not delete or report them (ToolTempest ADR-0019). Nothing tracked here uses them; deleting them is not part of this decision.
- Historical text keeps its mentions: the bodies of ADR-0025 and ADR-0026, the original text of B-019, and the wording in `scripts/verify.py`. This record supersedes only the statements of Decision item 3.
- Enforcement is by local hooks only. A clone without installed hooks, or a commit made with `--no-verify`, is not checked, and no workflow compensates (ADR-0026 states the same limit).
- ADR-0026 Context and ADR-0025 also describe the lock as covering `scripts/doc_sync.py`. Each is a dated description of the state when it was accepted, not a decision about the scripts; this record does not supersede them.

## Confirmation & Revisit

Evidence is the output of the commands in Context & Constraints, taken at the commits named there. In the clone used for this change, `diff scripts/hooks/pre-push "$(git rev-parse --git-path hooks)/pre-push"` prints nothing. The same command for `pre-commit` prints only a header-comment difference (tracked lines 2 to 3 against installed lines 2 to 4); the executable lines are identical. This describes one local clone and goes stale. The checker at `a55d6c0` has the SHA-256 that the lock declares.

Revisit if a consumer needs a Tier 2 style snapshot-and-apply flow again, or if a workflow starts to run the DocOps check.

## Source

The Owner's reply of 2026-11-12 choosing to close B-019 and record the retirement in an ADR. Claude Code drafted the wording from repository evidence, so `source_type` is `inferred`. The Owner's earlier decision to repin across the removal is not recorded in the repository (see Context & Constraints). No external AI cross-check was made. The Owner accepted this record on 2026-11-12.
