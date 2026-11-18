---
id: ADR-0032
status: Accepted
supersedes: null
superseded_by: null
source_type: inferred
---

# 0032 — Scan the Commits of a Push for Secrets in Radar's pre-push Hook

## Status

Accepted by the Owner. The Owner ordered on 2026-11-18 that Radar's `pre-push` hook scans the content being pushed for secrets with Betterleaks, blocks on a finding, and blocks when the scanner is missing, and authorized the hook change, its installation and this record. This record adds one step to the hook. It changes no decision of ADR-0031 and supersedes no ADR.

## Context & Constraints

Observations at commit `f1ddea9` of this repository unless stated otherwise:

- The hooks run no secret scan: `git grep -n -i -E 'betterleaks|gitleaks|trufflehog' f1ddea9 -- scripts/hooks` prints nothing and exits 1.
- The CI job `security_secrets` scans after the fact. `grep -n -E '^on:|schedule|workflow_dispatch|pull_request|^  push' .github/workflows/security.yml` lists only `schedule` and `workflow_dispatch`, so a secret reaches the remote before the job can see it. The job runs `./betterleaks git . --no-banner` with v1.7.3, pinned by sha256 in that file.
- Betterleaks is the one scanner Radar permits (ADR-0010; the Compactness row of `docs/CONSTITUTION.md` names it as an exception to the pip-only rule).
- The hook scripts make no network call (ADR-0026, Decision 4). Betterleaks validates findings against live APIs only with `--validation` (`betterleaks git --help`).
- The local scanner differs from the CI one. `betterleaks version` printed `1.10.1` on 2026-11-18, and the CI job pins v1.7.3. The CI invocation, run with 1.10.1 in a scratch repository holding one synthetic token-shaped value, exited 1 and logged `leaks found: 1`; the same invocation over a clean range exited 0. It was not run with v1.7.3: not verified.
- `.github/actions/vault-write/action.yml` runs `git push origin vault` from a fresh checkout in a workflow. A fresh checkout holds no installed hook, so that push is not scanned (ADR-0031 Consequences: hooks protect only a clone that ran the installer).
- The `pre-push` hooks of `article-pipeline` and `brain` run `gitleaks detect --source . --no-git` on the working tree and only warn when `gitleaks` is missing (`grep -n -i -B2 -A6 gitleaks article-pipeline/scripts/hooks/pre-push brain/.githooks/pre-push`). This record does not change them.

## Decision

1. **Position.** `pre-push` runs the secret scan as its last step, after the pin check, the lock guard and the DocOps checker. The order of ADR-0031, Decision 1 is unchanged, and no existing step changes.
2. **Input.** The scan covers the commits that the push would publish, read from the pre-push input, and never the working tree. For an existing remote ref it scans the old tip to the new tip. For a new ref, or an old tip that this clone does not hold, it scans the commits that the remote's tracking refs do not reach. A ref deletion is not scanned. A push that updates nothing (zero bytes) is N/A.
3. **Scanner.** The hook runs `betterleaks git` with the default rules, as the CI job does. It adds the range, `--redact` and a JSON report, and it removes the scanner's configuration variables from the environment. It never passes `--validation`.
4. **Finding.** A finding blocks the push. The message names the rule, file, line and commit of each finding and never prints its value.
5. **Failure.** A missing scanner blocks the push, and the message gives the install command. Any scanner exit or report that cannot be read as "no findings" blocks it too. A zero exit with an empty report is read as no findings, which is how `betterleaks git` reports a clean range; a non-zero exit never is.
6. **Scope.** The step runs in every worktree, the data-only `vault` one included, because it needs nothing from `scripts/`.

## Alternatives & Rationale

| Option | Verdict | Why |
|---|---|---|
| Scan the working tree (`--no-git`), as `article-pipeline` and `brain` do | Rejected | A push publishes commits. A secret that an earlier pushed commit holds and the tip no longer holds would pass. |
| Warn and continue when the scanner is missing, as `article-pipeline` and `brain` do | Rejected | The Owner ordered a block. A silent pass leaves the push unscanned. |
| Use `gitleaks`, which is installed | Rejected | ADR-0010 chose Betterleaks and the Constitution permits no other scanner. |
| Run the CI job on `push` | Rejected | It runs after the push, and the secret has already reached the remote. The Owner scoped the CI workflow out. |
| Run the scan before the DocOps checker | Rejected | Every step blocks the push on its own, so the position adds no protection. The last position leaves every existing step where ADR-0031 Decision 1 put it. |

## Consequences

- A push needs `betterleaks` on the `PATH` of the process that runs Git. A client that starts Git with a short `PATH` is blocked with the install message.
- The hook runs the installed version, not v1.7.3. Detection can differ between the hook and the CI job until the installed version and the pin are brought together. The hook does not compare versions.
- For a new ref the exclusion uses the clone's remote-tracking refs. A commit that a stale tracking ref still reaches, and that the remote no longer holds, is not scanned.
- Enforcement stays local: `--no-verify`, a removed or uninstalled hook, and the workflow push of `vault` bypass it (same limit as ADR-0031).
- A new ref with no tracking ref in the clone is scanned from its whole history. With 1.10.1, the full history of the current branch took 1.78 s and the full history of `origin/vault` took 3.99 s (`/usr/bin/time -p betterleaks git . --no-banner --log-opts <ref>`, 2026-11-18, one run each).
- Installing the changed hook meets BACKLOG B-027: the installer refuses while an older `.pre-lockguard-backup` differs from the installed hook.

## Confirmation & Revisit

Confirmed by the commit that implements this decision. Its message holds the results of the hook tests that call `git push` in disposable repositories (`python3 -m pytest tests/test_lock_guard_hooks.py -k test_s`), and of a real push without `--no-verify` to a local bare remote, once clean and once with a synthetic token-shaped value built at run time.

Revisit if the CI pin or the installed version changes (compare their detection), if the `security_secrets` job starts to run on `push`, if `article-pipeline` or `brain` take over this behavior, or if Betterleaks changes the exit code or the JSON report of `betterleaks git`.

## Source

The Owner's order and its clarification of 2026-11-18, given in the Radar window that implemented the step. The Owner fixed the requirements: Betterleaks, a block on a finding, a block on a missing scanner, the commits of the pushed ranges, and the position after the pin check and the lock guard. Claude Code chose the detail under DR-10: the last position, the range forms, the JSON report and the removal of the configuration variables. No external AI cross-check was made. `source_type` is `inferred` because Claude Code drafted the wording from repository evidence.
