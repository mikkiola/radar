---
id: ADR-0029
status: Accepted
supersedes: ADR-0026
superseded_by: null
source_type: inferred
---

# 0029 — The Constitution Holds Project Rules Only; Universal Rules Come from the Pinned ToolTempest File

## Status

Accepted by the Owner, 2026-11-10. Supersedes ADR-0026 in one point only (ADR-0026 stays unedited, DR-6), Decision item 7: the requirement that "a dated note records the replacement"; the rest of ADR-0026 stays in force.

## Context & Constraints

Observation at commit `7e66e19`: `git show 7e66e19:docs/CONSTITUTION.md | wc -l` prints 421. Many of those lines state rules that are not specific to this repository: the reading order, the mission card, the stop-and-ask rule, the review report, the ADR rules, and the language rule. Section 14 allows a same-day naming correction of an Accepted ADR (`git show 7e66e19:docs/CONSTITUTION.md | sed -n 346,357p`). Section 13 calls the permanent `SPEC.md` an exception (`git show 7e66e19:docs/CONSTITUTION.md | sed -n 325,328p`), while the shared SPEC policy covers it with the idle marker (universal rule SP-3).

ToolTempest states the universal rules once, in `docs/tooltempest/universal-rules.md`, and delivers that file through the contract root that its materializer installs (ToolTempest ADR-0020). The Owner approved the direction and this amendment on 2026-11-10.

## Decision

1. The Constitution holds the working rules of this repository only. For every universal rule it names the universal rule and repeats no obligation from it.
2. The universal rules are binding here. A document that contradicts them is fixed.
3. The universal rules reach this repository through the ToolTempest pin. This change does not alter the pin. The consumer change is pushed together with the repin, after the ToolTempest push.
4. The entry point routes to the universal rules and to the Constitution.
5. The Constitution carries no dated notes. Git history and the decision records hold the history.

## Alternatives & Rationale

- Keep the universal rules in the Constitution: rejected, because the consumers' copies differ and nothing compares them.
- Track a copy of the universal rules here: rejected, because a tracked copy is a second source that the pin does not control.

## Consequences

- Section numbers 1 to 17 are kept. A section whose rules are universal keeps its number and names the universal rule IDs.
- Until the repin, the universal rules file is absent here (`git ls-tree -r --name-only 7e66e19 docs/tooltempest` prints nothing) and the pointers to it have no target.
- The same-day naming correction of an Accepted ADR is no longer allowed. An Accepted ADR is not edited.
- `SPEC.md` staying in the repository is no longer an exception: it declares `spec-state: idle` between tasks, as the universal rules state.
- Write confirmation follows universal rule WR-13, the Owner's decision of 2026-11-10: the task prompt is the approval, and `[ЗАПРОС]` stays for token revocation, deleting a file another process may depend on, an edit of a Constitution, and an edit of `.tooltempest.lock` under the consumer contract. It loosens the earlier rules that every write, delete, or move needs the Owner's confirmation every time, and that files are read-only by default. `git show 7e66e19:docs/CONSTITUTION.md | grep -n -e "every time" -e "PLAN.md" -e "write a release"` prints them, and `git show 7e66e19:docs/CONSTITUTION.md | sed -n 266,267p` prints the read-only default.
- The model and login restriction, and the vault rules, stay project rules. Qualifiers that define a condition were restored: the Cowork replacement, the merge-request level, and the channel input language.
- The sentence that a session ends when its task is done and reported or at a stop-and-ask case (base lines 59 to 63, in the range below) is deleted because WR-5 forbids the agent to decide that a session is over. The routing sentence of `CLAUDE.md` about using the active mission with the SPEC is removed (`git diff 7e66e19 -- CLAUDE.md`); the row "The current target, when `CURRENT_MISSION.md` is `ACTIVE`" of the conflict table in "How every repository works" and step 8 of its "Reading order" hold it. The sentence to consult `docs/adr/` before changing an accepted decision moves to Constitution section 14. The commit confirmation of section 11 is void under the Owner's decisions of 2026-11-11 (next item).
- Explanation, examples, and history of the earlier Constitution that are not carried over: `git show 7e66e19:docs/CONSTITUTION.md | sed -n '12,13p;21,23p;26,28p;42,43p;48,50p;59,63p;67,70p;130,133p;147,150p;166,168p;204,209p;252,255p;291,294p;302,304p;309,314p;370,385p;413,421p'`. The whole removed text is `git diff 7e66e19 -- docs/CONSTITUTION.md` (lines that start with a minus).
- Owner decisions of 2026-11-11. Commit and push: a local commit inside the task's scope needs no Owner confirmation (the agent checks the full diff and runs the prescribed checks first, and a commit that contains an edit of a Constitution keeps its question under WR-13); any `git push` needs a separate explicit permission under universal rule WR-14. The earlier rule of section 11 (the full diff and the Owner's confirmation before any commit or push) changes to this order. The session-end skill no longer pushes: its single-candidate step makes a local commit and says that a push needs WR-14. The skill is repository text (`git ls-files .claude/skills` lists it; ToolTempest's `MANIFEST.txt` does not name it), so it is fixed here. Repin: a task prompt that names a repin authorizes the change of `.tooltempest.lock` and its local commit under the conditions of the consumer contract; this repository holds no separate repin rule.
- The rule sentences of `CLAUDE.md` that universal rules state are deleted there (session-end as an Owner action: WR-5; the commit half of "permission to prepare is separate from permission to commit or push" is void under the Owner's decisions of 2026-11-11 and section 11, and the push half is WR-14; "use `.claude/rules/pipeline.md`" moved to section 15), and those specific to this repository moved to Constitution sections 2 and 15 with a pointer left; the base text is `git show 7e66e19:CLAUDE.md`. No rule sentence is left in `CLAUDE.md`. Two statements are deleted without a home: that the rules are binding (the universal rules state it) and that a ToolTempest source pin does not install or activate a skill (a delivery fact that the consumer contract owns).
- `SPEC.md` no longer cites the Article Pipeline Constitution section "SPEC.md's status", which that repository's rewrite removed; it cites SP-1 and SP-3.
- Historical text that still cites removed rule locations stays as an open item: `git grep -n "documentation-rules.md" -- docs/BACKLOG.md` prints the citation of the earlier reference document in the backlog history.

## Confirmation & Revisit

The commit that adds this record carries the checks it ran and their output in its message.

The RV-6 ledger of this change, one row per obligation of the earlier Constitution (CARRIED, DELETED, or NA), is kept with the change report outside the repository. Rows marked GAP in it were restored in the Constitution or recorded in this ADR after the ledger was written; the staged text prevails.

Revisit when a rule that this repository needs cannot be stated as a project rule without contradicting a universal rule.

## Source

The Owner's task of 2026-11-10 and the Owner's decisions of 2026-11-11, executed in Claude Code sessions. This record is unpushed, and the Owner instructed that it is editable. Claude Code drafted the wording, so `source_type` is `inferred`. No external AI cross-check was made.
