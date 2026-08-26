# BACKLOG — Radar

Rewritten wholesale on each revision. Decision history lives in
`git log` and `docs/adr/`, not a separate changelog file.

## Closed this revision (2026-08-25)

**Full platform migration, GitLab → GitHub — closed in full.** Not
planned in advance as a separate task — arose mid-session from a
"migrate and delete GitLab" decision, triggered by GitLab compute-minute
exhaustion. Decision and consequences: ADR-0013. `vault` branch
public/private decision, open since 2026-08-07: ADR-0014.

Facts not already covered by ADR-0013/ADR-0014:
- `.gitlab-ci.yml` deleted from the repository entirely (see
  `docs/ARCHITECTURE.md`'s CI/CD section, commit `fd6e8b4`); all GitLab
  mentions in README/mkdocs.yml/telegram_post.py replaced with their
  GitHub equivalents.
- GitLab repository sent to deletion (30-day grace period, physical
  deletion 2026-09-24); GitLab personal access tokens `mirror-check-temp`
  and `radar` revoked. `brain-ci` deliberately left untouched — belongs
  to a different project.
- `TELEGRAM_BOT_TOKEN` was rotated through BotFather as part of the
  secrets rebuild (see `docs/ARCHITECTURE.md`/`docs/CONSTITUTION.md`
  for the full secrets list — this is the one mechanism detail neither
  of those carries).
- Acceptance: full SHA parity between GitLab and GitHub confirmed for
  both `main` and `vault` before GitLab deletion (identical hashes on
  both branches). First and, at the time, only real GitHub Actions run
  (`pages.yml`) — success, site substantively working.

Not closed within this same migration — see New, Open below.

---

**Previously closed items, unchanged this revision:** SPEC C (ADR-0011,
Superseded by ADR-0013), SPEC E (ADR-0010), SPEC D (ADR-0012) — closed
2026-08-07, full detail in each ADR and in `git log`. Their specific
technical content became moot alongside GitLab's deletion, but the fact
that they were correctly implemented and documented at the time they
closed still stands — that's history, not current state.

SPEC B (Repository Discoverability), closed 2026-08-07 — the README
audit that found and fixed the Scripts-table/CI-table drift and the
missing `GITHUB_READ_TOKEN` mention. No dedicated ADR was written for
this decision among the 14 added this session; it remains documented
only in `git log` and the (now superseded-in-parts) session history.

## Next queue

**DocOps/tooltempest-merge.** The session's original goal — bringing
Radar to the same DocOps standard as article-pipeline/tooltempest
(`docs/{ARCHITECTURE,ROADMAP,BACKLOG,CONSTITUTION}.md`, `docs/adr/`,
`.tooltempest.lock`, git hooks, `scripts/verify.py`) — was deferred in
the 2026-08-25 revision in favor of the more urgent infrastructure
migration (GitLab compute exhaustion). *Note: as of this commit, the
`docs/adr/` and `docs/{ARCHITECTURE,ROADMAP,BACKLOG,CONSTITUTION}.md`
portions of this item are now underway — this file is itself one of
that work's deliverables. `.tooltempest.lock`, git hooks, and
`scripts/verify.py` are not yet done.* Recon for this item was partially
done at the start of the 2026-08-25 session (article-pipeline/tooltempest
structure read; ADR-0032 "Drift Warning" confirmed to physically live in
article-pipeline, not tooltempest; tooltempest had exactly one real
consumer at recon time) — worth partially repeating given how much
changed (GitHub instead of GitLab, new CI system); don't rely on the
pre-migration snapshot.

## New, open

**Interactive graph doesn't render on GitHub Pages (404 on
graph.json).** Found at the end of the session, not fixed. Full
investigation and current best hypothesis: `docs/ARCHITECTURE.md`'s
"GitHub Pages" section. Needs its own diagnosis — likely another real
`pages.yml` run (e.g. push any trivial change) to be fully sure this was
a timing artifact and not a hidden problem.

