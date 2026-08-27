---
name: session-end
description: "Explicit, owner-triggered BACKLOG.md closure for Radar: reviews this session's commits for Closes: B-NNN trailers and presents/writes matching docs/BACKLOG.md closures per the confirmation rules below. Triggers on: /session-end only — never invoked by the model on its own judgment. Generic Closes: mechanism only, adapted from article-pipeline's session-end skill (its Syncs:/M1-M6 half is article-pipeline-specific and not included here)."
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Edit, Bash
---

# /session-end

Explicit, human-triggered BACKLOG.md closure for Radar, per the
`Closes: B-NNN` convention documented in tooltempest's
`docs/reference/documentation-rules.md`. The owner types
`/session-end`; invoking it *is* the signal this command acts on —
it does not try to infer whether a session is "done."

## Trailer-detection rule

**Never use a naive line-start text match** (e.g. grep for lines
beginning with "Closes:") — a commit body can contain ordinary prose
that happens to start a wrapped line with that same text. Use git's
own trailer parser instead, which only recognizes a real trailing
`key: value` block per `git-interpret-trailers`:

```bash
git log <session-commit-range> --format="%H %(trailers:key=Closes,valueonly)"
```

Each output line is `<full SHA> <value-or-blank>` — filter out blank
values; a commit with no `Closes:` trailer produces a trailing space
and nothing after it. Never fall back to a plain line-start grep
under any circumstance.

## What this does

1. **Find this session's `Closes: B-NNN` trailers**, per the
   trailer-detection rule above — never scan further back than this
   session's own commits, no repo-wide history scan.
2. **Look up each `B-NNN`'s current title** in `docs/BACKLOG.md` (its
   `#### [B-NNN] <title>` heading line — note Radar uses 4 hashes,
   not 3) — verbatim, exactly as written, no summarizing or
   rewording.
3. **Zero candidates found:** say so plainly (e.g. "No `Closes:`
   trailers found in this session's commits — nothing to close.").
4. **Exactly one candidate:** write the `docs/BACKLOG.md` edit and
   commit/push it directly. Invoking `/session-end` already is the
   owner's "close now" signal — no separate per-item confirmation
   prompt needed on top of that.
5. **More than one candidate:** present them as a numbered list,
   verbatim titles, and ask which one(s) to mark done, if any. No
   git/implementation jargon in that question (no "trailer,"
   "commit," "candidate"). Wait for the owner's explicit pick before
   writing anything; never guess.
6. **If a closure later turns out wrong:** an ordinary follow-up
   edit/commit fixes it — no supersession ritual.
7. Never touches `docs/CONSTITUTION.md`, `docs/ARCHITECTURE.md`, or
   `docs/ROADMAP.md` — this skill only handles `docs/BACKLOG.md`
   closure. Radar has no `Syncs:`/structural-fact-sync mechanism
   (that's an article-pipeline-specific invention, not part of
   tooltempest's shared convention) — do not attempt it.

**Source.** Adapted 2026-08-27 from article-pipeline's
`.claude/skills/session-end/SKILL.md`, generic `Closes:` half only.
Duplicated rather than shared via tooltempest for now — see Radar's
`docs/BACKLOG.md` for the owner decision on whether/when to
consolidate into a shared tooltempest skill.
