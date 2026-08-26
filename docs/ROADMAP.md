# ROADMAP — Radar

Rewritten wholesale on each revision. History lives in `git log` and
`docs/adr/`, not here.

The previously agreed sequence (SPEC A → A.5 → A.6 → E → C → B → D)
closed in full 2026-08-07. SPEC A: ADR-0007. SPEC A.5: ADR-0008.
SPEC A.6: ADR-0009. SPEC E: ADR-0010. SPEC C: ADR-0011 (superseded by
ADR-0013). SPEC D: ADR-0012. SPEC B (Repository Discoverability) has no
dedicated ADR — see `git log` for its record.

## Next queue (undetermined)

The next task is chosen again from `docs/BACKLOG.md`'s "Out of queue,
waiting on a trigger" list, or by the owner's new priority — a separate
`/spec` session, triggered explicitly by the owner
(`disable-model-invocation`).

Candidates with no assigned order (see `docs/BACKLOG.md` for the full
list and each one's current status):

- less-tokens / README-fetch+llm-tldr — waiting on content that would
  need compressing to exist.
- Phase 3b (transition matrix) — waiting on accumulated data,
  event-triggered.
- Timeout unification, GitHub API retry logic — undecided, no new
  context.
- `update_assessments.py`/`recheck_lifecycle.py` race condition on the
  shared vault file — found 2026-08-07, related-but-out-of-scope across
  several SPECs in a row, not addressed.
- Observability / Trust & Security / Optimization & Evolution —
  waiting on an explicit trigger from data at checkpoints; the
  2026-07-15 sequencing decision stays in force.

`vault` branch public/private decision — **resolved, ADR-0014.** No
longer an open candidate here.

## Process principles

Unchanged from the previous revision, confirmed in practice 2026-08-07.

**An MR only for major architectural tasks at SPEC A's level.**
Confirmed in practice three times running: SPEC C, B, and D created
neither an MR nor even an intermediate feature branch — all three
changes were targeted documentation/UI-configuration edits, below the
threshold where branch isolation adds real protection rather than just
process weight.

**Acceptance verification through public, read-only APIs, no token on
the agent's side.** Previously symmetric across GitLab (project ID
`82780086`) and GitHub (public repository, no token) as of SPEC C;
updated for the GitHub-only reality — commit SHA is now verified
through the public GitHub API alone, after every commit touching a
tracked branch.

## Compactness requirement

Unchanged from the previous revision.

Any new tool must be pip-installable, with no PyTorch/GPU/Docker/
database. The narrow exception for Betterleaks and TruffleHog stays
narrow, not a reformulation of the general rule. SPEC C/B/D added no
new dependencies at all — push-mirroring wasn't code, and
README/ARCHITECTURE.md aren't runtime.

---

Version: reflects the 2026-08-26 revision. SPEC A through D's history
moved to `git log`/`docs/adr/`; this file's scope narrowed to the
undetermined next-work queue and process principles only. `vault`
branch public/private decision removed as resolved (ADR-0014). GitLab
references updated to the GitHub-only reality. Source: Roadmap_v14
(2026-08-07 content) — per the owner's 2026-08-26 decision, this file
is now the sole source of truth going forward; the Google Drive folder
it came from is frozen as a historical archive, no parallel Google Doc.
