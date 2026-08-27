# Radar — Backlog

Two kinds of entries, kept separate: **Tasks** (a session can execute
these directly) and **Owner decisions needed** (only the project owner
can resolve these — a session should not guess a value or proceed past
one without an answer). Not a history log — see `docs/adr/` and `git
log` for decided/completed things.

P0 = blocks other work. P1 = should do soon. P2 = someday, not urgent.
P3 = speculative or purely conditional on an external trigger (data
accumulation, a scheduled event, a future need) — lower urgency than
"someday," not currently actionable at all. Priority applies within
each section separately.

Every entry carries a stable `[B-NNN]` ID, assigned once in file order
(top to bottom) and never reused or renumbered. One flat sequence
covers both **Tasks** and **Owner decisions needed** — not two separate
counters — since both live in this one file and a single namespace
keeps cross-references unambiguous. Radar has no local ADR-citation
pre-push gate (unlike article-pipeline's DocOps tooling) — there's no
citation-format rule for this ID scheme to be exempt from; it works the
same way regardless.

## Closed this revision (2026-08-25 / 2026-08-26)

**Full platform migration, GitLab → GitHub — closed in full.** Not
planned in advance as a separate task — arose mid-session (2026-08-25)
from a "migrate and delete GitLab" decision, triggered by GitLab
compute-minute exhaustion. Decision and consequences: ADR-0013. `vault`
branch public/private decision, open since 2026-08-07: ADR-0014.

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

**Previously closed items, unchanged this revision:** SPEC C (ADR-0011,
Superseded by ADR-0013), SPEC E (ADR-0010), SPEC D (ADR-0012) — closed
2026-08-07, full detail in each ADR and in `git log`. Their specific
technical content became moot alongside GitLab's deletion, but the fact
that they were correctly implemented and documented at the time they
closed still stands — that's history, not current state.

SPEC B (Repository Discoverability), closed 2026-08-07 — the README
audit that found and fixed the Scripts-table/CI-table drift and the
missing `GITHUB_READ_TOKEN` mention. No dedicated ADR was written for
this decision; it remains documented only in `git log`.

**DocOps/tooltempest-merge — the bulk of this item is now done.**
Originally deferred whole on 2026-08-25 in favor of the GitLab→GitHub
migration; resumed and largely completed 2026-08-26. Landed: 14 ADRs
(commit `f29367e`), `docs/{ARCHITECTURE,ROADMAP,BACKLOG,CONSTITUTION}.md`
+ `docs/adr/ADR-INDEX.md` + generator script, root `ARCHITECTURE.md`
removed and README.md's reference updated (commit `1726443`),
`.tooltempest.lock` pinned plus local pre-commit/pre-push hooks
installed (commit `467955a`), `SPEC.md` trimmed to idle state plus
`scripts/verify.py` added (commit `ab2d36d`), README's root tree
diagram corrected (commit `fb10dea`). Remaining piece tracked
separately below: [B-013].

## Rejected

**From the 2026-08-25 revision:** llm-tldr, Article Engine,
`repo.pushed_at` as a freshness proxy, a full FSM for
`check_repo_alive()`, reusing `check_repo_alive()` literally inside
`recheck_lifecycle.py`, Radar 2.0 Phase 3 item 4 (fastembed+HDBSCAN),
abstracting the code for a configurable domain for SPEC D's sake,
restoring a Telegram notification for new `VALIDATED_SHIFT` entries,
GitLab MR as the standard process for every task, full isolation of
SPEC E's acceptance run, duplicating the GitHub PAT into GitLab CI/CD
Variables (fully moot after GitLab's deletion), a CI job/Telegram
notification for mirror-sync failure (moot), a GitLab CI pipeline
status badge in README (moot), a separate GitHub Release when SPEC B
closed, detailing unimplemented layers in `docs/ARCHITECTURE.md`'s
Roadmap section.

**The built-in `GITHUB_TOKEN` instead of a dedicated PAT for writing to
`vault`** (2026-08-25). Technically simpler (no separate secret
needed), but doesn't let `pages.yml` react to a push automatically —
GitHub's anti-loop protection doesn't cascade events from the system
token, which would have required workflow_run/repository_dispatch
plumbing instead of a plain `on: push`. Rejected in favor of a PAT with
one clear job.

**Identity federation (WIF) instead of a static `ANTHROPIC_API_KEY`**
(2026-08-25). A real, official Anthropic feature, but it requires
implementing token-exchange logic (RFC 7523 JWT-bearer) by hand in
every pipeline Python script — Radar uses the bare Anthropic SDK in
hand-written scripts, not the ready-made `anthropics/claude-code-action`
where WIF is already built in. Rejected as disproportionate to that
session's scope; recorded here as a future technical option, not a
substantively rejected idea.

## Tasks

### P1

#### [B-001] P1 — Interactive graph doesn't render on GitHub Pages (404 on graph.json)

Found: 2026-08-25, end of the GitLab→GitHub migration session.

Browser console shows a 404 on `assets/javascripts/graph.json`,
followed by a JSON parse error (server returns the 404 HTML page
instead). Line-by-line check found no path mismatch between
`src/generate_graph.py`'s write path and
`docs/assets/javascripts/interactive_graph.js`'s fetch path — both
resolve to the same file in the built site. Full write-up and current
best hypothesis (the 404 was observed before the one successful deploy
finished, at a moment `.github/workflows/` didn't yet exist on GitHub
due to a confused-remotes issue) in `docs/ARCHITECTURE.md`'s "GitHub
Pages" section — that hypothesis was not confirmed by a repeat check
within that session.

- [ ] Trigger a fresh, unambiguous `pages.yml` run (push any trivial
      change) and check the live graph with a hard browser cache clear
      afterward, to settle whether this was a timing artifact or a
      real, persisting problem.

**Source.** `docs/ARCHITECTURE.md`'s GitHub Pages section, session
2026-08-25.

#### [B-004] P1 — Unmitigated prompt injection risk in analyze.py/patterns.py/fetch_analysts.py

Found: 2026-08-26, this session's history review.

Untrusted repository content (README text, descriptions, external
analyst content) reaches LLM prompts in these three scripts with no
isolation or sanitization step. `docs/CONSTITUTION.md`'s threat model
already names "prompt injection through external sources" generically;
this is the concrete, unmitigated instance of it — not previously
tracked as its own backlog item.

- [ ] Design and implement an isolation/sanitization step for external
      content before it reaches a prompt in these three scripts, or
      make an explicit, recorded decision that the current risk is
      acceptable and why.

**Source.** Session 2026-08-26, history review.

### P2

#### [B-009] P2 — update_assessments.py/recheck_lifecycle.py race condition on the shared vault file

Found: 2026-08-07, during the SPEC A→D sequence. Related-but-out-of-
scope across several SPECs in a row since; not addressed.

Both scripts can write to the same vault file without coordination.
Scope and exact mechanism not yet designed.

- [ ] Design a coordination mechanism (lock file, sequencing, or
      similar) and implement it.

**Source.** Roadmap_v14, "Следующая очередь" candidates list.

#### [B-013] P2 — Repeat article-pipeline/tooltempest recon post-migration

Found: 2026-08-25, noted as a follow-up during the DocOps-merge work;
still open as of 2026-08-26.

Recon for the DocOps merge was partially done at the start of the
2026-08-25 session, against article-pipeline/tooltempest's
pre-migration state (article-pipeline/tooltempest structure read,
ADR-0032 "Drift Warning" confirmed to physically live in
article-pipeline not tooltempest, tooltempest had exactly one real
consumer at recon time). Radar's own reality changed substantially
since (GitHub instead of GitLab, new CI system) — the pre-migration
recon snapshot shouldn't be relied on as still-current without
re-checking.

- [ ] Re-run the article-pipeline/tooltempest structure recon and
      confirm nothing relevant drifted since the pre-migration
      snapshot (consumer count, ADR-0032's location, MANIFEST.txt
      contents).

**Source.** Roadmap_v14 / session 2026-08-25, carried forward from the
original DocOps-merge task's own recommendation.

- [ ] [B-007] Timeout unification across pipeline scripts — undecided,
      no new context since first noted.
- [ ] [B-008] GitHub API retry logic — undecided, no new context since
      first noted.

### P3

- [ ] [B-003] Confirm each GitHub Actions cron schedule actually fires
      as designed. Updated 2026-08-27: of the 6 workflows with an
      actual cron trigger, 4 are now confirmed firing on schedule —
      `daily-run.yml`, `publish.yml`, `security.yml`, `lint-vault.yml`
      (all `success` except one `daily-run.yml` failure, root-caused
      and fixed the same day — see this session's `fix(auth)` commit).
      `weekly-patterns.yml` (`Thu 22:00 UTC`) and `monthly-lifecycle.yml`
      (1st of month, `17:00 UTC`) remain unconfirmed — neither has
      reached its next scheduled occurrence yet. `confirm-candidate.yml`
      was miscounted in this entry's original text: it is
      `workflow_dispatch`-only, has no cron trigger, and will never
      "confirm by firing on its own" — dropped from this item's scope.
      `pages.yml`/`test.yml` remain push-triggered, already confirmed.
      Remaining passive: waits on the next Thursday and next
      month-start respectively, not further work.
- [ ] [B-005] less-tokens / README-fetch+llm-tldr compression — blocked,
      the content this would compress doesn't exist in the pipeline
      yet.
- [ ] [B-006] Phase 3b: transition matrix / Temporal Consistency
      Validator — event-triggered, waits on accumulated data.
- [ ] [B-010] Observability gated layer — waits on an explicit trigger
      from data; the 2026-07-15 sequencing decision (not before the
      other gated layers below) stays in force.
- [ ] [B-011] Trust & Security gated layer — waits on an explicit
      trigger from data; same 2026-07-15 sequencing decision applies.
- [ ] [B-012] Optimization & Evolution gated layer — waits on an
      explicit trigger from data; same 2026-07-15 sequencing decision
      applies.

## Owner decisions needed

### P2

#### [B-002] P2 — Does `vault` need GitHub branch protection now that the GitLab mirroring reason is gone?

Found: 2026-08-07 (as an unresolved side effect of SPEC C's mirroring
scope), resurfaced 2026-08-25 during the full platform migration.

On GitLab, `vault` was protected purely as a technical prerequisite for
the push-mirror filter (only protected branches get mirrored) — that
reason disappeared with the full migration. Whether `vault` needs some
protection on GitHub independent of the old reason (e.g. so the CI
token can't accidentally overwrite something outside the normal
pipeline) is an architectural call the owner hasn't made yet. This is
also ADR-0014's own stated open item.

- [ ] Owner decides: protect `vault` on GitHub (and under what rule),
      or leave it unprotected deliberately. Answer becomes an ADR if
      it sets a rule, or is applied directly as a GitHub setting if
      it's a simple configuration choice.

**Source.** SPEC C (2026-08-07), ADR-0014 (2026-08-25).

---

Version: reflects the 2026-08-26 revision — rewritten to match
article-pipeline's real `[B-NNN]` Tasks/Owner-decisions structure
(confirmed against article-pipeline's actual `docs/BACKLOG.md`, not
assumed). 13 entries assigned (`B-001` through `B-013`); prior prose-only
open/rejected/closed content preserved as historical narrative above the
ID-bearing sections. Source: this session's BACKLOG.md audit and
extraction-plan confirmation, 2026-08-26.

#### [B-014] P3 — Contributor governance deferred until first real external PR
Found: 2026-08-27, session recon + Taleb/O'Connor/Harari lens review.
Radar has zero external contributors today. Designing a tooltempest-shared
governance pattern (CODEOWNERS, pre-merge gate, mirroring article-pipeline's
ADR-0033/0034/0035 chain) now would hardcode against a hypothetical, not a
real need — the antifragile move is to build when the first real PR arrives,
not before. This is a deliberate freeze, not an oversight: revisit only when
an actual external PR shows up.
- [ ] No action until triggering event occurs
- [ ] When triggered: reference article-pipeline's docs/adr/0033-0035 chain
      (final state per 0035, not the superseded 0033 prose) as the design
      basis, generalized via tooltempest — not copied hardcoded per-project
**Source.** Session decision, 2026-08-27, cross-repo recon + explicit
architectural-lens review (Taleb/O'Connor/Harari).

#### [B-015] P4 — Drift notification: resolved by existing pre-push mechanism
Found: 2026-08-27, same session.
Considered a scheduled GitHub Actions workflow in tooltempest to detect
consumer drift without waiting for a push. Decided against: the existing
pre-push hook already caught real drift today (.tooltempest.lock pinned
622e326 vs tooltempest HEAD a59d9aa) at zero additional infrastructure
cost. A cross-repo Issue-opening mechanism would need a new PAT with
write access to consumer repos' Issues — new attack surface and failure
point for a scenario (solo maintainer not opening a repo for weeks) that
doesn't match actual daily-cron usage. Closed as resolved-by-existing-
mechanism, not deferred.
- [x] No further action — existing pre-push hook is sufficient
**Source.** Session decision, 2026-08-27, cross-repo recon + explicit
architectural-lens review (Taleb/O'Connor/Harari).
