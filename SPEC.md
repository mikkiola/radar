# SPEC A: Runtime Architecture Reorganization — Specification

## Overview

Radar's Python modules, tests, and `.gitlab-ci.yml` currently live in a
flat layout at the repo root, with imports working via `sys.path[0]`
(the directory of the invoked script). This spec moves to a
`src/` + `tests/` layout matching Python open-source community
expectations, with **zero change in pipeline behavior**: all 10 GitLab
CI jobs must behave identically before and after.

This is SPEC A of five independent specs decided with the owner on
2026-08-06 (see "Out of scope" section below for the full queue). Only
SPEC A is in scope for this session.

## Revision: `src/radar/` → `src/` (found during implementation, 2026-08-06)

The original interview settled on `src/radar/` + `tests/` (nested
package directory, matching the eventual-pip-install rationale). During
implementation, moving all files into `src/radar/` and running the real
`pytest` suite against it surfaced a contradiction not caught at
interview time: `src/radar/` is a **packaging convention** — it exists
so that `radar` becomes an importable package name. But this same SPEC
already decided CI invokes scripts by **direct path**
(`python3 src/analyze.py`, not `python3 -m radar.analyze`), with a
**minimal `pyproject.toml`** (no `[project]` table, no `[build-system]`,
no `pip install -e .`). There is no package use of the `radar/`
directory anywhere in this spec — only the naming convention was
adopted, none of the packaging it implies.

Running `pytest tests/` against `src/radar/` with
`pythonpath = ["src"]` (as originally specified) produced
`ModuleNotFoundError` on every test file: `pythonpath = ["src"]` puts
`src/` on `sys.path`, not `src/radar/`, so flat imports like
`import vault_write` (used consistently by every test file and every
internal script) cannot resolve — they'd need `import radar.vault_write`
instead, which none of the existing code uses and which nothing in this
spec proposed rewriting.

**Resolution**: drop the nested `radar/` directory. Final layout is
`src/` with all 18 `.py` files and `99_System/` directly inside it, no
intermediate package folder. `pythonpath = ["src"]` then puts `src/`
itself on `sys.path`, matching the flat `import vault_write` style
everywhere else in the codebase — the same behavior scripts already get
at runtime via `sys.path[0]` when invoked directly. No test file
content changed; this was a path-only correction, consistent with
every other "path-only, no logic change" decision in this spec.

All directory-tree references, the per-job table, and prose below are
already updated to `src/` (not `src/radar/`) to reflect this. The
pip-install rationale for adopting `src/` (rather than staying flat at
repo root) still holds — `src/<package>/` nesting can be added later,
at the point install is actually needed, without disturbing `tests/`.

## Goals

- [ ] Adopt `src/` + `tests/` layout (owner decision: src/ now,
      not flat — Radar may be pip-installed later; laying the
      structure down now avoids a second migration).
- [ ] Zero behavior change across all 10 CI jobs (Rule 31: verified by
      a real acceptance CI run, not by reading `.gitlab-ci.yml`).
- [ ] `vault_write.py` (9 internal dependents) migrated last, after
      all other modules are stable in `src/`.
- [ ] Remove the stray untracked `gitlab.com/` directory (empty,
      accidental `git clone` artifact — done in this session, see
      Decisions Log).

## Tech Stack

No new runtime dependencies. `pyproject.toml` added, minimal scope
only (`[tool.pytest.ini_options]`). `requirements-dev.txt` added,
pinning `pytest>=7` (needed for `pythonpath` support — CI does not
run pytest at all today, so this pin only protects local/future test
runs, not CI behavior).

## Verified Against Current Code (2026-08-06)

Facts below were re-verified against the actual repo state in this
session; several corrected a stale prior-session summary.

### Repo layout facts

- `radar/` at repo root: **not** an artifact. It is an intentional
  local checkout of the `vault` branch (already in `.gitignore`,
  separate git history, same remote). Left untouched.
- `gitlab.com/lyolich777ka/` at repo root: empty, untracked, no
  `.gitignore` entry. Confirmed accidental clone artifact. **Deleted
  in this session** (`rm -rf gitlab.com`).
- `99_System/model_config.json` exists at repo root (master branch;
  distinct from `vault` branch's own `99_System/`, which holds
  different files — `published_posts.log`, templates, etc.).

### Import graph (flat imports, `import X` not `from src import X`)

- `vault_write.py` — hub, imported by 9 files: `analyze.py`,
  `check_frontmatter.py`, `confirm_candidate.py`, `generate_graph.py`,
  `patterns.py`, `promote_candidates.py`, `recheck_lifecycle.py`,
  `telegram_post.py`, `update_assessments.py`. Depends on nothing
  internal itself.
- `scorecard.py` → used only by `filter.py`.
- `filter.py` → used only by `radar_step0.py`.
- `analyze.py` → used by `promote_candidates.py`, `recheck_lifecycle.py`.
- `vault_language.py` → used by `patterns.py`, `update_assessments.py`.
- `check_model_updates.py`, `fetch_analysts.py`, `generate_indexes.py`,
  `backfill_frontmatter.py` — not imported by anything, import nothing
  internal.
- All internal imports are flat and rely on `sys.path[0]` being the
  invoked script's own directory. **Direct-path invocation**
  (`python3 src/analyze.py`, decided below) preserves this with
  zero code changes, because Python still sets `sys.path[0]` to the
  script's directory regardless of where that directory sits in the
  tree.

### `99_System/model_config.json` — critical finding, not in original briefing

Six files resolve the config path relative to `__file__`, not cwd:

```python
MODEL_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "99_System", "model_config.json"
)
```

Affected: `analyze.py`, `check_model_updates.py`, `fetch_analysts.py`,
`patterns.py`, `telegram_post.py`, `update_assessments.py`.

If these 6 files move into `src/` while `99_System/` stays at
repo root, all six break on first CI run (`src/99_System/` does
not exist). **Decision: move `99_System/` into `src/99_System/`
alongside the code.** Zero logic change in the 6 files — same
principle as leaving VAULT_PATH untouched (see below): a pure path
move, not a logic change, keeps the two change types from being mixed
under a single acceptance run.

### CI job path-to-vault mechanisms — corrected from prior-session summary

Prior-session summary claimed "7 jobs use `VAULT_PATH=.../vault_repo/01_Assessments`".
**Actual count verified against `.gitlab-ci.yml`: 5 jobs**, not 7. Four
distinct mechanisms exist across the 10 jobs:

| Mechanism | Jobs |
|---|---|
| `VAULT_PATH=.../vault_repo/01_Assessments` | `radar`, `confirm_candidate`, `promote_candidates`, `recheck_lifecycle`, `publish` (5 jobs) |
| `VAULT_PATH=.../vault_repo` (whole vault) | `check_models`, `patterns` (2 jobs) |
| `--vault vault_repo` CLI flag (argparse default falls back to `VAULT_PATH`, but CI passes the flag explicitly, bypassing the env var) | `analysts` (1 job) |
| Positional CLI argument, no env var at all | `lint_vault` (1 job) |
| No vault-path concept — hardcoded `docs/...` relative paths | `pages` (1 job) |

**Decision: leave all four mechanisms as-is, only update the path
values that point at the moved script.** Unifying the mechanism
changes logic inside `.py` files, not just paths — mixing that with a
pure file move would make an acceptance-run failure impossible to
diagnose (which change caused it?). Unification is deferred to
**SPEC A.5** (see "Out of scope" below).

`check_frontmatter.py` invocation styles — confirmed as originally
briefed: **8 jobs** (`radar` — 2 calls, `confirm_candidate`,
`promote_candidates`, `recheck_lifecycle`, `publish`, `analysts`,
`check_models`, `patterns`) call it as `python3 ../check_frontmatter.py 01_Assessments`
after `cd vault_repo`. **1 job** (`lint_vault`) calls it directly as
`python3 check_frontmatter.py vault_repo/01_Assessments`, no `cd`.
**1 job** (`pages`) never calls it. Not unified in SPEC A — see
"check_frontmatter.py invocation" below for the path-only fix.

### `pages` job — confirmed unique

Only job with `GIT_STRATEGY: none` plus an explicit
`git clone --branch master ... .` (all 9 others rely on GitLab CI's
default checkout). `generate_indexes.py`/`generate_graph.py` resolve
`docs/...` paths relative to cwd, not `__file__` — cwd stays repo root
throughout the `pages` job script (no `cd` before invoking them), so
moving the two scripts into `src/` requires no logic change,
only updating the invocation path in `.gitlab-ci.yml`. `mkdocs.yml`'s
`docs_dir: docs` is also cwd-relative and unaffected.

### Tests — not run in CI today

`grep -n "test\|pytest" .gitlab-ci.yml` returns nothing. None of the
10 jobs execute `test_*.py` files. This means:
- The `pythonpath` vs `conftest.py` choice for test imports has zero
  effect on CI behavior either way (Rule 31's identical-behavior
  criterion is unaffected by this choice).
- Local pytest version (verified: `9.1.1`) exceeds `pythonpath`'s
  `>=7` requirement, but nothing in the repo pinned this before —
  `requirements-dev.txt` (new, this spec) fixes that gap for future
  contributors.
- Actually wiring pytest execution into CI is an explicit **new**
  behavior (adds a job), out of scope for SPEC A's zero-change
  criterion — deferred to **SPEC A.6**.

## Detailed Requirements

### 1. Target directory structure

```
src/
    analyze.py
    backfill_frontmatter.py
    check_frontmatter.py
    check_model_updates.py
    confirm_candidate.py
    fetch_analysts.py
    filter.py
    generate_graph.py
    generate_indexes.py
    patterns.py
    promote_candidates.py
    radar_step0.py
    recheck_lifecycle.py
    scorecard.py
    telegram_post.py
    update_assessments.py
    vault_language.py
    vault_write.py            # moved last
    99_System/
        model_config.json
tests/
    test_analyze_candidate.py
    test_check_frontmatter.py
    test_confirm_candidate.py
    test_patterns.py
    test_promote_candidates.py
    test_recheck_lifecycle.py
    test_update_assessments.py
    test_vault_write.py
pyproject.toml                # new, minimal
requirements-dev.txt          # new: pytest>=7
requirements_pages.txt        # unchanged, stays at root
.gitlab-ci.yml                # paths updated
docs/                         # unchanged, mkdocs source, stays at root
mkdocs.yml                    # unchanged, stays at root
SPEC.md, README.md, LICENSE   # unchanged, stay at root
```

No internal `import` statements change. No script logic changes,
except the `99_System` path move (a file-location change, not a
logic change — the `__file__`-relative code stays identical).

### 2. `pyproject.toml` — minimal scope

