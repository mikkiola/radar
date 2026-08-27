# Radar — Architecture

State as of 2026-08-26. Every fact is a table cell — no prose
sections. Rationale for any decision: `docs/adr/`. Plan:
`docs/ROADMAP.md`. Tasks: `docs/BACKLOG.md`. This document does not
duplicate what those three own — it states current state and
dependencies only.

| Component | Status | Depends on | Validation | Commit |
|---|---|---|---|---|
| Collection & filtering (`radar_step0.py`, `filter.py`, `scorecard.py`) | Implemented | — (entry point; external sources: GitHub, HN, Reddit, AwesomeLists) | Running in production via `daily-run.yml`; `scorecard.py`'s OpenSSF Scorecard lookup is a third-party signal, not self-report | `1a6ed8c` (`radar_step0.py`, `scorecard.py`), `2908007` (`filter.py`) |
| Assessment (`analyze.py`) | Implemented | Collection & filtering | `compute_status()` (`src/analyze.py:211`) computes verdict from structured model output (`novelty_score`, `cross_validation_confirmed`, `novelty_checklist_passes`) in code, never from the model's self-report; below `novelty_score` 4 no file is written at all (NOISE). `state_value` lifecycle axis tracked as a separate field, independent of this maturity snapshot | `4818962` |
| Quarantine resolution (`promote_candidates.py`, `confirm_candidate.py`) | Implemented | Assessment | `apply_quarantine_gate()` (`src/analyze.py:222`) routes every fresh `VALIDATED_SHIFT` to `CANDIDATE` first, never publishes it directly. `promote_candidates.py` re-checks repo aliveness after `QUARANTINE_DAYS = 14` before promoting to `VALIDATED_SHIFT` (drops to `REJECTED_NOISE` if the repo went dark; retries on the next run if the aliveness check itself fails, never silently promoted). `confirm_candidate.py` requires an explicit human approve/reject for `CANDIDATE_LOW_CONFIDENCE` — time alone never resolves that state | `4818962` |
| Lifecycle recheck (`recheck_lifecycle.py`) | Implemented — known race condition, unaddressed (see docs/BACKLOG.md [B-009]) | Assessment | Re-checks already-`VALIDATED_SHIFT` entries for staleness: `FROZEN_MONTHS = 6` (no repo activity), `RELEASES_STOPPED_MONTHS = 12` (no releases) | `4818962` |
| Pattern clustering & falsification (`patterns.py`) | Implemented | Assessment, External analyst input | `should_falsify()` / `falsify_pattern()` / `run_falsification()` (`src/patterns.py:667/690/777`) re-examine existing patterns on every weekly run, not only new assessments | `4818962` |
| External analyst input (`fetch_analysts.py`) | Implemented | — (independent second input) | Runs in `weekly-patterns.yml`; feeds `patterns.py` as a second, independent input alongside internal assessments | `4818962` |
| Model-update feedback check (`check_model_updates.py`) | Implemented — first step only of the planned Feedback layer | — | Runs in `weekly-patterns.yml` | `4818962` |
| Publishing (`telegram_post.py`) | Implemented | Pattern clustering & falsification, Quarantine resolution | Posts confirmed patterns to the Telegram channel; human-facing output stays Russian by design | `fd6e8b4` |
| Vault write mechanism (`vault_write.py`, `vault_language.py`, `check_frontmatter.py`) | Implemented | — | Used by 7 of the 9 CI workflows via the `vault-write` composite action; `check_frontmatter.py` runs as a gate before every vault push. All scripts resolve vault paths through one shared `VAULT_ROOT` variable, not per-script path construction | `1a6ed8c` |
| Frontmatter maintenance (`backfill_frontmatter.py`, `update_assessments.py`) | Implemented — `update_assessments.py` shares the race condition noted in Lifecycle recheck above (see docs/BACKLOG.md [B-009]) | Vault write mechanism | `backfill_frontmatter.py` is a one-off/on-demand utility | `4818962` |
| Site generation (`generate_graph.py`, `generate_indexes.py`) | Implemented | Vault write mechanism | `generate_graph.py` writes `docs/assets/javascripts/graph.json` (via `DOCS_DIR`, matching `mkdocs.yml`'s `docs_dir`); output confirmed present in the one successful GitHub Pages build | `1a6ed8c` |
| CI/CD (9 GitHub Actions workflow files + `vault-write` composite action) | Implemented — 6 of 9 workflows confirmed running by trigger; `weekly-patterns.yml`/`monthly-lifecycle.yml` await their next scheduled occurrence, `confirm-candidate.yml` is manual-dispatch-only by design (see docs/BACKLOG.md [B-003]) | Collection & filtering, Assessment, Quarantine resolution, Lifecycle recheck, Pattern clustering & falsification, External analyst input, Model-update feedback check, Publishing, Vault write mechanism, Site generation | `test.yml`/`pages.yml` confirmed running (push-triggered); `daily-run.yml`/`publish.yml`/`security.yml`/`lint-vault.yml` confirmed running on their cron schedules as of 2026-08-27. All 6 secrets (`ANTHROPIC_API_KEY`, `GH_READ_TOKEN`, `GH_VAULT_PUSH_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID`, `TELEGRAM_OWNER_ID`) rebuilt fresh in GitHub Actions Secrets, none copied from the former GitLab CI/CD Variables. GitHub Actions runners use `python:3.12` via `actions/setup-python` | `fd6e8b4`, `60ddb1c` (GH_READ_TOKEN auth fix) |
| GitHub Pages | Implemented — interactive graph broken (see Validation) | Site generation, CI/CD | One successful `pages.yml` run confirmed (2026-08-25T13:23:40Z, build and deploy both succeeded); site substantively works — home page and Patterns/Assessments sections render, all 14 migrated patterns display correctly. Known defect: interactive graph doesn't render, 404 on `graph.json` — see docs/BACKLOG.md [B-001] | `fd6e8b4` |
| Platform: GitHub repo hosting (`github.com/mikkiola/radar`) | Implemented | — | Full SHA parity confirmed between GitLab and GitHub for both `main` and `vault` before GitLab deletion; `vault` moved as a full branch with complete history (1879 objects), SHA `39286a667923f64418b08942df926f6ca23571c3` confirmed identical on both platforms pre-deletion. `main` is protected (Maintainers push/merge, no force push); `vault` is not — see docs/BACKLOG.md [B-002] | `fd6e8b4` (`.gitlab-ci.yml` removal, workflow files added); branch rename/protection/ruleset changes are not commit-tracked |
| Domain-configuration layer (per-domain filter keywords/prompts) | Not started | Collection & filtering, Assessment | — | — |
| Forecasts (Layer 4) | Not started | Pattern clustering & falsification, External analyst input | — | — |
| Decisions | Not started | Forecasts | — | — |
| Outcomes | Not started | Decisions | — | — |
| Observability (gated layer) | Not started — waits on an explicit trigger from data (see docs/BACKLOG.md [B-010]) | — | — | — |
| Trust & Security (gated layer) | Not started — waits on an explicit trigger from data (see docs/BACKLOG.md [B-011]) | — | — | — |
| Optimization & Evolution (gated layer) | Not started — waits on an explicit trigger from data (see docs/BACKLOG.md [B-012]) | — | — | — |

## Repositories

| Repo | Contains |
|---|---|
| `github.com/mikkiola/radar` (`main` branch) | Pipeline scripts (`src/`), CI/CD workflows, documentation |
| `github.com/mikkiola/radar` (`vault` branch) | Data: assessments, patterns, generated site |

## Models used by this project

| Component | Model or service |
|---|---|
| Assessment (`analyze.py`) | Anthropic Haiku |
| External analyst input (`fetch_analysts.py`) | Anthropic Haiku |
| Pattern clustering & falsification (`patterns.py`) | Anthropic Sonnet |
| Publishing (`telegram_post.py`) | Anthropic Sonnet, Telegram Bot API |
| CI/CD, Platform | GitHub API |
| Collection & filtering (`scorecard.py`) | OpenSSF Scorecard API |
