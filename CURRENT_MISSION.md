# Current Mission

## GOAL
ID: G041, G005
Title: Detect technology shifts; result observability
Source: ../SYSTEM_GOALS.md
Goals version: 2026-09-30.v1
Reference: docs/PROJECT.md

## NOW
Remediating the Anthropic API cost/spend issues found in the 2026-09-23
token-spend investigation (`docs/BACKLOG.md`'s [B-024]/[B-025]/[B-026]).

## CURRENT STEP
Add usage/token logging (`input_tokens`/`output_tokens`) at each of the 7
Anthropic API call sites across 6 files — `analyze.py` (1, raw HTTP `requests.post`),
`update_assessments.py` (1, raw HTTP `requests.post`), `patterns.py` (2, SDK
`client.messages.create`), `fetch_analysts.py` (1), `check_model_updates.py` (1),
`telegram_post.py` (1) — [B-025]. Verified directly against the code this session;
`patterns.py` has two call sites, so the true count is 7, not 6.

## WHY
[B-025] is explicitly marked directly actionable ("low-effort/routine"); [B-024]
and [B-026] are explicitly blocked on a dedicated `/spec` session to redesign
`update_assessments.py`'s re-check logic, so they cannot be worked on now.

## DONE WHEN
Usage logging is added and confirmed present at all 7 named call sites (across
the 6 named files); `docs/BACKLOG.md`'s [B-025] is closed.

## IN SCOPE
- Usage/token logging additions at the 7 named call sites
- Any shared code path touched solely to add that logging

## OUT OF SCOPE
- Redesigning `update_assessments.py`'s 30-day recheck logic or adding a
  prompt-truncation cap ([B-024]/[B-026] — both blocked on their own `/spec` session)
- [B-001] (already closed) and [B-004] (blocked on its own `/spec` session) —
  ROADMAP's previously-stated P1 pool
- Any P2/P3 event-triggered backlog item, contributor governance, or Product &
  Business Roadmap (O1-O14) work
- General architecture cleanup or refactors not required for [B-025]

## BLOCKERS
- None known for [B-025] itself.
- Ambiguity, recorded rather than resolved: `docs/ROADMAP.md`'s Current pointer
  still names [B-001]/[B-004] as the current P1 pool. That text predates the
  2026-09-23 cost investigation and has not been updated since; [B-001] is already
  closed and [B-004] is blocked. This mission file tracks the narrower,
  evidence-backed current work ([B-025]) instead of the stale pointer text.

## STATUS
ACTIVE

## SCOPE RULE
Discovered issues, ideas, opportunities, cleanup, refactors, and future work do not
become part of the current mission unless they are required by DONE WHEN or
explicitly added to IN SCOPE. Otherwise record them in the appropriate
backlog/state mechanism and continue the current mission.