Decision: CI invokes scripts by direct path
(`python3 src/analyze.py`), not `python3 -m radar.analyze` and
not via `pip install -e .`. A full `[project]` metadata table would
therefore go unused and risks drifting from real dependencies. Only
add what's used today:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
```

No `[build-system]`, no `[project]` table. Revisit when/if the
package is actually pip-installed (not this spec).

### 3. `requirements-dev.txt` — new file

```
pytest>=7
```

Pinned because `pythonpath` in `[tool.pytest.ini_options]` requires
pytest >=7, and nothing in the repo pinned any version before this.
Not read by CI (CI doesn't run tests) — protects local/future
contributor test runs only.

### 4. `check_frontmatter.py` invocation — path-only fix, mechanism unchanged

The two calling styles (8 jobs via `cd vault_repo; python3 ../check_frontmatter.py 01_Assessments`,
1 job `lint_vault` via `python3 check_frontmatter.py vault_repo/01_Assessments`
with no `cd`) are **not unified** in SPEC A — only the script path
changes in both styles:

- 8-job style: `python3 ../check_frontmatter.py 01_Assessments` →
  `python3 ../src/check_frontmatter.py 01_Assessments`
  (still relative to `vault_repo/` after `cd`).
- `lint_vault` style: `python3 check_frontmatter.py vault_repo/01_Assessments` →
  `python3 src/check_frontmatter.py vault_repo/01_Assessments`.

### 5. `.gitlab-ci.yml` — per-job script path updates

Every `python3 <script>.py` invocation across all 10 jobs gets
`src/` prepended to `<script>.py`. `VAULT_PATH`,
`PATTERNS_PATH`, `PUBLISHED_LOG` env var *values* are untouched (they
point at `vault_repo/...`, not at the code location). The `--vault`
CLI flag value in the `analysts` job is untouched for the same
reason. Full per-job diff:

| Job | Script invocation changes |
|---|---|
| `radar` | `analyze.py` → `src/analyze.py`; `update_assessments.py` → `src/update_assessments.py`; both `check_frontmatter.py` calls get `src/` per rule above |
| `confirm_candidate` | `confirm_candidate.py` → `src/confirm_candidate.py`; `check_frontmatter.py` call updated |
| `promote_candidates` | `promote_candidates.py` → `src/promote_candidates.py`; `check_frontmatter.py` call updated |
| `recheck_lifecycle` | `recheck_lifecycle.py` → `src/recheck_lifecycle.py`; `check_frontmatter.py` call updated |
| `publish` | `telegram_post.py` → `src/telegram_post.py`; `check_frontmatter.py` call updated |
| `analysts` | `fetch_analysts.py --vault vault_repo` → `src/fetch_analysts.py --vault vault_repo`; `check_frontmatter.py` call updated |
| `lint_vault` | `check_frontmatter.py vault_repo/01_Assessments` → `src/check_frontmatter.py vault_repo/01_Assessments` (no `cd`, no other changes) |
| `check_models` | `check_model_updates.py` → `src/check_model_updates.py`; `check_frontmatter.py` call updated |
| `patterns` | `patterns.py` → `src/patterns.py`; `check_frontmatter.py` call updated |
| `pages` | `generate_indexes.py` → `src/generate_indexes.py`; `generate_graph.py` → `src/generate_graph.py`; `git clone --branch master` step unchanged (clones the new layout wholesale); `requirements_pages.txt` install unchanged (stays at root); `mkdocs build` unchanged |

`pip install ...` lines in every job are **unchanged** (inline,
per-job — consolidating into a shared `requirements.txt` was
explicitly decided out of scope for SPEC A; see Decisions Log).

### 6. Migration order and branch strategy

Owner decision: migration happens on a **separate branch**, merged to
`master` in one merge only after a passing acceptance CI run (Rule
31). Reason: `radar`, `confirm_candidate`, `promote_candidates`,
`recheck_lifecycle`, `publish`, `analysts`, `check_models`, `patterns`
all trigger on `schedule`/`web`, not on push — an in-progress
migration state on `master` risks a live scheduled run hitting broken
paths mid-migration (e.g. `recheck_lifecycle` runs monthly; a
misaligned schedule during a multi-day migration window would break a
production run). `pages` is the only job triggered by push, and only
on `master`/`vault` — safe, since it isn't triggered on a feature
branch.

Within the branch, file migration order:

1. Move `check_model_updates.py`, `fetch_analysts.py`,
   `generate_indexes.py`, `backfill_frontmatter.py` first — no
   internal dependents, no internal dependencies, zero-risk moves.
2. Move `scorecard.py`, `vault_language.py`, then `filter.py`,
   `analyze.py` — leaf-to-hub order along the dependency graph.
3. Move `radar_step0.py`, `check_frontmatter.py`, `generate_graph.py`,
   `confirm_candidate.py`, `promote_candidates.py`,
   `recheck_lifecycle.py`, `telegram_post.py`, `patterns.py`,
   `update_assessments.py` — all files that depend on `vault_write.py`
   but not vice versa, moved while `vault_write.py` still sits at the
   old root location (its 9 dependents keep working via `sys.path[0]`
   regardless of where `vault_write.py` itself lives, since Python
   resolves `import vault_write` by searching `sys.path`, and the
   *importing* script's own directory is what's added to
   `sys.path[0]` — this only works if `vault_write.py` is *also*
   findable, so in practice this step requires `vault_write.py` to
   already be reachable; see note below).
4. Move `vault_write.py` (+`99_System/`) last, once every module that
   imports it has already been updated to invoke from
   `src/` — at that point `vault_write.py` moving into the same
   directory is the final, most isolated step, testable on its own
   before the branch merge.

   **Note on step 3/4 ordering**: because `sys.path[0]` is set to the
   *invoked* script's own directory, a script in `src/` doing
   `import vault_write` requires `vault_write.py` to be in that same
   directory — it cannot resolve to a `vault_write.py` still sitting
   at repo root. This means steps 3 and 4 cannot be split across
   separate merged states without breaking imports in between. Within
   the single migration branch this is fine (intermediate commits on
   the branch are never merged or CI-triggered individually) — the
   ordering above is a within-branch commit sequence for isolating
   *review* risk, not a claim that `master` passes through each
   intermediate state.
5. Move all `test_*.py` files into `tests/`, add `pyproject.toml` and
   `requirements-dev.txt`.
6. Update all `.gitlab-ci.yml` paths per the table in section 5, in
   the same branch.
7. Run Rule 31 acceptance: trigger each of the 10 jobs' `web`-source
   rule paths manually (existing `PROMOTE_ONLY`, `LIFECYCLE_ONLY`,
   `CONFIRM_REPO`, `PUBLISH_ONLY`, `PATTERN_MODE=weekly`, `GRAPH_ONLY`
   variables already gate each job — no new CI variables needed to
   exercise all 10 paths from the web UI).
8. Merge to `master` only after all 10 jobs pass on the branch.

## Non-Functional Requirements

1. Zero behavior change — byte-for-byte same vault writes, same
   Telegram output, same `check_frontmatter.py` pass/fail outcomes,
   for identical input state, before and after migration.
2. No new runtime dependencies added to any CI job's `pip install`
   line.
3. `python3 -m py_compile` on every moved `.py` file before each
   commit (Rule 4).

## Security Considerations

None specific to this spec — no secrets, tokens, or credentials move
or change scope. `GITLAB_PUSH_TOKEN`/`CI_JOB_TOKEN` usage in
`.gitlab-ci.yml` is untouched.

Flagged for later: SPEC E (security scanning — see "Out of scope"
below) covers secret-scanning and dependency-CVE checks; explicitly
not part of SPEC A.

## Test Plan

1. **Local**: after each migration step, run
   `python3 -m py_compile` on touched files, and run the existing
   `test_*.py` suite locally (`pytest` with `pythonpath = ["src"]`)
   to catch import breakage before pushing.
2. **Rule 31 acceptance run** (required before merge, not optional):
   trigger a `web`-source pipeline on the migration branch and
   exercise every one of the 10 jobs via their existing gating
   variables (see step 7 above). Confirm:
   - `radar` job: analyze + update_assessments run without error,
     vault diff matches a pre-migration dry run on the same input.
   - `confirm_candidate`, `promote_candidates`, `recheck_lifecycle`,
     `publish`: each completes and pushes (or correctly no-ops) as
     before.
   - `analysts`, `check_models`, `patterns`: complete under
     `PATTERN_MODE=weekly`.
   - `lint_vault`: still catches a deliberately malformed frontmatter
     test fixture (verify the failure path, not just success).
   - `pages`: `mkdocs build` succeeds, `public/` artifact contains
     the same pages as a pre-migration build.
3. Record the acceptance run's pipeline URL and outcome in this file
   under a new "Acceptance Run Result" subsection before closing
   SPEC A (same pattern as the prior `recheck_lifecycle` spec's §13).

### Acceptance Run Result (2026-08-06, branch `spec-a-runtime-architecture`)

8 of 10 jobs triggered via `web` source with gating variables set
per-job; 7 came back green: `lint_vault`, `promote_candidates`,
`recheck_lifecycle`, `publish`, `analysts`, `check_models`, `patterns`.

- `radar` — correctly did **not** run. Suppressed by the
  `$PUBLISH_ONLY != "true" && $PATTERN_MODE != "weekly" && $LIFECYCLE_ONLY != "true"`
  guard on its `web` rule (see the rules-block verification done before
  the trigger) — the run intentionally set one of those three
  variables to gate other jobs one at a time, which correctly kept
  `radar` from firing alongside them. Not run standalone in this
  acceptance pass; not a gap, this was the expected behavior of the
  guard being exercised.
- `confirm_candidate` — intentionally not run. Owner decision: it
  mutates real assessment data on approve/reject, and no
  `CONFIRM_REPO`/`CONFIRM_DECISION` were supplied, which the rules
  verification confirmed means it structurally cannot fire (bare
  `$CONFIRM_REPO` truthiness check is false when the variable is
  entirely absent).
- **`pages` — failed**:
  `python3: can't open file '/builds/lyolich777ka/radar/src/generate_indexes.py': [Errno 2] No such file or directory`.
  Root cause confirmed from the log, **not a migration bug**: `pages`
  is the one job (see "Verified Against Current Code" above) with an
  explicit `git clone --branch master ...` instead of the default
  pipeline checkout — it always clones `master` regardless of which
  branch the pipeline itself runs on. `master` does not yet have this
  migration merged, so `src/generate_indexes.py` genuinely does not
  exist there. This is a **structural limitation of `pages`**: it can
  never be exercised on a feature branch under the current
  architecture, migration-related or not.

  **Owner-confirmed decision**: do not work around this with a
  temporary `.gitlab-ci.yml` change before merge (branch to point
  `pages`'s clone at the feature branch, test, then revert) — the cost
  (extra commits solely to test, a revert before merge) outweighs the
  benefit, given `pages` uses the same new path structure that all 7
  passing jobs already exercised successfully.

**SPEC A is NOT considered closed until `pages` is separately verified
green after the merge to `master`**, triggered via `web` source with
`GRAPH_ONLY=true` (see rules block: `$CI_PIPELINE_SOURCE == "web" && $GRAPH_ONLY == "true"`).
This is a mandatory closing step, not an optional follow-up — the
9-of-10 result above is sufficient to consider the branch merge-ready,
but not sufficient to consider SPEC A itself done.

### Related but out-of-scope finding: `filter.py` `AttributeError` (2026-08-06)

The post-merge `pages` verification run surfaced a second, unrelated
production bug via `radar`'s real execution: `src/filter.py:38` crashed
with `AttributeError: 'NoneType' object has no attribute 'lower'`.
`project.get("description", "").lower()` only substitutes the default
when the `description` key is *absent* — the GitHub API returns
`description: null` (not a missing key) for repositories with no
description, so `.get()` returned `None`, not `""`, and `.lower()`
crashed on it.

**This is not a SPEC A architecture bug.** The traceback path
(`/builds/lyolich777ka/radar/src/filter.py`) confirms the opposite: the
new `src/` layout resolved correctly — this is a pre-existing logic bug
that real GitHub API data happened to trigger during this acceptance
run, unrelated to the file reorganization. It surfaced here only
because this was the first real (non-mocked) `radar` execution against
live GitHub data since the migration.

Fixed in a standalone commit directly to `master` (not on the SPEC A
branch, not part of the migration diff), following the same
verify-before-fixing process as the rest of this spec (Rule 28/31):
`project.get(x) or default` instead of `project.get(x, default)`,
applied to all three same-pattern fields in `is_relevant()` —
`description` (confirmed crash), `title` (same pattern, plausible
`None` from the HN Algolia API), and `topics` (same pattern, would
raise `TypeError` instead of `AttributeError` if ever `None`). Verified
with a targeted reproduction of the exact crash (`None`
description/topics/title) plus the full `pytest` suite (99 passed) before
commit. See commit `2908007` on `master`.

## Milestones

1. [x] Create migration branch (`spec-a-runtime-architecture`).
2. [x] Move zero-dependent/zero-dependency files (step 1).
3. [x] Move leaf-to-hub files (step 2).
4. [x] Move remaining `vault_write.py`-dependent files (step 3).
5. [x] Move `vault_write.py` + `99_System/` (step 4).
6. [x] Move tests, add `pyproject.toml` + `requirements-dev.txt` (step 5).
7. [x] Update `.gitlab-ci.yml` (step 6).
8. [x] Rule 31 acceptance run, 8 of 10 jobs triggered (step 7) — 7
   green, `radar` correctly suppressed by its own guard,
   `confirm_candidate` intentionally skipped (mutates real data).
   `pages` failed for a structural reason unrelated to the migration
   (see Acceptance Run Result above).
9. [x] Merge to `master` (step 8) — via GitLab MR, owner-confirmed,
   merge commit `c5816e7`.
10. [x] **Mandatory, separate from step 9**: `pages` verified green via
    a `web`-source trigger with `GRAPH_ONLY=true`, after the merge —
    pipeline `#2737567158` on `master`, **Passed**, 4/4 jobs green
    (`lint_vault`, `radar`, `pages`, `pages:deploy`). `radar` also ran
    for real in this pipeline (not gated) and passed, which additionally
    validated the `filter.py` fix (see below) against live GitHub data,
    not just the local smoke test.

## SPEC A: CLOSED (2026-08-06)

All 10 CI jobs are now confirmed on `master` with the `src/` + `tests/`
layout: 9 via the pre-merge acceptance run on
`spec-a-runtime-architecture` (`lint_vault`, `promote_candidates`,
`recheck_lifecycle`, `publish`, `analysts`, `check_models`, `patterns`
green; `radar` correctly self-suppressed by its guard;
`confirm_candidate` intentionally not exercised — mutates real data,
structurally cannot fire without `CONFIRM_REPO`), plus `pages`
confirmed separately after merge (pipeline `#2737567158`, together with
`radar` running for real and passing). Zero-behavior-change criterion
met for all 10 jobs. `pages:deploy` (GitLab Pages' own deploy step,
downstream of the `pages` job's artifact) also came back green,
confirming the built site itself was accepted.

Everything under "Out of Scope for SPEC A" below remains genuinely out
of scope — SPEC A.5, SPEC A.6, SPEC E, SPEC C, SPEC B, SPEC D are
separate future sessions, not started here.

## Decisions Log (from interview, 2026-08-06)

- src/ layout adopted now, not flat — owner: Radar may be
  pip-installed later, avoid a second migration.
- `src/radar/` (nested package directory) revised to flat `src/`
  during implementation (2026-08-06) — see "Revision" section above.
  Found via a real `pytest` run, not caught at interview time: the
  nested folder was a packaging convention with no packaging behind
  it (no `[project]` table, no `-m radar.module` invocation), and it
  broke every test file's flat `import vault_write`-style imports.
- `gitlab.com/lyolich777ka/` stray empty directory deleted this
  session (`rm -rf gitlab.com`), confirmed harmless accidental clone
  artifact, not tracked by git.
- `vault_write.py` migrates last, in isolation, once its 9 dependents
  are already stable.
- Test imports: `pythonpath = ["src"]` in
  `[tool.pytest.ini_options]`, confirmed safe after checking local
  pytest version (9.1.1, exceeds the `>=7` requirement) and confirming
  CI does not run pytest at all today (so the choice has zero CI-behavior
  risk either way).
- `requirements-dev.txt` pinning `pytest>=7` — created now, in SPEC A
  (not deferred), specifically so the `pythonpath` choice is backed by
  a real repository pin, not just informal reliance on the local
  machine's installed version.
- `99_System/` moves into `src/99_System/` alongside the code —
  matches the "path-only change, no logic change" principle applied
  everywhere else in this spec, because 6 files resolve
  `model_config.json` via `__file__`-relative paths.
- VAULT_PATH's four different path-resolution mechanisms across the
  10 jobs are **not unified** in SPEC A — only path values change.
  Reason: unifying would mix a logic change with a pure file-move,
  making a Rule 31 acceptance failure impossible to attribute to one
  cause. Deferred to SPEC A.5.
- `pip install` consolidation into a shared `requirements.txt` — not
  done in SPEC A, same reasoning as VAULT_PATH (avoid mixing change
  types). Left as a candidate for a future session.
- `pyproject.toml` kept minimal — only `[tool.pytest.ini_options]` —
  because CI invokes scripts by direct path, not by installing the
  package; a full `[project]` table would go unused and risk drifting
  from reality.
- Migration happens on a separate branch, merged to `master` in one
  merge only after a passing Rule 31 acceptance run — because most CI
  jobs trigger on `schedule`/`web`, not on push, so a broken
  intermediate state on `master` risks a live scheduled run hitting it
  mid-migration.

## Out of Scope for SPEC A — Planned Separately

Not touched in this session. Recorded here so the full picture is not
lost between sessions.

- **SPEC A.5 — VAULT_PATH mechanism unification.** The 4 different
  path-resolution mechanisms found in this spec's verification
  (`VAULT_PATH` on `01_Assessments`, `VAULT_PATH` on the whole vault,
  `--vault` CLI flag, positional argument) get unified into one
  mechanism. Immediately after SPEC A's acceptance run closes.
- **SPEC A.6 — pytest execution wired into CI.** Actually running the
  test suite as a new CI job (a genuine new behavior, not a pure
  reorg — explicitly excluded from SPEC A's zero-change criterion).
  After SPEC A.5.
- **SPEC E — Security scanning.** Found 2026-08-06 on owner
  initiative, not in the original SPEC A/B/C/D briefing. Three
  components: Gitleaks (secret scanning CI job, blocks commits/PRs
  with detected secrets), `pip-audit` or `safety` (known-CVE check
  against the future `requirements-dev.txt` from SPEC A.6), TruffleHog
  (one-time full git-history scan before GitHub mirroring — secrets
  committed in the past, before current project practices). Ordered
  before SPEC C specifically so history is checked before the repo
  becomes visible on GitHub. After SPEC A.6.
- **SPEC C — GitHub mirroring.** GitLab stays source of truth.
  Requires the owner to check push-mirroring availability via GitLab
  web UI (Settings → Repository → Mirroring repositories) first — not
  yet done. After SPEC E.
- **SPEC B — Repository discoverability.** README (English), badges,
  topics, description, license confirmation, social preview, releases.
  References SPEC A's final paths, so depends on SPEC A being closed,
  but is otherwise independent in content. After SPEC C.
- **SPEC D — Architecture documentation.** Documents Radar's 5-layer
  architecture (Layer 0 Sources → Layer 1 Signals → Layer 2
  Assessment+CoVe → Layer 3 Patterns → Layer 4 Meta) as a generic
  reusable "detecting-and-verifying-signals-from-noise" pattern, with
  Radar as one concrete implementation. Explicitly decided: code is
  **not** abstracted into a configurable domain (same class of
  decision already rejected for llm-tldr/Article Engine) — only
  documentation changes. Last in the queue.

**Full queue order**: SPEC A → SPEC A.5 → SPEC A.6 → SPEC E → SPEC C
→ SPEC B → SPEC D. **SPEC A.5 and SPEC A.6 both closed 2026-08-07 (see
below) — SPEC E is next.**

## Open Questions / Decisions Needed

None remaining for SPEC A's design. Implementation-time open item:
verify no other file (outside the grepped `*.py` set) references the
old flat paths — e.g. check `.gitignore` patterns, any shell scripts,
or CI cache keys that assume repo-root-level `.py` files, before
starting the migration branch.

---

# SPEC A.5: VAULT_PATH Mechanism Unification — Specification

## Overview

SPEC A moved all `.py` files into `src/` without touching *how* each
script resolves the vault's filesystem path — that was deliberately
deferred (see "Out of scope" above) to keep the two risk classes
(file-move vs. logic-change) separable under Rule 31 acceptance. This
spec does the deferred logic change: collapses 4 different
path-resolution mechanisms into one.

## Verified Inventory (2026-08-07, grepped against real code — not the
original task brief, which undercounted the affected jobs)

4 mechanisms confirmed in the code:

1. `VAULT_PATH` env var pointing directly at `01_Assessments/`
2. `VAULT_PATH` env var pointing at the vault root
3. `--vault` CLI flag pointing at the vault root
4. positional CLI argument (`check_frontmatter.py` only)

The original task brief said "5 jobs" — the real count of jobs whose
**primary** script resolves the vault path via one of these mechanisms
is **8**: `radar`, `confirm_candidate`, `promote_candidates`,
`recheck_lifecycle`, `publish` (mechanism 1), `analysts` (mechanism 3),
`check_models`, `patterns` (mechanism 2). `lint_vault` is a 9th job
using mechanism 4 as its sole script. `pages` uses no VAULT_PATH
mechanism at all — hardcoded `cp -r` in `.gitlab-ci.yml`. "5" appears to
be the count for mechanism 1 alone.

**Correction found during Rule 28 line-by-line verification (2026-08-07,
this session)**: a **10th file**, `src/backfill_frontmatter.py`, also
uses mechanism 1 (`VAULT_PATH` env var, absolute leaf default
`~/radar/radar/01_Assessments`, line 10) and was missing from the
original inventory above and from the Per-File Change Plan. It is not
invoked by any `.gitlab-ci.yml` job (confirmed by grep) — it is a
one-off manual migration script ("Одноразовая миграция
01_Assessments/ на YAML frontmatter, Вариант A, backfill"), run by hand,
not by CI, matching SPEC A's own prior classification of it as "not
imported by anything, import nothing internal." **Owner decision:
include it as the 10th migrated file**, for full mechanism consistency
across the repo even where CI never exercises it — see its Per-File
Change Plan entry below.

Mechanism 1 additionally has two different fallback-default patterns:
absolute (`~/radar/radar/01_Assessments`, in `analyze.py` /
`update_assessments.py` / `telegram_post.py`) and relative
(`"01_Assessments"`, in `confirm_candidate.py` / `promote_candidates.py`
/ `recheck_lifecycle.py`). Never triggered in CI (the var is always set
explicitly there) but relevant to local dev.

## Decisions (from interview, 2026-08-07)

- **Chosen mechanism**: single env var, always pointing at the vault
  **root**. Every script derives its own subdirectory path(s) via
  `os.path.join(...)` — matches the pattern `patterns.py` and
  `check_model_updates.py` already use today. Chosen over "always point
  at `01_Assessments`" because that pattern breaks down for scripts
  needing multiple subdirectories (`patterns.py` needs 4); chosen over
  "CLI flag everywhere" because it would require adding `argparse` to 6
  scripts that currently just read `os.environ` directly, for no
  behavioral gain.
- **Renamed to `VAULT_ROOT`** (not kept as `VAULT_PATH`). Semantics
  change for 6 of 8 scripts (root instead of leaf) — a same-name env var
  with silently different meaning is a bug risk if anyone (including a
  future Claude session working from memory) sets it the old way.
  Renaming makes the old usage fail loudly (`KeyError`/empty path)
  instead of silently pointing at the wrong directory.
- **Fallback default**: single absolute value everywhere —
  `os.path.expanduser("~/radar/radar")` — replacing both prior
  patterns. Never exercised in CI (var always set explicitly there);
  only affects local runs without `VAULT_ROOT` set.
- **Derived subdirectory constants named `ASSESSMENTS_PATH`** (not a
  per-script bespoke name) — follows the existing precedent in
  `patterns.py`, which `tests/test_patterns.py` already monkeypatches by
  that name.
- **`PATTERNS_PATH` (currently a separate env var in `analyze.py`) and
  `PUBLISHED_LOG` (currently a separate env var in `telegram_post.py`)
  are folded into `VAULT_ROOT`-derived constants**, dropping their
  standalone env-var overrides. One override variable for the whole
  pipeline, not per-script secondary overrides.
- **`fetch_analysts.py`'s `--vault` CLI flag is removed.** It becomes a
  plain `os.environ.get("VAULT_ROOT", ...)` read like every other
  script. `import argparse` is removed from the file entirely — the
  `--vault` flag was its only use.
- **`check_frontmatter.py` (mechanism 4, positional argument) is
  explicitly out of scope** — not silently excluded. It's a different
  contract (accepts a path as a CLI argument, not an env var) already
  consistent across all 8 call sites, and it's a lint utility, not part
  of the vault-path-resolution problem the task describes.
- **`pages` job is explicitly out of scope** — no VAULT_PATH mechanism
  exists there today; this spec unifies path *resolution*, not
  introduces one where none existed.
- **Test files are in scope, in the same MR**: renaming the derived
  constant breaks `monkeypatch.setattr(module, "VAULT_PATH", ...)` calls
  in 4 test files. Fixing production code without fixing tests in the
  same change would leave `pytest` broken on the branch.
- **Migration branch**: separate branch + MR, merged to `master` only
  after a green acceptance run — same reasoning as SPEC A. Most affected
  jobs trigger on `schedule`, so a broken intermediate state on `master`
  risks a live scheduled run mid-migration.
- **Acceptance scope**: all 8 primary jobs triggered for real via GitLab
  web trigger on the migration branch. `confirm_candidate` is the one
  exception — dry run only (code read + local `pytest`), unless a real
  `CANDIDATE` file happens to exist in the vault at merge time, since it
  requires a real `$CONFIRM_REPO` HITL target and the others make live
  Anthropic API calls that cost money and don't need duplicating for
  this one job's sake.

## Per-File Change Plan

### `src/analyze.py`
```python
# before
VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar/01_Assessments"))
PATTERNS_PATH = os.environ.get("PATTERNS_PATH", os.path.expanduser("~/radar/radar/02_Patterns"))

# after
VAULT_ROOT = os.environ.get("VAULT_ROOT", os.path.expanduser("~/radar/radar"))
ASSESSMENTS_PATH = os.path.join(VAULT_ROOT, "01_Assessments")
PATTERNS_PATH = os.path.join(VAULT_ROOT, "02_Patterns")
```
All other `VAULT_PATH` references in the file (lines 238, 245, 247, 254,
256, 469, 509) → `ASSESSMENTS_PATH`.

### `src/update_assessments.py`
```python
# before
VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar/01_Assessments"))

# after
VAULT_ROOT = os.environ.get("VAULT_ROOT", os.path.expanduser("~/radar/radar"))
ASSESSMENTS_PATH = os.path.join(VAULT_ROOT, "01_Assessments")
```
All other `VAULT_PATH` references (lines 52, 53, 56, 68) → `ASSESSMENTS_PATH`.

### `src/confirm_candidate.py`
```python
# before
VAULT_PATH = os.environ.get("VAULT_PATH", "01_Assessments")

# after
VAULT_ROOT = os.environ.get("VAULT_ROOT", os.path.expanduser("~/radar/radar"))
ASSESSMENTS_PATH = os.path.join(VAULT_ROOT, "01_Assessments")
```
Line 20 (`os.path.join(VAULT_PATH, repo + ".md")`) → `ASSESSMENTS_PATH`.

### `src/promote_candidates.py`
```python
# before
VAULT_PATH = os.environ.get("VAULT_PATH", "01_Assessments")

# after
VAULT_ROOT = os.environ.get("VAULT_ROOT", os.path.expanduser("~/radar/radar"))
ASSESSMENTS_PATH = os.path.join(VAULT_ROOT, "01_Assessments")
```
Lines 13, 15, 18 → `ASSESSMENTS_PATH`.

### `src/recheck_lifecycle.py`
```python
# before
VAULT_PATH = os.environ.get("VAULT_PATH", "01_Assessments")

# after
VAULT_ROOT = os.environ.get("VAULT_ROOT", os.path.expanduser("~/radar/radar"))
ASSESSMENTS_PATH = os.path.join(VAULT_ROOT, "01_Assessments")
```
Lines 14, 16, 19 → `ASSESSMENTS_PATH`.

### `src/telegram_post.py`
```python
# before
VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar/01_Assessments"))
PUBLISHED_LOG = os.environ.get("PUBLISHED_LOG", os.path.expanduser("~/radar/radar/99_System/published_posts.log"))

# after
VAULT_ROOT = os.environ.get("VAULT_ROOT", os.path.expanduser("~/radar/radar"))
ASSESSMENTS_PATH = os.path.join(VAULT_ROOT, "01_Assessments")
PUBLISHED_LOG = os.path.join(VAULT_ROOT, "99_System", "published_posts.log")
```
All other `VAULT_PATH` references (lines 30, 33, 67, 205) → `ASSESSMENTS_PATH`.
`PUBLISHED_LOG` loses its standalone env-var override — always derived.

### `src/fetch_analysts.py`
```python
# before
import argparse
...
def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--vault",
        default=os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar")),
    )
    args = arg_parser.parse_args()
    vault_path = args.vault
    analysts_path = os.path.join(vault_path, "04_Analysts")

# after
# (import argparse removed entirely — no other use in the file)
...
def main():
    vault_root = os.environ.get("VAULT_ROOT", os.path.expanduser("~/radar/radar"))
    analysts_path = os.path.join(vault_root, "04_Analysts")
```
`print(f"[fetch_analysts] vault: {vault_path}")` → `{vault_root}`.

### `src/check_model_updates.py`
```python
# before
VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar"))
FEEDBACK_DIR = os.path.join(VAULT_PATH, "98_Feedback", "Infrastructure")

# after
VAULT_ROOT = os.environ.get("VAULT_ROOT", os.path.expanduser("~/radar/radar"))
FEEDBACK_DIR = os.path.join(VAULT_ROOT, "98_Feedback", "Infrastructure")
```

### `src/patterns.py`
```python
# before
VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar"))
ASSESSMENTS_PATH = os.path.join(VAULT_PATH, "01_Assessments")
PATTERNS_PATH = os.path.join(VAULT_PATH, "02_Patterns")
ARCHIVE_PATH = os.path.join(VAULT_PATH, "03_Archive")
ANALYSTS_PATH = os.path.join(VAULT_PATH, "04_Analysts")

# after
VAULT_ROOT = os.environ.get("VAULT_ROOT", os.path.expanduser("~/radar/radar"))
ASSESSMENTS_PATH = os.path.join(VAULT_ROOT, "01_Assessments")
PATTERNS_PATH = os.path.join(VAULT_ROOT, "02_Patterns")
ARCHIVE_PATH = os.path.join(VAULT_ROOT, "03_Archive")
ANALYSTS_PATH = os.path.join(VAULT_ROOT, "04_Analysts")
```
Line 800 (`print(f"[patterns] vault: {VAULT_PATH}")`) → `{VAULT_ROOT}`.
`ASSESSMENTS_PATH`/`PATTERNS_PATH` attribute names are unchanged from
today — only their internal source variable changes — so no test
changes needed for the lines that already monkeypatch these names.

### `src/backfill_frontmatter.py`
```python
# before
VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar/01_Assessments"))

# after
VAULT_ROOT = os.environ.get("VAULT_ROOT", os.path.expanduser("~/radar/radar"))
ASSESSMENTS_PATH = os.path.join(VAULT_ROOT, "01_Assessments")
```
All other `VAULT_PATH` references (lines 193, 194, 198, 205, 211, plus
the `vault_path` parameter of `verify_local_checkout_matches_origin()`
at line 145/150, called with `VAULT_PATH` at line 211) →
`ASSESSMENTS_PATH`. Not invoked by any CI job — this is a manual-only
script; the change only prevents a silent stale-`VAULT_PATH` divergence
if anyone runs it locally alongside the other 9 now-renamed scripts.

### `src/check_frontmatter.py` — **not touched.**

### `.gitlab-ci.yml`
- Line 17: `VAULT_PATH="$(pwd)/vault_repo/01_Assessments" PATTERNS_PATH="$(pwd)/vault_repo/02_Patterns"` → `VAULT_ROOT="$(pwd)/vault_repo"`
- Line 18: `VAULT_PATH="$(pwd)/vault_repo/01_Assessments"` → `VAULT_ROOT="$(pwd)/vault_repo"`
- Line 44: same substitution
- Line 62: same substitution
- Line 86: same substitution
- Line 111: `VAULT_PATH="$(pwd)/vault_repo/01_Assessments" PUBLISHED_LOG="$(pwd)/vault_repo/99_System/published_posts.log"` → `VAULT_ROOT="$(pwd)/vault_repo"`
- Line 135: `python3 src/fetch_analysts.py --vault vault_repo` → `VAULT_ROOT="$(pwd)/vault_repo" python3 src/fetch_analysts.py`
- Line 166: `VAULT_PATH="$(pwd)/vault_repo"` → `VAULT_ROOT="$(pwd)/vault_repo"`
- Line 181: `VAULT_PATH="$(pwd)/vault_repo"` → `VAULT_ROOT="$(pwd)/vault_repo"`
- All `check_frontmatter.py` invocations (every job that calls it) and
  the `pages` job — unchanged.

### Test files
- `tests/test_confirm_candidate.py:19` — `monkeypatch.setattr(confirm_candidate, "VAULT_PATH", vault_path)` → `"ASSESSMENTS_PATH"`
- `tests/test_promote_candidates.py:89` — `monkeypatch.setattr(promote_candidates, "VAULT_PATH", tmpdir)` → `"ASSESSMENTS_PATH"`
- `tests/test_recheck_lifecycle.py:287` — `monkeypatch.setattr(recheck_lifecycle, "VAULT_PATH", tmpdir)` → `"ASSESSMENTS_PATH"`
- `tests/test_patterns.py:132` — `monkeypatch.setattr(update_assessments, "VAULT_PATH", str(tmp_path))` → `"ASSESSMENTS_PATH"`
- `tests/test_patterns.py:170/184/244/262/279/293/303/314` — already target `ASSESSMENTS_PATH`/`PATTERNS_PATH` on `patterns`, unchanged.
- `tests/test_analyze_candidate.py` — verified not touching `VAULT_PATH`, unchanged.
- No `conftest.py` and no `monkeypatch.setenv`/`os.environ[...]` usage of `VAULT_PATH` found anywhere in `tests/` — confirmed by grep, not assumed.

## Process correction: MR ceremony dropped (2026-08-07, mid-session)

**Owner decision, new general principle going forward**: no MR for
SPEC A.5 — merges to `master` happen via direct `git merge` after a
green Rule 31 acceptance run, without opening a GitLab MR first.
Reason: solo development, no reviewers to route an MR through — the MR
step was ceremony inherited from SPEC A's process without re-examining
whether it earns its cost here. **Going forward**: MR only for
architecture-level changes on the scale of SPEC A (multi-file layout
reorganization, changes touching all 10 CI jobs at once); all smaller
tasks (including the rest of this queue: A.5 itself, A.6, E, C, B, D)
use direct merge after acceptance, no MR. This session had already
pushed `spec-a5-vault-path-unification` and obtained a GitLab
"create MR" link before this correction landed — that link is not
used; the branch is merged directly instead once acceptance is green.

## Test Plan

1. `python3 -m py_compile` on all 10 changed `.py` files after editing
   (9 CI-invoked + `backfill_frontmatter.py`).
2. `python3 -m pytest tests/` locally — must pass with the 4 updated
   test files before pushing.
3. Full diff review + explicit owner confirmation before commit/push
   (Rule: mandatory before every commit in this project).
4. Push to a new branch (`spec-a5-vault-path-unification`). No MR (see
   "Process correction" above) — direct merge after acceptance.
5. Real acceptance run via GitLab web trigger, on the branch, for all 8
   primary jobs: `radar`, `promote_candidates`, `recheck_lifecycle`,
   `publish`, `analysts`, `check_models`, `patterns` triggered for real;
   `confirm_candidate` dry-run only (see Decisions above) unless a real
   `CANDIDATE` file exists in the vault at merge time.
   `backfill_frontmatter.py` is not CI-invoked — verified by local
   `py_compile` + code read only, no acceptance-run entry.
6. All triggered jobs green before merge.
7. Direct `git merge` branch → `master` (no MR, see "Process correction"
   above) only after step 6 passes, with explicit owner confirmation.

### Acceptance Run Result (2026-08-07, branch `spec-a5-vault-path-unification`)

5 web-triggered pipelines covering all 7 live primary jobs, all green,
plus `confirm_candidate` dry-run (code read + local `pytest`, no live
trigger — 15 real `CANDIDATE_LOW_CONFIDENCE` files existed in the vault
at run time, but the owner explicitly reconfirmed dry-run-only mid-session,
overriding the original conditional wording in "Acceptance scope" above):

- `#2739373293` — `recheck_lifecycle` + `lint_vault` — Passed.
- `#2739374559` — `publish` + `lint_vault` — Passed.
- `#2739375863` — `analysts` + `check_models` + `patterns` + `lint_vault` — Passed.
- `#2739369504` — `promote_candidates` + `lint_vault` Passed on first run;
  `radar` failed on first run (`git pull --rebase` conflict, see
  "Related but out-of-scope finding" below), retried in the same
  pipeline and **Passed** on retry, with no other job running
  concurrently by that point (verified via GitLab API before retry —
  all other acceptance pipelines were already in a terminal state).
  Final state: `lint_vault` + `promote_candidates` + `radar`, all Passed.

All 7 live jobs (`radar`, `promote_candidates`, `recheck_lifecycle`,
`publish`, `analysts`, `check_models`, `patterns`) confirmed green,
`confirm_candidate` dry-run confirmed via code read + local `pytest`.
`backfill_frontmatter.py` (10th changed file, not CI-invoked) verified
via local `py_compile` + code read only, per Test Plan step 5.

### Related but out-of-scope finding: `radar`/`recheck_lifecycle` write race (2026-08-07)

The first `radar` attempt in pipeline `#2739369504` failed on
`git pull --rebase origin vault` with a conflict in
`01_Assessments/Верификация_доверия_для_сетей_агентов 2026-07-02.md`.
Root cause confirmed via the public GitLab API before deciding on a
retry: `update_assessments.py` (called by `radar`, reprocesses
assessments >30 days old) and `recheck_lifecycle.py` (appends
`evidence_log` entries to `VALIDATED_SHIFT` files) both target this
same file, and `recheck_lifecycle`'s pipeline (`#2739373293`) pushed
its own change to `origin/vault` in the window between `radar`'s local
commit and its rebase attempt.

**Not a SPEC A.5 bug.** `VAULT_ROOT`/`ASSESSMENTS_PATH` played no role —
this is a pre-existing pipeline-design gap: no job's commit/rebase/push
sequence retries on a rebase conflict, it just fails the job. In normal
production operation this essentially never fires, since these jobs run
on separate cron schedules (`radar` frequently, `recheck_lifecycle`
monthly) rather than back-to-back — it surfaced here only because
acceptance testing deliberately fired 5 pipelines in quick succession
against the same `vault` branch, creating a race that scheduled
operation doesn't normally produce. Same class of finding as SPEC A's
`filter.py` `AttributeError` (production bug surfaced by real execution
during acceptance, unrelated to the migration's own change scope) —
verified via the GitLab API that the failed job's local commit
(`fc8b05e`) never reached `origin/vault` (404 on lookup by SHA) and
that the conflicted file itself was left clean on the remote (no
conflict markers, valid YAML frontmatter) before retrying. No data was
lost or corrupted; the retry re-ran cleanly once no other job was
writing concurrently. Left as a candidate for a future session (e.g. a
retry-on-rebase-conflict loop, or serializing vault-writing jobs) — not
fixed in this session, same "verify, don't silently expand scope"
principle SPEC A applied to `filter.py`.

## Milestones

1. [x] Edit all 10 `.py` files per the per-file plan above (9 CI-invoked
   + `backfill_frontmatter.py`).
2. [x] Edit `.gitlab-ci.yml` per the substitutions above.
3. [x] Edit the 4 test files.
4. [x] `py_compile` + local `pytest` green (99 passed).
5. [x] Full diff review, owner confirmation — found and fixed 2 bugs
   not caught by the line-by-line SPEC check: `patterns.py:800` still
   referenced undefined `VAULT_PATH` (`NameError` at runtime), and a
   stale `VAULT_PATH` mention in a `backfill_frontmatter.py` docstring.
6. [x] Push to `spec-a5-vault-path-unification` (commit `4818962`). No
   MR opened — see "Process correction" above.
7. [x] Real CI acceptance run (8 jobs, 7 live + 1 dry), all green — see
   "Acceptance Run Result" above. One unrelated pipeline-race finding
   surfaced and diagnosed (see "Related but out-of-scope finding").
8. [x] Direct merge to `master` (no MR), owner-confirmed — merge commit
   `10523e4`, pushed to `origin/master`.
9. [x] This SPEC.md section updated with the closure note below; "Full
   queue order" pointer updated to SPEC A.6 as next.

## SPEC A.5: CLOSED (2026-08-07)

All 4 `VAULT_PATH` path-resolution mechanisms collapsed into one:
`VAULT_ROOT` (env var, always the vault root) with per-script derived
subdirectory constants. 10 `.py` files migrated (9 CI-invoked +
`backfill_frontmatter.py`, added mid-session after Rule 28 verification
found it missing from the original inventory), `.gitlab-ci.yml` updated
across all 9 affected job script lines, 4 test files updated for the
renamed monkeypatch targets.

Verification: `py_compile` clean on all 10 files, local `pytest` 99/99
passed both before and after merge. Full diff review (separate pass
from the line-by-line SPEC check) caught 2 real bugs before commit —
`patterns.py:800` referencing the now-undefined `VAULT_PATH`
(`NameError` at runtime) and a stale docstring reference — both fixed
pre-commit. Rule 31 acceptance: 5 web-triggered pipelines, all 7 live
primary jobs (`radar`, `promote_candidates`, `recheck_lifecycle`,
`publish`, `analysts`, `check_models`, `patterns`) confirmed green,
`confirm_candidate` verified via dry-run (code read + local `pytest`)
per owner decision. One unrelated pipeline-write-race surfaced during
acceptance (`radar` vs `recheck_lifecycle` on a shared file, see
"Related but out-of-scope finding" above) — diagnosed via the GitLab
API as non-data-losing and unrelated to this spec's scope, resolved by
retry once the racing job had finished.

Process note: this session also produced a new standing decision
(not specific to SPEC A.5) — GitLab MRs are reserved for SPEC-A-scale
architecture changes; smaller tasks merge directly after a green
acceptance run, no MR ceremony. Applied here: branch pushed, a
GitLab "create MR" link was obtained but never used, merged directly
into `master` instead (commit `10523e4`) after owner confirmation.

Everything under "Out of Scope for SPEC A" above remains genuinely out
of scope for A.5 as well — SPEC A.6 (pytest wired into CI) was next
and is now also closed (see "SPEC A.6: CLOSED" below) — **SPEC E is
next.**

## Open Questions / Decisions Needed

None remaining — all forks resolved during interview (2026-08-07), plus
the `backfill_frontmatter.py` gap found and resolved during this
session's Rule 28 verification (owner: include as 10th file, see
"Verified Inventory" correction above). SPEC A.5 is closed; see
"SPEC A.5: CLOSED" above.

---

# SPEC A.6: pytest Execution Wired Into CI — Specification

## Overview

Tests exist (`tests/`, 99 tests across 8 `test_*.py` files) and pass
locally, but no CI job runs them today — `grep -n "test\|pytest"
.gitlab-ci.yml` returns nothing (confirmed both at SPEC A time and
again in this session). This spec adds a dedicated `test` job that
runs the real suite in CI. Unlike SPEC A and SPEC A.5 (pure reorg /
pure path-mechanism change), this is **genuinely new executable
behavior** — CI starts doing something it never did before — so Rule
31 applies at the stricter bar: a real push-triggered pipeline run,
not a reading of the YAML.

## Verified Against Current Code (2026-08-07)

- **Test file count corrected**: original task brief said 11
  `test_*.py` files; actual count is **8**
  (`test_analyze_candidate.py`, `test_check_frontmatter.py`,
  `test_confirm_candidate.py`, `test_patterns.py`,
  `test_promote_candidates.py`, `test_recheck_lifecycle.py`,
  `test_update_assessments.py`, `test_vault_write.py`). 99 tests
  collected (`pytest --collect-only -q`), matching the brief's "99
  tests" figure.
- **No test performs a real network/API call.** Verified by grepping
  all 8 files for `requests.|anthropic|urlopen|mock|monkeypatch|patch\(`
  — every external dependency (`gh_api`, `check_repo_alive`, etc.) is
  replaced via `monkeypatch.setattr` with fake objects
  (`_FakeGhApi`, `_FakeRepos`, `_FakeActions`) or exercised against
  `tmp_path`/`tmpdir`. No `responses`/`httpretty`/live HTTP anywhere.
- **But import-time still requires 4 runtime packages.** Test files
  import `src/` modules directly (`import analyze`, `import
  vault_write`, etc.), and those modules import `requests`, `ghapi`,
  `anthropic`, `pyyaml` at module scope — even though the tests never
  actually call out over the network. `requirements-dev.txt` currently
  pins only `pytest>=7`; running `pytest tests/` in a bare
  `pip install -r requirements-dev.txt` environment would fail on
  `ModuleNotFoundError` before a single test executes.
- **`lint_vault`'s existing `pip install pyyaml requests --quiet` is
  insufficient** for the full suite (missing `ghapi`, `anthropic`) —
  relevant because bolting pytest onto `lint_vault` was one candidate
  considered and rejected at interview.
- **`vault` branch has no `.gitlab-ci.yml`** (confirmed via `git
  ls-tree -r origin/vault --name-only`). Bot pushes to `vault` by
  `radar`/`confirm_candidate`/`promote_candidates`/`recheck_lifecycle`/
  `publish`/`analysts`/`check_models`/`patterns` do not trigger any
  pipeline there — "block push to vault" (a framing carried over from
  the task brief) is not a mechanism that exists to gate.
- **`pages` already triggers on `push` to `master`/`vault`**, in the
  same stage-sequential pipeline a new push-triggered job would join.
  This is the one real coexistence point for a gating decision — not
  the vault-push framing above.
- **GitLab CI default stage-blocking**: a job that fails in an earlier
  stage (without `allow_failure: true`) prevents jobs in later stages
  of the same pipeline from starting. Combined with the decision to
  place `test` in a new stage before `run` (and therefore before
  `pages`), this means an unqualified job failure would silently block
  `pages` — found and flagged mid-interview, resolved via
  `allow_failure: true` (see Decisions below).

## Decisions (from interview, 2026-08-07)

- **New dedicated job `test`**, not a step bolted onto `lint_vault`.
  Keeps `lint_vault`'s existing meaning (frontmatter lint) separate
  from "run the test suite," and avoids expanding `lint_vault`'s
  install line for a second, unrelated purpose.
- **New stage `test`, first in the pipeline** (before `run`):
  `test -> run -> publish -> collect -> patterns -> pages`. Semantically
  clean (tests gate nothing in practice today, see next point, but the
  ordering reads correctly), zero effect on any of the other 10 jobs'
  existing `rules:` blocks.
- **Trigger: `push`, unrestricted by branch** — fires on any push to
  any ref that carries this `.gitlab-ci.yml` (in practice: `master`
  and feature branches; `vault` has no CI file, see above, so it's
  structurally excluded, not excluded by a branch filter). Chosen over
  `master`-only so tests run on feature-branch pushes too, before
  merge — matches the project's branch-then-direct-merge flow already
  used for SPEC A and SPEC A.5. Chosen over `web`/`web`-inclusive
  because a manual trigger adds owner effort for something that should
  just happen on every push, with no `CONFIRM_REPO`-style reason to
  gate it behind a manual variable.
- **On failure: `allow_failure: true`, no gating of any other job.**
  The task brief's framing ("block push to vault... or just notify")
  doesn't map onto how this system actually works: there is no vault
  push to block (see Verified section), and the 8 vault-writing jobs
  don't share a pipeline with `test` at all (they trigger on
  `schedule`/`web`, `test` triggers on `push` — mutually exclusive
  pipeline-source rules). The only real interaction is `pages`, which
  *does* share a push-triggered pipeline with `test`. Without
  `allow_failure: true`, GitLab's default stage-blocking would silently
  stop `pages` from running whenever `test` fails — an unintended
  side effect the interview surfaced and explicitly rejected.
  `allow_failure: true` makes the job's pass/fail state visible in the
  UI (shown as a warning triangle on failure) without stopping
  anything downstream. No Telegram notification added — unlike
  `lint_vault`, a failing local-code test isn't an owner-facing
  incident requiring a push alert; it's visible in the pipeline UI on
  the next visit.
- **Dependencies: `requirements-dev.txt` stays pytest-only.** The
  `.gitlab-ci.yml` `test` job's install line adds the 4 runtime
  packages inline instead: `pip install -r requirements-dev.txt
  requests anthropic ghapi pyyaml --quiet` — mirrors the `radar`
  job's existing install line exactly (same 4 packages), keeps
  `requirements-dev.txt`'s scope as "test tooling only" (unchanged
  from its SPEC A definition), and avoids a second, competing
  definition of "what packages does `src/` need" living in a file
  most of the other 9 jobs never read.
- **No vault clone in the `test` job.** Unlike every other job, `test`
  never does `git clone --branch vault ...` — confirmed unnecessary
  because no test touches a real vault path; all vault interaction in
  tests goes through `tmp_path`/`monkeypatch`-redirected paths. This
  makes `test` the simplest job in the file: no `git config`, no
  `GITLAB_PUSH_TOKEN`, no commit/push dance.
- **Command: `python3 -m pytest tests/ -q`** — matches the convention
  already documented in SPEC A's Test Plan for local runs, and relies
  on the default checkout already placing `pyproject.toml`
  (`pythonpath = ["src"]`) at the repo root, same as a local run.
- **Image: default `python:3.12`** (top-level `image:` in
  `.gitlab-ci.yml`), no per-job override — same image every other job
  uses; no need to match the local machine's `pytest 9.1.1` / Python
  3.14, since CI has never run tests before and this is establishing
  its own baseline, not preserving one.
- **`allow_failure: true` verified against GitLab's documented
  behavior, not by a dedicated throwaway/dummy-job pipeline run.**
  Considered and rejected: adding a temporary dummy job in a later
  stage on the feature branch purely to prove non-blocking, then
  reverting before merge. Rejected because `allow_failure` is a
  stable, core GitLab CI primitive (not project-specific logic), and
  the added risk/steps (temporary `.gitlab-ci.yml` churn, remembering
  to revert before merge) outweigh re-deriving a platform guarantee
  that's already well-established. Rule 31's real-run requirement is
  still satisfied for everything the project actually wrote: the
  `test` job itself, triggered for real, running the real suite.

## Detailed Requirements

### 1. `.gitlab-ci.yml` — new stage + new job

`stages:` block:
```yaml
stages:
  - test
  - run
  - publish
  - collect
  - patterns
  - pages
```

New job (placed before the existing `radar:` job):
```yaml
test:
  stage: test
  allow_failure: true
  script:
    - pip install -r requirements-dev.txt requests anthropic ghapi pyyaml --quiet
    - python3 -m pytest tests/ -q
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push"'
```

No changes to any of the other 10 jobs — their `script:`, `rules:`,
and stage assignments are untouched. `requirements-dev.txt` content is
untouched (`pytest>=7`, unchanged from SPEC A).

### 2. Files NOT changed

- No `.py` file changes — this spec is CI-config-only.
- `requirements-dev.txt` — unchanged.
- `pyproject.toml` — unchanged (`pythonpath = ["src"]` already covers
  this job's needs).
- No test file changes.

## Non-Functional Requirements

1. Zero behavior change to the existing 10 jobs — same triggers, same
   scripts, same stage membership, verified by diffing
   `.gitlab-ci.yml` before/after outside the `test`-job addition and
   the `stages:` list insertion.
2. `test` job failure must never prevent `pages` (or any other job)
   from running in the same pipeline (`allow_failure: true`).
3. No new files added to the repo — this spec only edits
   `.gitlab-ci.yml`.

## Security Considerations

None — the `test` job never clones the `vault` branch, never uses
`GITLAB_PUSH_TOKEN`/`CI_JOB_TOKEN`, never touches real assessment
data. It runs entirely against the `master`/branch checkout's own
`tests/` and `src/` trees.

## Test Plan

1. `python3 -m py_compile` — not applicable (no `.py` files change in
   this spec).
2. Local: `python3 -m pytest tests/ -q` already green (99/99),
   unaffected by this spec (no test content changes).
3. Push to a new branch (naming convention matches SPEC
   A/A.5: `spec-a6-ci-pytest`). No MR (project process, confirmed
   2026-08-07) — direct merge after acceptance.
4. **Rule 31 acceptance run (real, push-triggered, not inferred from
   YAML)**: the push to the feature branch itself triggers the `test`
   job automatically (its `rules:` match any push). Confirm via the
   GitLab API or UI:
   - `test` job appears in the resulting pipeline, stage `test`.
   - `test` job passes, 99/99, matching the local run.
   - No other job fires in that same pipeline (`pages` is
     master/vault-restricted, all 8 vault-writing jobs are
     schedule/web-restricted) — confirms `test`'s isolation on a
     feature-branch push, consistent with the Decisions above.
5. After merge to `master`: confirm a real push-triggered pipeline on
   `master` runs **both** `test` and `pages` in the same pipeline
   (the actual coexistence this spec's `allow_failure` decision is
   about), both green under normal (non-broken) conditions.
6. Full diff review of `.gitlab-ci.yml` + explicit owner confirmation
   before commit/push (mandatory before every commit in this project).
7. Direct `git merge` branch → `master` (no MR) only after steps 4-6
   pass, with explicit owner confirmation.

## Milestones

1. [x] Create branch `spec-a6-ci-pytest`.
2. [x] Edit `.gitlab-ci.yml`: add `test` stage to `stages:`, add the
   `test:` job block.
3. [x] `python3 -m pytest tests/ -q` locally — confirmed still 99/99
   (sanity check only, no test content changed).
4. [x] Full diff review, explicit owner confirmation before commit.
5. [x] Push to `spec-a6-ci-pytest` (commit `aa611b3`).
6. [x] Rule 31 acceptance: real push-triggered pipeline on the branch,
   confirm `test` job runs and passes, confirm no other job fires
   alongside it.
7. [x] Direct merge to `master` (no MR), owner-confirmed — fast-forward
   merge, commit `aa611b3` on `master`.
8. [x] Post-merge acceptance: real push-triggered pipeline on
   `master`, confirm `test` and `pages` both appear and both pass in
   the same pipeline.
9. [x] This SPEC.md section updated with acceptance run results below;
   "Full queue order" pointer updated to SPEC E as next.

### Acceptance Run Result (2026-08-07)

**Branch run** — pipeline `#2739535090` on `spec-a6-ci-pytest`
(`push` source, sha `aa611b3`): only the `test` job fired
(`status: "success"`, not merely "allowed failure" — the job's own
`status` field, independent of `allow_failure` pipeline aggregation,
confirmed a genuine pass), 41s duration. No other job appeared in the
same pipeline, confirming the isolation predicted at interview:
`pages` is restricted to `master`/`vault`, the 8 vault-writing jobs
are restricted to `schedule`/`web` — none of them share a `push`-on-
feature-branch pipeline with `test`.

**Post-merge run** — pipeline `#2739538824` on `master` (`push`
source, sha `aa611b3`, triggered automatically by the merge push):
`status: "success"` overall. Both `test` and `pages` fired in the same
pipeline and both reached `status: "success"` — the specific
coexistence scenario `allow_failure: true` was added to protect. This
confirms the mid-interview stage-blocking finding was correctly
resolved: a `test`-stage job ahead of `pages` in the stage order did
not prevent `pages` from running.

Verification method: GitLab public read-only API (project ID
`82780086`, no token — project confirmed `visibility: "public"`),
polling `/pipelines/:id` and `/pipelines/:id/jobs`. The
`/jobs/:id/trace` endpoint returned `401 Unauthorized` even on this
public project (raw job log not fetchable without a token) — job-level
`status` field from the jobs-list endpoint was used as the source of
truth instead, which is sufficient to distinguish a real pass from an
allowed failure (the two are different `status` values, `success` vs
`failed`, independent of the `allow_failure` flag).

Both `git merge` (fast-forward, no conflicts) and both pipeline runs
completed with explicit owner confirmation before each shared-state
action (branch push, merge, master push), per the project's
[ЗАПРОС]-before-action process.

## SPEC A.6: CLOSED (2026-08-07)

`test` job added to `.gitlab-ci.yml`: new `test` stage (first in the
pipeline), `push`-triggered on any branch, `allow_failure: true`,
installs `requirements-dev.txt` + `requests anthropic ghapi pyyaml`
inline, runs `python3 -m pytest tests/ -q`. No vault clone, no `.py`
file changes, `requirements-dev.txt` unchanged (stays pytest-only).
All 10 pre-existing jobs unmodified — confirmed by diff.

Verified both on a feature branch (isolated run, only `test` fired)
and post-merge on `master` (coexistence with `pages` in the same
pipeline, both green) — see "Acceptance Run Result" above. Real CI
runs, not YAML inference, per Rule 31's stricter bar for genuinely new
executable behavior.

Everything under SPEC A's "Out of Scope" list remains genuinely out of
scope — **SPEC E (security scanning) is next.**

## Open Questions / Decisions Needed

None remaining — all forks resolved during interview (2026-08-07),
including the mid-interview stage-blocking/`allow_failure` correction
(see "Verified Against Current Code" and Decisions above). SPEC A.6 is
closed; see "SPEC A.6: CLOSED" above.

---

# SPEC E: Security Scanning (Secrets + Dependency CVEs + One-Time Deep History Audit) — Specification

## Overview

Add security scanning as its own check class, ahead of SPEC C (GitHub
mirroring) on purpose — anything forgotten in the git history (a
secret, a vulnerable dependency) should surface before the repo
becomes visible on GitHub, not after. Three tools, three different
jobs (compactness verified per-tool at interview, not assumed):
Betterleaks (recurring secret scanning, both branches, CI-gated),
pip-audit (recurring dependency-CVE scanning, both branches'
combined runtime+dev deps), TruffleHog (one-time deep history audit
of both branches, run locally, not wired into CI).

## Verified Against Current Code (2026-08-07)

### Real inventory (grepped, not assumed)

- 11 jobs in `.gitlab-ci.yml`, stages `test -> run -> publish ->
  collect -> patterns -> pages`: `test`, `radar`, `confirm_candidate`,
  `promote_candidates`, `recheck_lifecycle`, `publish`, `analysts`,
  `lint_vault`, `check_models`, `patterns`, `pages`. All on `image:
  python:3.12`.
- `requirements-dev.txt`: `pytest>=7` only.
- `requirements_pages.txt`: `mkdocs`, `mkdocs-material`, `pyyaml`,
  `requests` — unpinned (project convention, not a pinned-lockfile
  project).
- Runtime deps inline across `pip install` lines in every other job:
  `requests`, `anthropic`, `ghapi`, `pyyaml` (grepped from all 11
  `pip install` invocations in the file).
- `lint_vault` (existing job, same class of check — periodic,
  schedule/web-triggered, notifies via Telegram on failure) is the
  structural template this SPEC's two new jobs follow: `pip install
  ... --quiet`, clone `vault_repo` read-only via
  `${CI_JOB_TOKEN}`, `rules: [schedule, web]` with no extra variable
  gating (fires on *every* scheduled/web pipeline regardless of which
  other job's purpose-specific variable is set — existing behavior,
  not something this SPEC introduces).

### Tool availability — checked live, not presumed

| Tool | pip-installable? | Verified fact |
|---|---|---|
| `pip-audit` | yes | PyPI, v2.10.1, official PyPA tool, uses free OSV.dev DB, no API key |
| `safety` | yes | PyPI, v3.8.1, but v3.x pushes toward a safety-platform account/API key for full DB access — rejected for this reason |
| Gitleaks | no | Not on PyPI. Go binary, GitHub releases. Latest `v8.30.1` |
| Betterleaks | no | Not on PyPI. Go binary, GitHub releases. Latest `v1.7.3` (released 2026-07-31), repo created 2026-02-03, 1616 stars, 72 open issues, MIT, not archived. Release assets include `checksums.txt` + `checksums.txt.sigstore.json` |
| TruffleHog (v3, `trufflesecurity/trufflehog`) | no | Go binary, GitHub releases. Latest `v3.96.0` |
| `truffleHog` (pip, v2.2.1) | yes, but a trap | Deprecated, abandoned v2, entropy-only — not the tool this SPEC means |
| `trufflehog3` | yes, but a trap | Unrelated third-party reimplementation, not the official project |

### Prior context — not starting from zero

A manual grep audit already happened (session 2026-07-17): master
(~247 matches) and vault (~339 matches) checked against
`sk-ant-`/`ghp_`/`glpat-`/`xoxb-`/`AIza` patterns — every match was an
env-variable reference, no real leak found. Separately, the
`obsidian-git` plugin (vendored binary/plugin code) was found
committed into vault's history — a repo-hygiene issue, not a secret,
still unresolved, out of scope here. This SPEC does not start from a
blank slate, but a manual grep is not the same as a purpose-built
scanner, and there have been many commits since — hence Betterleaks
and TruffleHog both re-check for real.

## Decisions (from interview, 2026-08-07)

1. **Dependency CVE scanner: `pip-audit`**, not `safety`. Free OSV.dev
   backend, no account/API key — matches the project's "no extra
   service, no extra secret" bias. `safety` v3.x's push toward a
   platform account was the deciding factor against it.
2. **Binary install method for both Go tools: `curl` + pinned release
   version**, not `curl | sh` install scripts. Version pinned
   literally in `.gitlab-ci.yml` — reproducible, no "whatever's
   latest today" drift.
3. **Secret scanner: Betterleaks**, not Gitleaks — resolved as a
   mid-interview fork (see below), against the interviewer's
   recommendation of Gitleaks. Owner's explicit call.
4. **Betterleaks trigger: `schedule` + `web`, both branches**
   (`master` and `vault`, cloned/scanned separately) — same
   trigger shape as `lint_vault`. `vault` is the higher-risk branch
   (real data written every run) and must not go unscanned.
5. **On a finding (Betterleaks or pip-audit): hard fail**
   (`allow_failure: false`, the job's default) **+ Telegram
   notification**, reusing the existing `TELEGRAM_BOT_TOKEN` /
   `TELEGRAM_OWNER_ID` CI variables and `lint_vault`'s
   curl-to-Telegram pattern. A red pipeline is the point — nothing
   should be easy to ignore.
6. **pip-audit source: new `requirements-security.txt`** at repo
   root (master branch), consolidating every runtime + dev dependency
   named anywhere in the project (`requests`, `anthropic`, `ghapi`,
   `pyyaml`, `mkdocs`, `mkdocs-material`, `pytest`) into one audit
   target — unpinned, matching the existing `requirements-dev.txt` /
   `requirements_pages.txt` convention (all inline `pip install`s in
   the project are already unpinned, so auditing pinned versions would
   report against something nothing actually runs). Triggered on
   `schedule` + `web`, same shape as the Betterleaks job.
7. **TruffleHog: run locally, once, not wired into CI.** This is a
   one-time deep-history audit, not a recurring check — adding a
   permanent CI job for a one-off would be scope creep and a
   maintenance burden with no ongoing payoff. Scans full history
   (`--only-verified` pass for a clean "rotate this now" signal, plus
   a separate full/unverified pass for completeness — verified
   findings are definitive, unverified ones are still worth knowing
   about even if TruffleHog couldn't confirm the credential is live).
   Both branches (`master`, `vault`).
8. **New `security` stage, placed first** in `stages:` (ahead of
   `test`): `security, test, run, publish, collect, patterns, pages`.
   Matches the task's own framing (security should be visible before
   anything else, ahead of SPEC C). Schedule/web-triggered jobs don't
   block each other by stage order (confirmed empirically in SPEC
   A.6's acceptance run for the `test` stage), so this reordering
   carries no coexistence risk for the existing 11 jobs.
9. **Two separate jobs**, not one combined job: `security_secrets`
   (Betterleaks) and `security_deps` (pip-audit). Independent
   pass/fail status in the GitLab UI, one tool's failure doesn't
   suppress the other's from even running.
10. **Sequencing: local baseline/triage first, hard-fail CI job
    second.** Both Betterleaks and TruffleHog get a manual local run
    against full history first; any false positive shaped like the
    known "env-var reference" pattern from the 2026-07-17 audit gets
    resolved (allowlist or confirmed-safe) *before* `security_secrets`
    is added to `.gitlab-ci.yml` as a hard-fail job. Avoids landing a
    red pipeline on day one from noise that was already known to
    exist.
11. **Remediation scope: rotation only.** If Betterleaks or TruffleHog
    finds a real secret, this SPEC covers rotating it (existing
    Absolute Rule — one secret per service/task). Purging it from git
    history (`git filter-repo` / BFG) is explicitly **out of scope**
    here — it's a destructive, history-rewriting operation with its
    own blast radius (every SHA changes, interacts with SPEC C's
    future GitHub mirror) and deserves its own SPEC if it's ever
    needed.
12. **CVE remediation process**: on a `pip-audit` finding, bump the
    affected package's pin in `requirements-security.txt` (or drop the
    unpinned entry to a `>=fixed-version` floor) and verify the
    inline `pip install` lines across the 11 jobs pick up the fix
    (they're already unpinned, so they'll get the patched version
    automatically — `requirements-security.txt` exists to *catch*
    this, not to *pin* what's installed at runtime).

### Mid-interview fork: Gitleaks vs Betterleaks (2026-08-07)

Owner flagged, mid-interview, that Gitleaks has a same-author
"spiritual successor," Betterleaks — verified live via web search and
GitHub API, not assumed:

- Betterleaks: `betterleaks/betterleaks`, created 2026-02-03, latest
  `v1.7.3` (2026-07-31), 1616 stars, 72 open issues, MIT. Built by
  Zach Rice — the original Gitleaks author, who lost repository/name
  control and restarted under a new name. Same CLI philosophy
  (`betterleaks git <path>` scans full history by default,
  `betterleaks dir <path>` for a working-tree-only scan — not
  byte-for-byte identical to Gitleaks' `detect --source`, "drop-in"
  per the project's own claim but not independently confirmed flag-
  for-flag at interview time). Detection engine: Token Efficiency (BPE
  tokenization) instead of Shannon entropy — 98.6% vs 70.4% recall
  claimed on the CredData benchmark (self-reported by the
  project/Aikido, not third-party verified). Release assets are
  checksum + sigstore-signed.
- Gitleaks: `v8.30.1`, 8 years of history, huge CI-example ecosystem,
  author has publicly stated it "will remain stable and continue to
  receive security patches" despite stepping back to build Betterleaks.

Interviewer's recommendation was Gitleaks — for a tool whose first-ever
role in this project is a hard-fail CI gate, a proven 8-year tool
carries less unknown-unknown risk than a 6-month-old one (72 open
issues is a meaningful count at that age), and the recall benchmark is
self-published by an interested party. **Owner overrode this and chose
Betterleaks** — the better detection engine and the direct relevance
to the exact false-positive class already seen in the 2026-07-17 manual
audit (env-var-reference matches) were the deciding factors. Recorded
as an explicit owner override, not a silent pick.

## Detailed Requirements

### 1. `requirements-security.txt` (new file, repo root, master)

```
requests
anthropic
ghapi
pyyaml
mkdocs
mkdocs-material
pytest
```

Unpinned, matching existing convention. Consolidates every dependency
named anywhere in `.gitlab-ci.yml` or `requirements_pages.txt` /
`requirements-dev.txt` into one `pip-audit -r` target.

### 2. `.gitlab-ci.yml` — new `security` stage, two new jobs

`stages:` gains `security` as the first entry.

`security_secrets` (Betterleaks):
- `stage: security`
- `variables: GIT_DEPTH: "0"` — GitLab's default checkout for the
  job's own working copy (`master`) may be a shallow clone; Betterleaks
  scanning full history requires `GIT_DEPTH: 0` explicitly, otherwise
  it silently only sees the last N commits. (The `git clone --branch
  vault ...` step for the vault side is a plain `git clone`, not
  GitLab's automatic checkout, so it already gets full history without
  this variable — only the `master` side needs it.)
- `curl`-download pinned `betterleaks_1.7.3_linux_x64.tar.gz` from the
  `betterleaks/betterleaks` GitHub release, verify against
  `checksums.txt`, `chmod +x`.
- Scan `master`'s own working copy, then `git clone --branch vault`
  (read-only, `${CI_JOB_TOKEN}`, same pattern as every other job) and
  scan that.
- On any finding: POST to Telegram (`TELEGRAM_BOT_TOKEN` /
  `TELEGRAM_OWNER_ID`, same curl pattern as `lint_vault`), `exit 1`.
- `rules: [schedule, web]`, no extra variable gate — same shape as
  `lint_vault`.

`security_deps` (pip-audit):
- `stage: security`
- `pip install pip-audit --quiet`
- `pip-audit -r requirements-security.txt`
- On any finding: same Telegram pattern, `exit 1`.
- `rules: [schedule, web]`.

Neither job needs `GITLAB_PUSH_TOKEN` — both are read-only, they don't
write back to `vault`.

### 3. Local one-time TruffleHog run (not in CI)

Pinned `trufflehog_3.96.0_linux_amd64` (or the macOS build for a local
Mac run), against local clones of both `master` and `vault` with full
history present. Two passes: `--only-verified` first (definitive,
"rotate this now" signal), then a full unverified pass for
completeness. Results triaged manually; any confirmed secret gets
rotated per the existing Absolute Rule.

### 4. Local one-time Betterleaks baseline (before the CI job exists)

Same two branches, full history, run locally before
`security_secrets` is added to `.gitlab-ci.yml`. Any finding shaped
like the 2026-07-17 audit's env-var-reference false positives gets
resolved — either confirmed genuinely safe and allowlisted (see
"Betterleaks allowlist mechanism — confirmed" below), or, if real,
rotated before the CI job goes in hard-failing.

#### Betterleaks allowlist mechanism — confirmed (2026-08-07, `betterleaks --help`, v1.7.3)

Installed the real binary and read `--help` rather than guessing —
resolves the Open Question left at interview time:

- `-b/--baseline-path <file>` — path to a baseline of already-accepted
  findings (the actual "allowlist" mechanism for known false
  positives).
- `-i/--gitleaks-ignore-path <path>` (default `.`) — looks for
  `.betterleaksignore` **or** `.gitleaksignore` in that path.
- `-c/--config <file>` — custom rule config; precedence: `--config` →
  `BETTERLEAKS_CONFIG`/`GITLEAKS_CONFIG` env → `BETTERLEAKS_CONFIG_TOML`/
  `GITLEAKS_CONFIG_TOML` env → `.betterleaks.toml` or `.gitleaks.toml`
  in the target path.

No discrepancy from what was assumed at interview time — confirms the
project's own "drop-in" claim: both native `.betterleaks*` filenames
and legacy `.gitleaks*` filenames are read natively, no translation
needed. If the local baseline run below needs an allowlist, it goes in
a `.gitleaksignore` (or `.betterleaksignore`) at repo root, committed
to `master`.

## Test Plan / Acceptance

Per Rule 31 (this SPEC touches `.gitlab-ci.yml`, requires a real
push/web-triggered pipeline run, not YAML inference):

1. Local baseline runs (TruffleHog, Betterleaks) completed and triaged
   first — see Decisions #10 above. Any real finding rotated before
   proceeding.
2. `requirements-security.txt` added, `security` stage + both new jobs
   added to `.gitlab-ci.yml` on a feature branch.
3. Full diff review + explicit owner confirmation before commit/push
   (mandatory, every commit).
4. Real web-triggered pipeline on the feature branch: confirm both
   `security_secrets` and `security_deps` fire and reach `status:
   "success"` (post-triage state should be clean — a failure here
   means the baseline triage missed something, not a spec defect).
   Confirm no unrelated job fires alongside them (same isolation check
   pattern as SPEC A.6's acceptance run).
5. Direct `git merge` to `master` (no MR — below SPEC-A architectural
   scale), owner-confirmed.
6. Post-merge: real web-triggered pipeline on `master`, confirm both
   jobs still fire and pass there too.
7. This SPEC.md section updated with acceptance run results; "Full
   queue order" pointer updated to SPEC C as next.

## Milestones

1. [x] Local TruffleHog full-history run, both branches, triage,
   rotate anything real.
2. [x] Local Betterleaks baseline run, both branches, triage
   (allowlist or rotate as needed).
3. [x] Create `requirements-security.txt`.
4. [x] Branch `spec-e-security-scanning`, edit `.gitlab-ci.yml`:
   `security` stage first, `security_secrets` + `security_deps` jobs.
5. [x] Full diff review, explicit owner confirmation before commit.
6. [x] Push, real web-triggered acceptance run on the branch (both new
   jobs green, no unrelated job fires).
7. [x] Direct merge to `master`, owner-confirmed.
8. [x] Post-merge acceptance: real web-triggered pipeline on `master`,
   both jobs green.
9. [x] This SPEC.md section updated with acceptance results; queue
   pointer moved to SPEC C.

### Acceptance Run Result (2026-08-07)

**Isolation risk found and resolved before triggering anything**: unlike
SPEC A.6's `test` job (`push`-triggered, cleanly isolated),
`security_secrets`/`security_deps` require `schedule` or `web` — a bare
`web` pipeline on this project also satisfies `radar`'s rule (`web &&
$PUBLISH_ONLY != "true" && $PATTERN_MODE != "weekly" &&
$LIFECYCLE_ONLY != "true"`), and every variable that would suppress
`radar` turns on a different production job (`publish`,
`check_models`/`patterns`/`analysts`, or `recheck_lifecycle`
respectively) — no variable combination isolates just the two new
jobs. This is a pre-existing property of `.gitlab-ci.yml`'s rules, not
something SPEC E introduced. Flagged explicitly to the owner before
triggering; owner accepted `radar` (and `lint_vault`, same situation)
firing alongside the two new jobs as a real side effect, rather than
this SPEC silently expanding scope to also refactor the trigger
isolation of five pre-existing jobs.

**Branch run** — pipeline `#2739617177` on `spec-e-security-scanning`
(`web` source, sha `cdbdab0`): four jobs fired, all `status:
"success"` — `security_secrets`, `security_deps`, `lint_vault`,
`radar`. Exactly the four predicted (the other 9 jobs' rules require
`push` or a specific gating variable not set here) — confirms
isolation from everything else.

**Post-merge run** — direct `git merge --ff-only` to `master`
(`cdbdab0`), pushed. Two pipelines resulted:
- automatic `push`-triggered pipeline `#2739636945`: `test` and
  `pages` both `success` (the SPEC A.6 coexistence check, still holds
  — unaffected by SPEC E since `security_secrets`/`security_deps`
  don't fire on `push`).
- manual `web`-triggered pipeline `#2739638228` (per Rule 31, real run
  not inferred): same four jobs as the branch run —
  `security_secrets`, `security_deps`, `lint_vault`, `radar` — all
  `status: "success"`.

Verification method: same as SPEC A.6 — GitLab public read-only API
(project ID `82780086`, no token), `/pipelines/:id/jobs` job-level
`status` field (`/jobs/:id` and `/jobs/:id/trace` both return `401`
even for this public project — reconfirmed here, `/pipelines/:id/jobs`
remains the only usable unauthenticated endpoint for this).

Both `git merge` and both pipeline triggers completed with explicit
owner confirmation before each shared-state action, per the project's
[ЗАПРОС]-before-action process.

## Open Questions / Decisions Needed

None remaining — resolved during implementation (2026-08-07):

- ~~Exact Betterleaks allowlist/ignore-config filename and syntax~~ —
  resolved, see "Betterleaks allowlist mechanism — confirmed" above
  (`.gitleaksignore`/`.betterleaksignore` + `-b/--baseline-path`).
- ~~Whether the local baseline surfaces a real finding~~ — resolved,
  see "Local Baseline Run Result" below. Clean on both tools; no
  rotation, no allowlist needed.

### Local Baseline Run Result (2026-08-07)

Ran against local full clones of both `master` and `vault` (`git
clone --branch <X> https://gitlab.com/lyolich777ka/radar.git`, no
`--single-branch` — note: this pulls every remote branch's objects
into both local clones regardless of which branch is checked out, so
each clone already contained the complete history of both `master`
and `vault`; confirmed via `git branch -a` in each clone and via
identical scan byte-counts/results between the two. This doesn't
affect the CI job design below — GitLab CI's automatic checkout *is*
single-branch by default, so the explicit `git clone --branch vault`
step in `security_secrets` remains necessary there.)

**TruffleHog v3.96.0** (binary downloaded from
`trufflesecurity/trufflehog` release `v3.96.0`, darwin_arm64,
checksum verified against the release's `_checksums.txt` before
execution):
- `--only-verified` pass: 6 findings, all `DetectorName: Lob`, all
  confirmed false positives — `Raw` value in every case is a Python
  test function name (`test_frozen_entered_then_no_dup_next_run`,
  `test_validate_paths_returns_only_invalid`,
  `test_unknown_alive_state_stays_candidate`,
  `test_file_with_valid_state_value_is_none`,
  `test_non_dict_top_level_is_unrecoverable`,
  `test_valid_json_passes_through_unchanged`, across
  `tests/test_recheck_lifecycle.py`, `tests/test_check_frontmatter.py`,
  `tests/test_promote_candidates.py`, `tests/test_patterns.py`), which
  happens to match Lob's API key format (`test_...`) closely enough
  that TruffleHog's live verification call against Lob's API returned
  a false "verified" positive — a known false-positive class for the
  Lob detector, not a real credential of any kind.
- Full pass (verification still runs by default, `--only-verified`
  only changes output filtering, confirmed via `unverified_secrets: 0`
  in both the filtered and unfiltered run): same 6 Lob false positives,
  zero additional findings across 2113 chunks / ~3.8MB / 118+209
  commits combined object graph.
- No real secret found. No rotation needed.

**Betterleaks v1.7.3** (binary downloaded from `betterleaks/betterleaks`
release `v1.7.3`, darwin_arm64, checksum verified against the
release's `checksums.txt` before execution): `betterleaks git
<clone-path>` against both local clones — **"no leaks found"**, zero
findings on either. No allowlist needed (nothing to allowlist). This
outcome — Betterleaks producing zero false positives where TruffleHog's
Lob detector produced 6 — is a small real-world data point in favor of
the Betterleaks-over-Gitleaks call made mid-interview, though it's a
single data point, not a controlled comparison (Gitleaks was never run
against this repo for a direct comparison).

Conclusion: repo is clean per both tools' full-history scan of both
branches. `security_secrets` (Betterleaks) can go straight to
hard-fail in CI with no baseline allowlist file needed.

## SPEC E: CLOSED (2026-08-07)

`security` stage added first in `.gitlab-ci.yml`. Two new jobs,
`schedule`/`web`-triggered, hard-fail (`allow_failure` defaults to
`false`) + Telegram notification on any finding, matching
`lint_vault`'s existing pattern:

- `security_secrets` — Betterleaks `v1.7.3` (pinned, checksum-verified
  at download time), scans `master` (`GIT_DEPTH: 0` for full history)
  and `vault` (fresh clone, already full history by default).
- `security_deps` — `pip-audit` against new `requirements-security.txt`
  (consolidates every runtime + dev dependency named anywhere in the
  project).

Local one-time baseline (TruffleHog `v3.96.0` + Betterleaks `v1.7.3`,
full history, both branches) ran before the CI job went in hard-failing
— clean: TruffleHog's only findings were 6 confirmed false positives
(Lob detector matching Python test-function names), Betterleaks found
nothing. No rotation, no allowlist file needed. TruffleHog itself is
not wired into CI — one-time audit per Decision #7, not a recurring
check.

Verified on a feature branch (`web`-triggered, isolated to the 4
predicted jobs) and post-merge on `master` (`web`-triggered, same 4
jobs green; separately, the automatic `push`-triggered pipeline
confirmed `test`+`pages` coexistence still holds) — see "Acceptance
Run Result" above. Real CI runs, not YAML inference, per Rule 31.

A pre-existing `.gitlab-ci.yml` property was surfaced during
acceptance-run planning (no clean way to `web`-trigger this project
without also firing `radar` or another production job) — flagged to
the owner explicitly rather than silently expanding this SPEC's scope
to fix it. Left as-is; a candidate for its own SPEC if it ever becomes
a real problem.

**Full queue order**: SPEC A → SPEC A.5 → SPEC A.6 → SPEC E → SPEC C.

# SPEC C: GitHub Push Mirroring — Specification

## Overview

Mirror `master` (code only, not `vault`) from GitLab (source of truth)
to a public GitHub repository, for discoverability, using GitLab's
native push-mirroring feature — no CI code involved.

## Goals

- [ ] `master` pushed to GitHub automatically on every push to GitLab,
      via GitLab's built-in push mirror (no custom CI job).
- [ ] `vault` branch never reaches GitHub.
- [ ] New GitHub PAT scoped minimally, stored only where it's actually
      consumed (the Mirroring form), not duplicated into CI/CD Variables.
- [ ] GitHub-side repo clearly marked as a mirror, protected against
      accidental direct writes.

## Resolutions carried in from interview

These were decided before or during this interview and are not
reopened:

1. **New GitHub PAT, separate from `GITHUB_READ_TOKEN`.** Rationale:
   "one secret per service/task" is already the project's standing rule
   (precedent: `git-cli-local` token ≠ `GITHUB_READ_TOKEN`). Push
   mirroring is a new task with different rights (push, not read) →
   new secret by the same principle. Decided by the owner before this
   interview started; not reopened.

2. **PAT storage: Mirroring form only, not duplicated into GitLab
   CI/CD Variables.** The brief assumed parity with the project's other
   6 secrets (`ANTHROPIC_API_KEY`, `GITHUB_READ_TOKEN`,
   `GITLAB_PUSH_TOKEN`, `TELEGRAM_BOT_TOKEN`/`CHANNEL_ID`/`OWNER_ID`),
   all of which live in CI/CD Variables because a CI job reads them.
   Verified against the real `.gitlab-ci.yml` (12 jobs, no mirror-related
   job) and GitLab's mirroring mechanism during this interview: push
   mirroring is driven by a GitLab daemon, not by `.gitlab-ci.yml` — no
   job reads this credential, so it lives only in Settings → Repository
   → Mirroring → Password (write-only after save, visible only for
   reset, Maintainer+ only). Duplicating it into CI/CD Variables would
   create a second copy with no consumer — attack-surface and future-audit
   confusion, not a useful hedge. If a future CI job genuinely needs this
   token, add it to CI/CD Variables at that point, with an explicit reason.

3. **PAT scope: fine-grained, repository-scoped to the new GitHub mirror
   repo only, `Contents: Read and write` permission.** Minimal blast
   radius — compromise of this token grants no access to any other
   repository on the GitHub account, unlike a classic `repo`-scope PAT.

4. **Branch scope: `master` only.** `vault` is project data (assessments,
   patterns, candidates), not code, on its own git history unrelated to
   `master`. Discoverability is a code concern. `vault` public/private
   status is a separate, not-yet-decided backlog item and must not be
   settled implicitly via a mirroring config choice.

5. **GitHub repo: same slug (`radar`), public.** Matches the GitLab slug;
   public matches the discoverability goal (mirroring for a private repo
   would defeat the purpose).

6. **Sync-failure monitoring: GitLab's built-in email notification to
   Maintainers is sufficient.** No new CI job or Telegram hook — the
   mirror is not production-critical (GitLab remains source of truth),
   so a dedicated monitoring job would be cost without matching benefit.
   Failures also surface visually in Settings → Mirroring as an
   `error` status.

7. **GitHub-side hardening: both a README mirror notice and GitHub
   branch protection on `master`.** Different risk classes — the README
   note (GitLab is source of truth, PRs/issues go there) guards against
   human confusion; branch protection (no direct push except the
   mirror's own credential) guards against silent divergence from source
   of truth if the GitHub side ever gets a stray collaborator with write
   access. Both are near-zero-cost; the savings from skipping either
   don't justify leaving a free, avoidable risk in place.

8. **No `.gitlab-ci.yml` changes, no feature branch for CI code.**
   Confirmed by grepping the current file (12 jobs, `security → test →
   run → publish → collect → patterns → pages`, nothing mirror-related)
   and cross-checking GitLab's docs during this interview: push
   mirroring is entirely UI-configured. The only repo-content change in
   this SPEC is the README mirror notice (Resolution 7), landed directly
   — below the SPEC-A-scale threshold for an MR per the project's
   standing process rule.

## Discovered constraint: branch exclusion mechanism

GitLab push mirrors have **no blacklist** for branches — there is only
one filtering option, **"Only mirror protected branches"** (a
whitelist). Confirmed against GitLab's docs during this interview.
Checked the repo's current protected-branch state via the public read-only
API (`GET /projects/82780086/protected_branches`) — **empty**, neither
`master` nor `vault` is currently protected.

To satisfy Resolution 4 (`master`-only mirroring), `master` must
become a protected branch and `vault` must not, with "Only mirror
protected branches" enabled on the mirror. This is a new required setup
step, not previously covered in the brief. Protecting a branch is a
protected-branch action — per the project's known constraint, this
requires the GitLab web UI (unavailable from CLI/Claude Code).

## Implementation Steps (all manual, owner-executed via web UI)

Claude Code has no GitHub access, no GitLab token, and no CLI for
either platform in this environment — every step below is a
`[ЗАПРОС]`-style owner action. Sequencing matters (protection before
mirror config, mirror config before test push).

1. **[ЗАПРОС] GitHub: create empty repository.**
   Action: create a new **public** repository named `radar` under the
   owner's GitHub account. Do not initialize with README/license/
   .gitignore — must be empty so the first push mirror sync is a clean
   fast-forward. Confirm?

2. **[ЗАПРОС] GitHub: create fine-grained PAT.**
   Action: Settings → Developer settings → Personal access tokens →
   Fine-grained tokens → Generate new token. Repository access:
   "Only select repositories" → `radar` (the one just created).
   Permissions: Repository permissions → Contents → **Read and write**.
   No other permissions. Expiration: owner's choice (GitHub caps
   fine-grained PATs at 1 year; note the expiry date so it can be
   rotated before it silently breaks the mirror). Confirm scope and
   proceed?

3. **[ЗАПРОС] GitLab: protect `master`.**
   Action: Settings → Repository → Protected branches → Protect →
   branch `master`. Default "Allowed to push/merge: Maintainers" is
   fine (mirroring reads from the local repo, it doesn't need special
   push rights on the GitLab side). Do **not** protect `vault`. Confirm?

4. **[ЗАПРОС] GitLab: configure the push mirror.**
   Action: Settings → Repository → Mirroring repositories → Add:
   - Git repository URL: `https://github.com/<owner>/radar.git`
   - Mirror direction: **Push**
   - Authentication method: **Username and Password**
     - Username: GitHub username
     - Password: the fine-grained PAT from step 2
   - Check **"Only mirror protected branches"** (this is what excludes
     `vault`, per the discovered constraint above)
   - Leave "Keep divergent refs" unchecked (not needed — GitHub side has
     no independent history to preserve)

   Confirm before saving (this stores a live credential)?

5. **[ЗАПРОС] GitHub: branch protection on `master` (executed via
   Rulesets, not classic branch protection — corrected below).**
   Action: Settings → Rules → Rulesets → New branch ruleset.
   - Ruleset Name: `master`
   - Enforcement status: **Active** (not the default `Disabled`)
   - Target branches: Add target → **Add a branch name pattern** →
     `master` (not "Include default branch" — an empty repo's default
     branch is typically `main`, which won't match; `master` doesn't
     exist as a ref yet until the mirror's first push)
   - Rules: check **Restrict updates** (this is the actual mechanism —
     "only bypass-listed actors can update matching refs"; GitHub's
     current Rulesets UI replaced the classic "Restrict who can push"
     checkbox this SPEC originally assumed). Also keep **Restrict
     deletions** and **Block force pushes** checked.
   - Bypass list → Add bypass → role **Repository admin** (Rulesets'
     bypass list only offers roles/apps, not individual usernames —
     the repo owner holds the admin role by virtue of creating the
     repo in step 1, so this covers the account the mirror
     authenticates as without blocking it)
   - Create

   Corrected against the actual GitHub UI during acceptance execution
   (2026-08-07) — GitHub had moved to Rulesets since this SPEC's
   original terms were drafted from general knowledge, not verified
   live.

6. **README mirror notice (Claude Code executes, direct to `master`,
   no MR — Resolution 8).**
   Add a short note near the top of `README.md` stating GitHub is a
   read-only mirror, GitLab is source of truth, and PRs/issues belong
   on GitLab. Exact wording to be drafted at implementation time and
   shown to the owner before committing (small, reversible, in-repo
   change — not a `[ЗАПРОС]` for external-system state, but still shown
   before commit per the "verify real path before write" rule).

## Test Plan (Acceptance Run)

1. After steps 1-5 above are confirmed done by the owner, Claude Code
   makes the README-notice commit (step 6) directly to `master` on
   GitLab and pushes it.
2. Wait for GitLab's mirror sync (up to 1 minute, since "Only mirror
   protected branches" is on — GitLab's docs state 1 minute for
   protected-branch-only mirrors vs. 5 minutes otherwise).
3. Verify via the **public, unauthenticated GitHub API** (repo is
   public, no token needed) that the commit SHA on
   `github.com/<owner>/radar` `master` matches the commit SHA just
   pushed to `gitlab.com/lyolich777ka/radar` `master`:
   `curl -s https://api.github.com/repos/<owner>/radar/commits/master | jq .sha`
4. Separately confirm `vault` did **not** appear as a branch on GitHub:
   `curl -s https://api.github.com/repos/<owner>/radar/branches | jq '.[].name'`
   must not list `vault`.
5. Green = both checks pass. This is a real API check against live
   state, not YAML/UI inference, per the project's standing verification
   rule.

## Security Considerations

- PAT is fine-grained, single-repo, `Contents: RW` only — minimal blast
  radius if leaked (Resolution 3).
- PAT lives in exactly one place (the Mirroring form), consistent with
  "one secret, one consumer, no idle copies" (Resolution 2).
- GitHub-side branch protection (step 5) prevents the mirror's own
  target from becoming a second writable copy of the codebase reachable
  by anyone but the owner and the mirror credential.
- `vault` exclusion is enforced structurally (protected-branches
  whitelist), not by convention — it cannot be pushed by accident once
  step 3+4 are in place correctly.

## Milestones

1. [ ] GitHub repo + PAT created (steps 1-2)
2. [ ] GitLab `master` protected, `vault` left unprotected (step 3)
3. [ ] Push mirror configured and saved (step 4)
4. [ ] GitHub branch protection on `master` (step 5)
5. [ ] README mirror notice committed directly to `master` (step 6)
6. [ ] Acceptance run green (commit SHA match + `vault` absence, per
       Test Plan)

## Open Questions / Decisions Needed

None — all resolved during this interview (see "Resolutions carried in
from interview" above).

## SPEC C: CLOSED (2026-08-07)

Owner confirmed Y and executed steps 1-5 (GitHub repo `mikkiola/radar`
created public/empty, fine-grained PAT scoped to that repo with
`Contents: RW`, GitLab `master` protected via Protected branches,
push mirror configured with "Only mirror protected branches", GitHub
branch protection on `master`).

Step 5 required a live correction during execution: GitHub's current
UI is **Rulesets**, not the classic "Add branch protection rule" flow
this SPEC originally assumed from general knowledge. Corrected in
place (see Implementation Steps, step 5) rather than left to cause a
mismatch — actual config used: Ruleset `master`, Enforcement `Active`,
target branches by name pattern `master` (not "default branch" — an
empty repo's default is `main`, which wouldn't match), rules
`Restrict updates` + `Restrict deletions` + `Block force pushes`,
bypass list role `Repository admin` (Rulesets bypass only supports
roles/apps, not individual usernames — the owner holds admin by virtue
of creating the repo, so this covers the mirror's authenticating
account without a per-user option).

README mirror notice (step 6) committed directly to `master`
(`9434826` / full SHA `94348263cbaf99c6a15786e63ddf818315e73147`,
2026-08-07) — no feature branch, per Resolution 8 (below the
SPEC-A-scale threshold for an MR).

**Acceptance Run Result** — real API checks against live state, not
UI/YAML inference, per the project's standing verification rule:

- `curl https://api.github.com/repos/mikkiola/radar/commits/master` →
  `sha: 94348263cbaf99c6a15786e63ddf818315e73147` — **exact match**
  with the commit just pushed to `gitlab.com/lyolich777ka/radar`
  `master`. Mirror sync completed within the ~1-minute window expected
  for protected-branches-only mirrors.
- `curl https://api.github.com/repos/mikkiola/radar/branches` →
  `["master"]` only — **`vault` confirmed absent**, structural
  exclusion via the protected-branches whitelist mechanism holds.

Both checks green. SPEC C closed, no further action needed. GitLab
remains source of truth; GitHub is a live, working read-only mirror.

**Full queue order**: SPEC A → SPEC A.5 → SPEC A.6 → SPEC E → SPEC C.

# SPEC B: Repository Discoverability — Specification

## Overview

Make the repository understandable to an external developer within 30
seconds, by bringing README, badges, and GitHub/GitLab metadata up to
date with the real state of the codebase after SPEC A/A.6/E/C. Not a
generic-template rewrite — SPEC D (separate, later) owns reformulating
the docs as a reusable domain-agnostic pattern. SPEC B describes Radar
as it actually is (an AI/agentic-tooling-market signal detector).

## Audit findings (real, grepped against the repo — 2026-08-07)

1. **README Scripts table**: documents 9 of ~19 files in `src/`. Missing
   entirely: `backfill_frontmatter.py`, `check_frontmatter.py`,
   `check_model_updates.py`, `confirm_candidate.py`,
   `promote_candidates.py`, `recheck_lifecycle.py`, `scorecard.py`,
   `vault_language.py`, `vault_write.py`. Existing entries also lack the
   `src/` path prefix (stale since the SPEC A reorg).
2. **README CI/CD table**: documents 5 of 13 jobs in `.gitlab-ci.yml`.
   Missing: `security_secrets`, `security_deps`, `test`,
   `confirm_candidate`, `promote_candidates`, `recheck_lifecycle`,
   `lint_vault`, `check_models`.
3. **README Environment variables table**: missing `GITHUB_READ_TOKEN`,
   which is real and used in `src/radar_step0.py` and `src/analyze.py`.
4. **No top-level directory tree** anywhere in README — only the
   `vault` branch's internal structure is shown (`Vault structure`
   section). A first-time reader has no map of `src/`, `tests/`,
   `docs/`, `requirements*.txt` at the code-repo level.
5. **No badges** at all.
6. **GitHub topics**: empty (checked via public API,
   `api.github.com/repos/mikkiola/radar`). **GitLab topics**: already
   has 12 well-chosen, pipeline-accurate topics (`agentic-ai`,
   `ai-agents`, `github-actions`, `knowledge-management`, `llm`,
   `market-intelligence`, `open-source`, `python`,
   `research-automation`, `signal-detection`, `technology-radar`,
   `Trend-analysis`) — set prior to this SPEC, not duplicated effort.
7. **Descriptions differ in wording** between GitLab and GitHub (same
   substance, different phrasing — GitHub's was written during SPEC C).
8. **GitHub Releases**: empty. **Social preview image**: unset (GitHub
   shows its default placeholder).
9. Confirmed not in scope for this audit: `radar_step0.py` and
   `filter.py` are not directly CI-invoked — they're imported as
   library modules inside `analyze.py` (`from radar_step0 import ...`,
   `from filter import is_relevant`), which is what the `radar` job
   actually runs. The accurate table entry for them is "helper module
   used by analyze.py", not a standalone scheduled step — noted so the
   rewritten table doesn't just copy the old (inaccurate) framing.

## Resolutions from interview

1. **README Scripts and CI/CD tables: full rewrite**, not a partial
   patch. Grepped fresh against `src/*.py` and `.gitlab-ci.yml` at
   implementation time (not copied from this SPEC's audit snapshot,
   which could drift before implementation lands).
2. **Add a top-level repository structure tree** near the top of
   README, before the existing `## How it works` section. Covers
   `src/`, `tests/`, `docs/`, root config/requirements files — not the
   vault-branch layout (already covered separately).
3. **Badges**: `License: MIT` (static, shields.io, links to `LICENSE`)
   and `Python 3.12` (static, matches `image: python:3.12` in
   `.gitlab-ci.yml`). **No CI pipeline-status badge** — the project has
   no push-triggered job that would keep such a badge meaningfully
   live (daily/weekly schedule-triggered jobs wouldn't move a
   push-pipeline badge), so it would read as more current than it is.
4. **Add `GITHUB_READ_TOKEN`** to the README's Environment variables
   table — real, in-use, was simply omitted.
5. **GitHub topics: copy all 12 from GitLab verbatim.** GitLab's list
   already reflects actual pipeline content, not generic AI buzzwords —
   reuse it rather than re-deriving a second list.
6. **GitHub description: align to the GitLab wording** ("An AI
   ecosystem radar that detects structural shifts in open-source AI by
   analyzing GitHub, Hacker News, and Reddit, then clustering signals
   into long-term patterns."). GitLab treated as the source-of-truth
   phrasing since it already matches the topics list.
7. **Social preview image: deferred**, out of scope for this SPEC.
   Requires a designed image; not core to the routine discoverability
   scope here. GitHub falls back to its neutral default placeholder —
   not broken, just not customized.
8. **GitHub Releases: deferred**, out of scope. No versioned
   functionality or semantic-versioning scheme exists yet — the
   pipeline runs continuously (daily/weekly jobs), not in discrete
   releases. A tag today would carry no real release-notes content.
   Candidate for its own trigger once real versioned functionality
   exists, or for SPEC D.

## Implementation Steps

1. **[ЗАПРОС] Claude Code edits `README.md` directly** (whole-file
   replace is the standing exception for this file per the project's
   write rules): rewrite the Scripts table (all `src/*.py`, fresh grep
   against real files), rewrite the CI/CD table (all jobs in
   `.gitlab-ci.yml`, fresh grep), add `GITHUB_READ_TOKEN` to
   Environment variables, add the two badges under the title, add a
   top-level repository structure tree before `## How it works`. Diff
   shown to the owner before commit. Commit and push directly to
   `master` (below the SPEC-A-scale MR threshold).

2. **[ЗАПРОС] Owner: GitHub → repo Settings → General → Topics.**
   Add all 12: `agentic-ai`, `ai-agents`, `github-actions`,
   `knowledge-management`, `llm`, `market-intelligence`, `open-source`,
   `python`, `research-automation`, `signal-detection`,
   `technology-radar`, `Trend-analysis`. (Claude Code has no GitHub
   token/CLI in this environment — manual UI action.)

3. **[ЗАПРОС] Owner: GitHub → repo Settings → General → Description.**
   Replace with: "An AI ecosystem radar that detects structural shifts
   in open-source AI by analyzing GitHub, Hacker News, and Reddit, then
   clustering signals into long-term patterns."

## Test Plan (Acceptance Run)

1. After step 1's commit is pushed, verify the push-mirror carried it
   to GitHub (per SPEC C's mechanism) via the public GitHub API —
   commit SHA on `github.com/mikkiola/radar` `master` matches the
   commit just pushed to GitLab `master`.
2. After steps 2-3, verify via the public GitHub API
   (`api.github.com/repos/mikkiola/radar`) that `topics` contains all
   12 entries and `description` matches the GitLab wording.
3. Manually re-read the updated README top-to-bottom and confirm: an
   external reader gets what the project does, how it's laid out, and
   what's running in CI, without needing to open `.gitlab-ci.yml` or
   `ls src/` themselves.

## Security Considerations

None — this SPEC touches no secrets, no CI code, no auth. Purely docs
and repo metadata.

## Milestones

1. [ ] README rewritten (Scripts, CI/CD, env vars, badges, structure
       tree) and committed to `master`
2. [ ] GitHub topics synced (step 2)
3. [ ] GitHub description synced (step 3)
4. [ ] Acceptance run green (mirror sync + topics/description API
       check + manual read-through)

## Open Questions / Decisions Needed

None — all resolved during this interview (see "Resolutions from
interview" above).

## SPEC B: CLOSED (2026-08-07)

Owner confirmed Y. Implementation:

- **Step 1** (README rewrite) — Claude Code committed directly to
  `master`, no feature branch (below the SPEC-A-scale MR threshold):
  `7948c9f` / full SHA `7948c9fe2b153a9aad4add5506eb4390b39dd861`.
  Scripts table expanded from 9 to 18 entries (all of `src/*.py`, with
  `src/` path prefix and accurate "helper module vs CI-invoked job"
  framing per the audit finding). CI/CD table expanded from 5 to 13
  jobs, matching `.gitlab-ci.yml` exactly. Added `GITHUB_READ_TOKEN` to
  Environment variables, a top-level repository structure tree, and
  `License: MIT` + `Python 3.12` badges.
- **Steps 2-3** (GitHub topics + description) — owner-executed via
  GitHub UI. Topics were already in place (added prior to this SPEC's
  execution window, consistent with the audit's finding that GitLab's
  topics predate SPEC B). Description updated to the GitLab-aligned
  wording.

**Acceptance Run Result** — real API checks against live state, not
inference, per the project's standing verification rule:

- `curl https://api.github.com/repos/mikkiola/radar/commits/master` →
  `sha: 7948c9fe2b153a9aad4add5506eb4390b39dd861` — **exact match**
  with the README commit pushed to `gitlab.com/lyolich777ka/radar`
  `master`. Push-mirror sync (SPEC C mechanism) confirmed still
  working correctly.
- `curl https://api.github.com/repos/mikkiola/radar` → `description`
  **matches** the GitLab wording exactly; `topics` contains all 12
  entries — GitHub lowercases topic slugs automatically
  (`Trend-analysis` → `trend-analysis`), a platform normalization, not
  a discrepancy against what was entered.
- Manual read-through of the updated README confirmed: project
  purpose, directory layout, script roles, and CI job triggers are all
  now visible without opening `.gitlab-ci.yml` or listing `src/`
  separately.

All three checks green. SPEC B closed, no further action needed.
Social preview and GitHub Releases remain deferred (Resolutions 7-8),
not blockers.

**Full queue order**: SPEC A → SPEC A.5 → SPEC A.6 → SPEC E → SPEC C → SPEC B.
