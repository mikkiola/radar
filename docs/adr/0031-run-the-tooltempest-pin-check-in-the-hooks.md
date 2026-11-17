---
id: ADR-0031
status: Accepted
supersedes: ADR-0026
superseded_by: null
source_type: inferred
---

# 0031 — Run the ToolTempest Pin Check as the First Step of Radar's Hooks

## Status

Accepted by the Owner. The Owner decided on 2026-11-17 at 12:14 (Asia/Saigon) that the commit and push hooks of Radar, Brain and article-pipeline call `scripts/tt_pin_check.py` as their first step, with everything else in the hooks unchanged, and authorized this record, the hook edits and their installation on 2026-11-17 at 19:57 (Asia/Saigon). Supersedes ADR-0026 on one point: its Decision 2, which states what the versioned hooks run. ADR-0026 stays unedited, its `superseded_by` stays null and it stays Accepted (universal rule DR-6; the same point-level form as ADR-0029 and ADR-0030).

## Context & Constraints

Observations at commit `46fd622` of this repository unless a ToolTempest commit is named:

- The tracked hooks run the ADR-index check (`pre-commit` only), the lock guard and `docops.py`, and never call the pin check: `git grep -c -F tt_pin_check 46fd622 -- scripts/hooks` prints nothing and exits 1.
- Each hook looks for `docops.py` in its own working tree first and then in the main working tree: `git grep -n 'resolve_docops_checker()' 46fd622 -- scripts/hooks` prints one definition in each hook.
- The lock guard compares the materialized `docops.py` with the lock only when the lock is staged or pushed (ADR-0030, Context). Neither hook reads the install receipt: `git grep -c -i receipt 46fd622 -- scripts/hooks` prints nothing and exits 1.
- ToolTempest repository, ADR-0022, Decision 5: "A pinned executable runs only after the installed file set matches its install receipt and the pinned objects. There is no fallback to another worktree or clone." Its Consequences state that a consumer receives the hook change through the consumer's own repin and delivery decision. `git -C ~/.cache/tooltempest/repo show 66e0bc3407cf01ed124dc41a48cfd5910397bc98:scripts/tt_pin_check.py` shows the launch check that implements it; its docstring names a consumer hook as its caller and gives the exit codes 0 (passed or skipped), 1 (blocked) and 2 (usage or internal failure, which blocks as well).
- Git runs the same installed hooks in every worktree of the clone (ADR-0025, Consequences). The data-only `vault` worktree has no `scripts/` and never held the lock (ADR-0025, Context).

Constraint: the hook scripts make no network call (ADR-0026, Decision 4, unchanged). The pin check reads local Git objects only (its docstring: "nothing is fetched").

## Decision

This record replaces Decision 2 of ADR-0026. Everything else in ADR-0026 stays in force, except as ADR-0030 already supersedes.

1. **Order.** `scripts/tt_pin_check.py` is the first step of `pre-commit`, and the first step of `pre-push` after the hook reads its input once. No other step runs before it. `pre-commit` runs `tt_pin_check.py commit`; `pre-push` runs `tt_pin_check.py push` on the captured pre-push input. The lock guard (ADR-0025), the DocOps checker and every other step keep their content and their order relative to each other.
2. **Blocking.** Any non-zero exit of the pin check ends the hook with the same exit code, and no later step runs. A missing or non-zero DocOps checker still blocks, as in ADR-0026.
3. **No lock, no input.** A tree without `.tooltempest.lock` is skipped by the pin check itself with exit 0 and a message; this is the accepted behavior for the `vault` branch. A zero-byte pre-push input runs neither the pin check nor the DocOps checker, as ADR-0026 Decision 3 states.
4. **Lookup.** The hooks look for `tt_pin_check.py` in their own working tree only, with no fallback to another worktree or clone (ToolTempest repository, ADR-0022, Decision 5). If it is absent, the hook blocks when the index (`pre-commit`) or the history of a pushed ref (`pre-push`) holds `.tooltempest.lock`, and skips with a message otherwise. The lookup of `docops.py` stays as ADR-0026 Decision 2 states it: working tree first, then main working tree.

## Alternatives & Rationale

| Option | Verdict | Why |
|---|---|---|
| Keep ADR-0026 Decision 2 | Rejected | The hooks would keep running an installed `docops.py` that no check compared with the receipt and the pinned objects, which ToolTempest repository, ADR-0022, Decision 5 forbids for a pinned executable. |
| Replace the lock guard with the pin check | Rejected | ADR-0026 Consequences list the guard's behaviors that the shared mechanism lacks (reading the lock from the index and from a pushed revision, a not-applicable result, exit 1 versus 2). |
| Look up `tt_pin_check.py` in the main working tree as a fallback | Rejected | It would run a script from a clone that can be behind the lock, which is the incident ADR-0022 describes. |
| Run the pin check after the lock guard, immediately before `docops.py` | Rejected | The Owner decided on the first step. With a wrong pin the earlier steps would still run the tracked scripts of this tree, `scripts/generate_adr_index.py` and `scripts/check_tooltempest_lock.py`. |
| Run the pin check after `docops.py` | Rejected | The check exists to decide whether `docops.py` may run. |

## Consequences

- A clone whose installed core predates the pin, or lacks `scripts/tt_pin_check.py`, is blocked at the next commit and push of a tree that holds the lock, with the pin check's own message or the hook's. Operation: in such a clone, `git commit` ends with `commit blocked` and a non-zero status. A clone that never installed the hooks is unaffected (ADR-0025).
- Each commit and push runs `tooling.py verify` through the pin check. The added time is not measured.
- Enforcement stays local: `--no-verify`, a removed hook or an uninstalled hook bypasses it, and no workflow runs it (same limit as ADR-0026).
- The `docops.py` fallback to the main working tree is unchanged. For a tree that holds the lock the pin check has already proven the working-tree copy; for a tree without a lock, such as `vault`, the fallback stays unverified and ADR-0022 Decision 5 of ToolTempest does not gate that tree.
- Installing the changed hooks meets BACKLOG B-027: the installer refuses while an older `.pre-lockguard-backup` differs from the installed hook.

## Confirmation & Revisit

Confirmed by the commit that implements this decision, in a throwaway copy of the repository outside the working tree. Each case prints the hook's exit status; the results are in that commit's message.

- A wrong pin gives a non-zero exit and a blocked commit and push, and a `bash -x` trace of the hook shows no later step run; a correct pin continues to the later steps and to `docops.py`.
- An absent `scripts/tt_pin_check.py` blocks both hooks in a tree with a lock.
- A tree without the lock, and a zero-byte pre-push input, exit 0 with a message.

Revisit if ToolTempest changes the exit codes or arguments of `tt_pin_check.py`, if the shared mechanism takes over the lock guard (BACKLOG B-033), or if a workflow starts to run the DocOps check.

## Source

The Owner's decisions of 2026-11-17 at 12:14 and at 19:57 (Asia/Saigon), given in the Radar window that wired the pin check, after the repin to ToolTempest `66e0bc3`. The first draft of this record, committed earlier in the same task, placed the pin check after the lock guard; the Owner corrected the placement to the first step before any hook was changed or installed. Claude Code drafted the wording from repository evidence, so `source_type` is `inferred`. No external AI cross-check was made. This record checks nothing else on the Owner's behalf.
