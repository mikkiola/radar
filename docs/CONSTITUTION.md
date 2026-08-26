# CONSTITUTION — Radar

Immutable rules. Changed only by Olga's explicit decision, never
mid-session. Project source of truth: this file plus
`docs/ARCHITECTURE.md`, `docs/BACKLOG.md`, and `docs/adr/`.

## What this project is

Radar is a measuring instrument for the agentic and AI market, plus the
"Public Radar of an Architect" Telegram channel. Not a news aggregator.
Not a GitHub scraper. A research platform for accumulating, verifying,
and evolving knowledge about structural shifts in the technology
ecosystem, with AI/MCP/LLM as its first domain.

Owner: Olga — engineer/architect. Values: automation, strict order,
zero small talk.

The channel is not built for an audience. `@radar_public` is open, but
not promoted and not a growth target. The goal is a personal measuring
instrument for Olga's own investment/architecture decisions. The
audience kill-metric (reach/subscribers) was struck down as the wrong
metric to begin with — fixed 2026-07-28.

**Updated 2026-08-25 — platform change.** The repository is no longer
on GitLab. Sole repository and source of truth: `github.com/mikkiola/radar`,
public, MIT license. The GitLab repository
(`gitlab.com/lyolich777ka/radar`, previously shown in its UI as "Olga
Stroganova / opensource-radar") was set for deletion 2026-08-25,
physically gone 2026-09-24 (GitLab's 30-day grace period). Reason:
GitLab compute-minute exhaustion with no realistic path to renewal,
plus consolidating repository ownership under the `mikkiola` account
(already owns article-pipeline and tooltempest). Full decision record:
ADR-0013.

Branches: `main` (scripts, renamed from `master` 2026-08-25, GitHub
convention) and `vault` (data, separate git history, moved to GitHub
with full history preserved, SHA confirmed identical on both platforms
before GitLab's deletion). Default branch on GitHub: `main`.

README.md is in English, reflects the current architecture without
exposing internal paths, secrets, or exact cron schedules.

## Design principles

1. Falsifiability First — every conclusion carries a revision
   criterion. The system stores checkable claims, not opinions.
2. Knowledge Before Automation — automation appears only after a
   stable knowledge structure exists, not because it seems useful.
3. Storage Is Cheap, Context Is Expensive — store almost everything;
   send an LLM the minimum active context.
4. Analysts Are Hypotheses — no external analyst is an authority. An
   analyst's weight is set by track record, not assigned by hand.
5. Agents Are Replaceable — the architecture doesn't depend on any
   specific model or provider.
6. Graceful Degradation — one component failing doesn't stop the whole
   system.
7. Internal English, External Russian — data for the AI is in English,
   the interface for the human is in Russian. Full decision and
   resolved forks: ADR-0001.
8. Feedback-Driven Evolution — new functionality appears only after
   accumulated feedback with an observed cause, never by assumption.
9. Knowledge Is More Valuable Than Code — code can be rewritten,
   observation history can't. Protection priority: Knowledge, Metadata,
   Infrastructure, Code.

## Content selection criterion for the channel

Does this carry a SHIFT? A shift is a change in how knowledge or value
is organized in the ecosystem, caught before it becomes common
knowledge.

Passes: a new ecosystem behavior pattern, a change in who knowledge is
addressed to, a change in decision-making structure, a shift in what
becomes infrastructure. Doesn't pass: product news, a release
feature rundown, "an interesting tool," this week's popular topic.

## Channel voice

Olga writes in first person: direct, no preamble, no explanations for
a broad audience, no CTA, no emoji markers. Length 300-800 characters.
Always in Russian, regardless of the input data's language.

## Boundaries of what the executor (me / agents) can do

Cowork doesn't execute code and has no direct GitHub connector for
repository operations in this sense — git operations are performed
manually by the owner, via the GitHub web UI or via Claude Code.

In Google Drive, the agent can only create and copy, not move/delete.
Deletion and moving are the user's own actions. Direct editing of an
existing Google Doc, without an overwrite tool, isn't available —
updating canonical documents when no write tool exists for that
specific file is done manually by the owner: the agent prepares the
full text of the new document, the owner decides whether to replace the
old one with it.

The agent instruction document (AGENT_INSTRUCTION) is a Project
Knowledge entity, not a file in the repository.

Actions on protected branches and Rulesets on GitHub that require the
web UI aren't available from the terminal/Claude Code programmatically
in general. Claude Code's auto-mode classifier blocks `git remote add`
and `git push` even with the owner's explicit confirmation in some
sessions — in those cases the command is run manually by the owner in a
regular terminal.

Claude Code can confuse remotes when several are configured in one
local clone (found 2026-08-25). Observed case: the local Radar clone
had `origin` (GitLab) and `github` (GitHub) configured at once; several
`git push origin main` commands in a row went to GitLab, not GitHub,
even though the session's goal was moving to GitHub — found only
through a direct `git remote -v` check and SHA comparison on both
platforms. Rule: name the remote explicitly in every push/pull command
when working with multiple remotes; periodically re-check
`git remote -v` at the first sign of a mismatch.

Project Knowledge on claude.ai can lag behind the current version of a
document in Google Drive — don't rely on `project_knowledge_search` as
the sole source when updating canonical documents.

## What can't be touched by hand, architectural invariants

Radar's vault (data, `vault` branch) and scripts (`main` branch) — one
repository (`github.com/mikkiola/radar`), two branches, both on GitHub
as of 2026-08-25.

`model_config.json` (path `src/99_System/model_config.json`) — the
single source for model IDs. Never hardcode a model ID in a script.

`model_config.json` is only ever updated by hand, after a smoke test
and a breaking-changes check.

The `Модель:` / `Промпт версия:` block belongs only in `02_Patterns/`.
Never add it to `telegram_post.py`.

Assessment and pattern files are never overwritten wholesale — targeted
edits only, `os.path.exists(filepath)` before any write.

"Human Edit" (`## Правка человека`) is the only place a disagreement
with Claude's assessment can be recorded.

Vault language contract: headings follow the body's own language;
`Метка:`-fields (`Оценка`, `Статус`, `Вердикт`, `Уверенность`) are
always in Russian — this is a machine-readable protocol. Full decision:
ADR-0001.

The `master` branch was deleted on both platforms 2026-08-25 (renamed
to `main` with full history preserved, the old `master` branch deleted
after confirmed parity). The repository's only branches are `main` and
`vault`.

`SPEC.md` stays in the repository as documentation, never deleted after
a commit. The rule of verifying `SPEC.md` against the real code before
implementation stays in force.

The single source of an assessment's status is YAML frontmatter. The
`status` field in every `01_Assessments/` file's frontmatter is the
single source of truth. `status` is only ever written through
`write_verdict_entry()` in `vault_write.py`.

The frontmatter invariant is mechanically enforced: a preventive
full-scan gate (`check_frontmatter.py`) at the end of every job that
writes to `vault`, plus the detective `lint_vault` job.

## CI/CD and secrets, updated 2026-08-25, full platform change

GitLab CI is fully removed (`.gitlab-ci.yml` deleted from the
repository 2026-08-25, commit `fd6e8b4`). All automation now runs
through GitHub Actions — 9 workflow files in `.github/workflows/` plus
1 composite action (`vault-write`, encapsulating the clone-vault /
run-script / commit+push pattern, reused by 7 jobs instead of being
duplicated in each file).

Structure: `security.yml` (`security_secrets`, `security_deps`),
`test.yml` (`test`), `daily-run.yml` (`radar`, `promote_candidates`,
`recheck_lifecycle` manual), `monthly-lifecycle.yml` (`recheck_lifecycle`
scheduled), `weekly-patterns.yml` (`analysts`, `check_models`,
`patterns` — `patterns` depends on `analysts` and `check_models` via
`needs`), `publish.yml` (`publish`, twice daily), `lint-vault.yml`
(`lint_vault`), `confirm-candidate.yml` (`confirm_candidate`, manual
with inputs), `pages.yml` (`build` plus `deploy` to GitHub Pages).

Schedules were converted from Asia/Bangkok to UTC — a fixed −7 hour
shift recalculation. GitHub Actions cron doesn't guarantee to-the-minute
accuracy.

All 6 secrets were rebuilt from scratch 2026-08-25, not migrated from
GitLab. Reason: the old values turned out to be accidentally exposed in
plaintext through GitLab's `/variables` API endpoint — `masked: true`
only protects CI-log output, not the API response itself for an
authorized caller with sufficient scope.

Current secrets, in GitHub Actions Settings → Secrets and variables →
Actions: `ANTHROPIC_API_KEY` (separate from the Brain project's key,
`radar-github-actions`), `GH_READ_TOKEN` (fine-grained PAT, public
repositories read-only access, verified by reading `radar_step0.py`
line by line — only 4 GET calls, not a single write), `GH_VAULT_PUSH_TOKEN`
(fine-grained PAT, `mikkiola/radar` only, Contents Read/write),
`TELEGRAM_BOT_TOKEN` (new token, `@radar_architect_bot`),
`TELEGRAM_CHANNEL_ID` (`@radar_public`, not really a secret),
`TELEGRAM_OWNER_ID` (`227280271`, not really a secret).

GitHub Actions secret naming rule: a name can't start with `GITHUB_` —
reserved by the platform.

The choice between the built-in `GITHUB_TOKEN` and a PAT secret for
writing to `vault` was resolved in favor of a PAT. Reason: `pages.yml`
must react to a push to both `main` and `vault`, and commits made via
the built-in `GITHUB_TOKEN` deliberately don't cascade further workflow
events.

GitHub Pages: Settings → Pages → Source = GitHub Actions. URL:
`https://mikkiola.github.io/radar/`.

## Data and security rules

API keys are never stored in markdown, the git repository, logs, or
publications — only through CI/Actions secrets.

Every external service gets its own dedicated access key. Reusing keys
between projects (specifically between Radar and Brain) or between
different purposes within one project is forbidden.

New rule, 2026-08-25: an API endpoint that returns full configuration
data may not respect a `masked`/`protected` flag in the response
itself. Before using any new diagnostic API endpoint capable of
returning secret values, check its documentation for exactly what it
hides.

An API key is passed to the child process, not the session — when
testing code, pass the key as an inline prefix to the specific command.

## Hard output and code-work rules

1. Always check the real path before writing.
2. Mark hypotheses with the tag ГИПОТЕЗА (HYPOTHESIS), verified facts
   with ФАКТ (FACT).
3. Output for the human is in Russian. Vault data for the LLM is in
   English, service `Метка:`-fields stay Russian literals (ADR-0001).
4. Declare Python functions before the `if __name__ == "__main__"`
   block.
5. Never overwrite existing assessment and pattern files.
6. `python3 -m py_compile` after every change, before push. Equivalent
   for YAML CI files, as of 2026-08-25: `python3 -c` with
   `yaml.safe_load` — mandatory before committing a workflow file.
7. No em dashes or en dashes inside Python strings, hyphen only.
8. Don't mark CI variables Protected if the branches aren't protected.
9. Never run `git remote set-url` without explicitly naming the
   folder. Added 2026-08-25: the same applies to `git remote add` when
   working with multiple remotes.
10. Targeted edits, never rewrite files wholesale. Exception:
    README.md and LICENSE.
11. Ask what already exists before proposing to create something new.
12. `max_tokens` for clustering 20+ files, minimum 5200.
13. `thinking` type `disabled` in every programmatic Sonnet call. Never
    set `temperature`/`top_p`/`top_k`.
14. `sed` on macOS only with an explicit empty argument.
15. A gitlink with no `.gitmodules` is diagnosed via `git ls-files`.
16. A CI config is a file, not a set of terminal commands.
17. Cowork doesn't execute code and has no full access to the
    repository's git operations.
18. Risk asymmetry as the criterion for routine configuration
    decisions.
19. An external brainstorm is not a falsifiable source by default.
20. Data that contradicts the rest of the context isn't trusted without
    direct verification.
21. Rule: read the calendar at the start of a new session.
22. Rule: build-vs-reuse check before writing a component from scratch.
23. Double incident closure — Operational and Root Cause statuses
    tracked separately.
24. Git diagnosis must start with `git fetch` and `git status`. Added
    2026-08-25: with multiple remotes, fetch and check each remote
    separately.
25. Grill Me and Dual Review fully removed, replaced by the `spec`
    skill (ADR-0002).
26. The gap between Project Knowledge and the repository was decided
    not to be closed.
27. The `spec` skill is only invoked explicitly by the owner, via
    slash command (ADR-0002).
28. Verify `SPEC.md` against the real code before implementation.
29. Record an experiment result's epistemic status explicitly.
30. Check production cron for race risk during multi-hour sessions
    touching `vault` — applies to GitHub Actions schedules too.
31. A real acceptance run in CI before closing any phase touching CI
    configuration. Confirmed 2026-08-25: static YAML validation is
    necessary but not sufficient.
32. New, 2026-08-25: with multiple git remotes, name the remote
    explicitly in every command; periodically diff branches for
    symmetry.
33. New, 2026-08-25: on discovering a secret leaked through an API,
    rotation must cover every secret reachable through that same call.

## Mandatory parameters for Sonnet 5 in programmatic calls

`client.messages.create` with `model` = `MODEL_CONFIG.sonnet`,
`thinking` type `disabled`, `max_tokens`, `messages`. Never set
`temperature`/`top_p`/`top_k`.

## Non-goals

Radar is not: an autonomous AI agent, a trading system, a
recommendation system, a content generator, an infrastructure
logging/monitoring system, a marketing/growth tool for the channel.

## Threat model, briefly

Open data sources, no user data, no financial operations. Main
threats: loss of knowledge, token compromise, data corruption,
uncontrolled spend, degraded output quality, prompt injection through
external sources.

New threat, 2026-08-25: secret exposure through a platform's own
diagnostic API endpoints, outside the project's code control.

Budget Protection: `STOP_PIPELINE` if a spending limit is exceeded.

Model/Auth Protection, categorical rule: a Claude Code session only
works through Sonnet under the existing subscription. Switching to
Opus, Fable, Mythos, or a direct `ANTHROPIC_API_KEY` is categorically
forbidden. Before starting any session that touches code — explicit
confirmation of the model and the auth method.

Scope clarification: this ban applies to what runs the session itself
— not to scripts inside the Radar repository that use their own
`ANTHROPIC_API_KEY`.

## RELEASE rule

Storage: a separate file per session, Google Drive, Radar folder,
named `RELEASE_<date>`.

Trigger: on the explicit command "write a release."

## Process-artifact rule

`PLAN.md` and similar files are never archived — deleted after a
successful commit. `SPEC.md` stays in the repository permanently.

## Olga's userPreferences

Output language: Russian. Format: dry facts, bullet lists, code, no
preamble. Files are read-only by default; any Write/Delete/Move only on
explicit request. Routine work — one decision. Architecture — 2-3
options in a table. Uncertainty — one clarifying question.

## Verify-before-execute rule

Trigger: the task touches something that can't be checked after the
fact by simply reading the result.

Rule: interview through the `spec` skill, only on the owner's explicit
call, then line-by-line verification against the real code, then a
full diff before commit/push with explicit confirmation.

## Rule: critical review of external opinions

Not falsifiable by default unless at least one participant has actually
rejected the hypothesis at some point.

---

Version: reflects the 2026-08-25 revision (full platform migration:
repository, CI/CD, all secrets, GitHub Pages; `master` renamed to `main`
with history preserved on both platforms before GitLab's deletion;
GitLab repository set for 30-day deletion; new rules 32-33 on multiple
remotes and full rotation on a leak; new threat-model entry on
diagnostic API endpoints; CI/CD and secrets section rewritten fully for
GitHub Actions). Source: session 2026-08-25 (CONSTITUTION_r v2.3),
DocOps-merge deferred to a later session at that time, now underway as
of this commit — cross-referenced against ADR-0001 through ADR-0014.

## ToolTempest consumer obligation

Applies to any project that consumes ToolTempest (`mikkiola/tooltempest`),
not only this repository — expected to be copied, verbatim or
near-verbatim, into any other ToolTempest consumer's own Constitution.
ToolTempest has no Constitution of its own to hold this rule.

Whenever a session works on ToolTempest itself (not this consumer
project) and adds, removes, or renames a file under `scripts/`,
`schemas/`, `skills/`, or `rules/` — the four directories ToolTempest's
own `MANIFEST.txt` tracks — that session must run ToolTempest's
completeness-check script (`scripts/check_manifest.py`) before
considering the change done, and update `MANIFEST.txt` in the same
commit if it reports a mismatch, not as a separate later task.

This is also the natural trigger point for the owner to consider
repinning `.tooltempest.lock` in this repo (or any other consumer) to
pick up the new file — that repin remains a deliberate, separate
action, not automatic.
