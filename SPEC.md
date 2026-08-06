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

## Milestones

1. [ ] Create migration branch.
2. [ ] Move zero-dependent/zero-dependency files (step 1).
3. [ ] Move leaf-to-hub files (step 2).
4. [ ] Move remaining `vault_write.py`-dependent files (step 3).
5. [ ] Move `vault_write.py` + `99_System/` (step 4).
6. [ ] Move tests, add `pyproject.toml` + `requirements-dev.txt` (step 5).
7. [ ] Update `.gitlab-ci.yml` (step 6).
8. [ ] Rule 31 acceptance run, all 10 jobs (step 7).
9. [ ] Merge to `master` (step 8).

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
→ SPEC B → SPEC D.

## Open Questions / Decisions Needed

None remaining for SPEC A's design. Implementation-time open item:
verify no other file (outside the grepped `*.py` set) references the
old flat paths — e.g. check `.gitignore` patterns, any shell scripts,
or CI cache keys that assume repo-root-level `.py` files, before
starting the migration branch.