**`vault` branch protection is not configured on the GitHub side.**
On GitLab, `vault` was protected purely as a technical prerequisite for
the push-mirror filter (only protected branches get mirrored) — that
reason disappeared with the full migration. Whether `vault` needs some
protection on GitHub independent of the old reason (e.g. so the CI token
can't accidentally overwrite something outside the normal pipeline) has
not been explicitly considered. This is also ADR-0014's own stated open
item.

**GitHub Actions schedule accuracy hasn't been confirmed by real runs.**
Besides `pages.yml` (fired on push) and `test.yml` (fired on push), the
other 7 workflow files depend on cron schedules that had not fired even
once as of session end — first real confirmation only arrives when each
one's nearest scheduled time is reached (e.g. `daily-run.yml` at 22:00
UTC). The CI migration can only be considered fully verified after each
one's first real run, not immediately after the files were created.

**Leftover empty directory `gitlab.com/lyolich777ka/` at the repository
root** — found 2026-08-06, relevance after the platform change not
explicitly re-assessed (it may have been specific to GitLab's on-disk
path structure, or may not be).

**Prompt injection risk in `analyze.py`/`patterns.py`/`fetch_analysts.py`
— open risk, unmitigated.** Untrusted repository content (README text,
descriptions, external analyst content) reaches LLM prompts in these
three scripts with no isolation or sanitization step. Not previously
tracked as its own BACKLOG item — surfaced during this session's
history review. `docs/CONSTITUTION.md`'s threat model already names
"prompt injection through external sources" generically; this is the
concrete, unmitigated instance of it.

## Out of queue, waiting on a trigger

(Unchanged from the previous revision, except the `vault` decision
above.)

- less-tokens / README-fetch+llm-tldr — deferred; the content this was
  meant to compress doesn't exist in the pipeline yet.
- Phase 3b (transition matrix, Temporal Consistency Validator) —
  deliberately not started, event-triggered.
- Timeout unification — undecided, unchanged.
- GitHub API retry logic — undecided, unchanged.
- `update_assessments.py`/`recheck_lifecycle.py` race condition on the
  shared `vault` file — not addressed.
- Observability / Trust & Security / Optimization & Evolution (gated
  layers) — not started, waiting on an explicit trigger from data.

## Rejected

(Unchanged from the previous revision.)

- llm-tldr, Article Engine, `repo.pushed_at` as a freshness proxy, a
  full FSM for `check_repo_alive()`, reusing `check_repo_alive()`
  literally inside `recheck_lifecycle.py`, Radar 2.0 Phase 3 item 4
  (fastembed+HDBSCAN), abstracting the code for a configurable domain
  for SPEC D's sake, restoring a Telegram notification for new
  `VALIDATED_SHIFT` entries, GitLab MR as the standard process for every
  task, full isolation of SPEC E's acceptance run, duplicating the
  GitHub PAT into GitLab CI/CD Variables (fully moot after GitLab's
  deletion), a CI job/Telegram notification for mirror-sync failure
  (moot), a GitLab CI pipeline status badge in README (moot), a separate
  GitHub Release when SPEC B closed, detailing unimplemented layers in
  `docs/ARCHITECTURE.md`'s Roadmap section.

**New rejection (2026-08-25): the built-in `GITHUB_TOKEN` instead of a
dedicated PAT for writing to `vault`.** Technically simpler (no separate
secret needed), but doesn't let `pages.yml` react to a push
automatically — GitHub's anti-loop protection doesn't cascade events
from the system token, which would have required workflow_run/
repository_dispatch plumbing instead of a plain `on: push`. Rejected in
favor of a PAT with one clear job.

**New rejection (2026-08-25): identity federation (WIF) instead of a
static `ANTHROPIC_API_KEY`.** A real, official Anthropic feature, but it
requires implementing token-exchange logic (RFC 7523 JWT-bearer) by hand
in every pipeline Python script — Radar uses the bare Anthropic SDK in
hand-written scripts, not the ready-made `anthropics/claude-code-action`
where WIF is already built in. Rejected as disproportionate to this
session's scope; recorded here as a future technical option, not a
substantively rejected idea.

---

Version: reflects the 2026-08-25 revision (full GitLab→GitHub platform
migration closed in full; `vault` public/private decision closed by
explicit "publish it" decision; DocOps/tooltempest-merge deferred from
that session, now underway as of this commit; three new open items —
graph on Pages, `vault` protection on GitHub, schedules unconfirmed by
real runs — plus a fourth, prompt injection, surfaced during this
session's history review; two new rejected decisions — `GITHUB_TOKEN`
and WIF). Source: session 2026-08-25 (BACKLOG_r v4.0), merged with this
session's own history review and ADR-0001 through ADR-0014.
