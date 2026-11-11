# Radar — Constitution

| Field | Value |
|---|---|
| Type | Reference |
| Holds | The working rules of this repository only |
| Universal rules | [`docs/tooltempest/universal-rules.md`](tooltempest/universal-rules.md), section "How every repository works" |

The universal rules are binding here. They state the reading order, which file
wins on a conflict, how a rule changes, the function of each document, and the
ADR, commit, review, mission, and language rules. This file does not repeat
them. MUST, SHOULD, and MAY have the meaning defined there.

After the repin that delivers it, the universal rules file is materialized from
the commit pinned in `.tooltempest.lock` and is not tracked. In a fresh clone, materialize it first;
`.gitignore` gives the command.

Section numbers are stable IDs. A section whose rules are universal keeps its
number and names the universal rule IDs.

## 1. Role

The Owner's values: automation, strict order, zero small talk.

| Surface | Role | Limits |
|---|---|---|
| Cowork (claude.ai chat) | Architect, planning | Runs no code. Has no GitHub connector for repository operations. In Google Drive it creates and copies files; the Owner moves and deletes. It cannot overwrite an existing Google Doc without a write tool for that file: it prepares the full replacement text, and the Owner applies it. |
| Claude Code | Implementer | All Git operations (commits, pushes, branch and file changes) go through Claude Code on the real machine, never through Cowork. Cowork's own instruction document is a Project Knowledge entity, outside Claude Code's scope. |

- Ordinary technical work needs no per-step confirmation: reading, drafting,
  editing, running commands, preparing diffs.
- Write, delete, move, and local commit follow universal rule WR-13 (§9). Push
  follows WR-14 (§11).

## 2. Session protocol

- At session start, also check the real current date.
- When Project Knowledge on claude.ai and this repository disagree, this
  repository wins for anything `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`,
  `docs/BACKLOG.md`, or this file covers. Do not rely on
  `project_knowledge_search` as the sole source when a canonical document
  might have changed.
- `README.md` stays in English, reflects the current architecture, and MUST
  NOT expose internal paths, secrets, or exact cron schedules.
- `/session-end` (`.claude/skills/session-end/SKILL.md`) closes
  `docs/BACKLOG.md` entries only. It has no fact-sync step. Reuse it and the
  installed shared skills; do not add another closer, an automatic session
  detector, or a copied global skill.
- Session end: WR-5.

## 3. Keeping documents current

Universal rules WR-4, WR-5, DR-10. In addition, update the document in the same
commit, not in a separate later step.

## 4. The one stop-and-ask rule

Universal rules WR-1, WR-2.

## 5. Test-Driven Development

Universal rule WR-6. It applies to `compute_status()` and
`apply_quarantine_gate()` in `src/analyze.py`.

## 6. Unconditional rules (no exceptions)

Universal rules WR-7 to WR-10. In addition:

| Topic | Rule |
|---|---|
| Sensitive operations | Actions on protected branches and Rulesets need GitHub's web UI. When Claude Code's auto-mode classifier blocks `git remote add` or `git push`, even with explicit confirmation, the Owner runs the command in a regular terminal. |
| Git remotes | Name the remote in every push, pull, and fetch. Start a diagnosis with `git fetch` and `git status` per remote. Periodically diff branches across remotes for symmetry. Re-check `git remote -v` at the first sign of a mismatch. |
| Compactness | A new tool MUST be pip-installable, with no PyTorch, GPU dependency, Docker, or database. The exception covers Betterleaks and TruffleHog only. |
| Epistemic labels | Mark a hypothesis `ГИПОТЕЗА` and a verified fact `ФАКТ`. Record an experiment's epistemic status the same way. Do not trust data that contradicts the rest of the context without direct verification. |
| Incident closure | Track and close Operational status and Root Cause status separately. |
| Secrets | Keep API keys only in CI secrets, never in Markdown, the repository, logs, or publications. Each external service gets its own key; do not reuse a key across projects or purposes. Pass a key under test to the child process as an inline prefix of that one command, never to the session itself. |
| Diagnostic endpoints | Before you use a new endpoint that can return secret values, read what its `masked` or `protected` flag hides. After a leak through an API call, rotate every secret that the call can reach. |
| Code | Check the real path before a write. Declare Python functions before the `if __name__ == "__main__"` block. Use only hyphens, no em or en dashes, inside Python strings. Use `sed` on macOS with an explicit empty backup argument. Diagnose a gitlink without a `.gitmodules` entry with `git ls-files`. |
| CI | Review a CI config like code. Do not mark a CI variable Protected when its branch is not protected. Run `python3 -m py_compile` after every Python change, and `yaml.safe_load` on a workflow file before you commit it. |
| Model calls | Every programmatic Sonnet call sets `thinking` to `disabled` and sets no `temperature`, `top_p`, or `top_k`. A clustering call over 20 files sets `max_tokens` to at least 5200. |
| Vault writes | Edit assessment and pattern files in place, never wholesale, and check `os.path.exists(filepath)` first. `README.md` and `LICENSE` MAY be rewritten wholesale. |
| Model IDs | `src/99_System/model_config.json` is the one source of model IDs. Never hardcode a model ID in a script. Update it by hand only, after a smoke test and a breaking-changes check. |
| Assessment fields | Write `status` only through `write_verdict_entry()` in `vault_write.py`. Record a disagreement with the model's verdict only in `## Правка человека`; never edit the model's original fields in place to reflect a human override. The `Модель:` / `Промпт версия:` block belongs only in `02_Patterns/` output, never in `telegram_post.py`. |
| Process | Use a merge request only for a major architectural task, at the level of a SPEC. After any commit on a tracked branch, verify its SHA through the public GitHub API alone, with no token on the agent's side, where the repository's visibility allows. Check production cron schedules, GitHub Actions included, for a race before a multi-hour session that touches `vault`. Run a real acceptance run in CI before you close a phase that touched CI configuration. |

## 7. ToolTempest consumer obligation

`docs/tooltempest/consumer-contract.md` states the obligation. It is
materialized with the universal rules file; read the version pinned in
`.tooltempest.lock`, not a remembered one.

## 8. Conditional rules

Universal rules WR-1, WR-2, WR-11. In addition:

- For a routine configuration choice with no stated preference, pick the
  option whose failure is cheaper and more reversible.
- An external AI cross-check or brainstorm is not evidence that an idea was
  tested unless at least one participant rejected the hypothesis at some point.
  Universal agreement is not evidence.

## 9. Write/Delete/Move confirmation

Universal rule WR-13.

## 10. Response format by task type

| Task type | Format |
|---|---|
| Chat with the Owner | Russian, dry facts, bullet lists, code. No preamble. |
| Routine work | One decision. No options. |
| Uncertainty | One clarifying question. |
| Architectural decision | Universal rule WR-3. |
| Write, delete, or move | Universal rule WR-13. |
| Release write, on the command "write a release" | One file per session, in the Google Drive Radar folder, named `RELEASE_<date>`. |

## 11. Review report format

Universal rule RV-1. In addition:

- Where visibility allows, confirm through the public GitHub API that the
  pushed commit SHA matches the one reported.

## 12. The `/spec` skill

Universal rule SP-2. In addition:

- A Claude Code session that touches code runs only on Sonnet, under the
  existing Pro subscription login. Never Opus, Fable, Mythos, or a direct
  `ANTHROPIC_API_KEY`. Confirm the model and the login before the session
  starts. Scripts in this repository that use their own `ANTHROPIC_API_KEY`
  are not covered.
- Before implementation, verify `SPEC.md` against the real code.

## 13. `SPEC.md`'s status

Universal rules SP-1 to SP-5. In addition:

- `SPEC.md` stays in the repository between tasks (SP-3).
- After a successful commit, delete `PLAN.md` and similar transient planning
  artifacts. Do not archive them.

## 14. ADR discipline

Universal rules DR-1 to DR-13. `scripts/generate_adr_index.py` generates
`docs/adr/ADR-INDEX.md`; `scripts/hooks/pre-commit` blocks a commit with a
stale index. No check enforces DR-11 here. Consult `docs/adr/` before you change an accepted decision.

## 15. Claude Code task discipline

Universal rules WR-12, WR-16, and WR-17. In addition:

- Use `.claude/rules/pipeline.md` for pipeline changes.
- A neighboring `vault` worktree is not a disposable fixture and is not part of
  an instruction-edit task.
- Open Owner decisions in `PROJECT` remain open. A working script or a passing
  fixture does not settle a product outcome, a business goal, or a definition
  of done.
- Brain and Article Pipeline are separate systems. Workspace proximity
  authorizes no cross-project integration.
- Commands in `README.md` are not authorized smoke tests.
- Select an existing test module after you inspect its network and model
  doubles.
- Preserve the primary code checkout, the existing worktrees, and their
  histories.

## 16. Language

Universal rules LG-1 to LG-4. In addition, data for the AI is in English.
Named exceptions:

- Russian: chat with the Owner, Telegram channel output, human-edited template
  fields.
- Vault files: the body and headings of a vault file follow the language of the
  body. The `Метка:` fields `Оценка`, `Статус`, `Вердикт`, and
  `Уверенность` are Russian literals that code matches by exact string. Do not
  retrofit old Russian-language files.
- Channel voice for Telegram posts: first person, direct, no preamble, no
  explanations for a broad audience, no CTA, no emoji markers, 300 to 800
  characters, always Russian regardless of the language of the input data.

## 17. The Mission Harness (`CURRENT_MISSION.md`)

Universal rules MC-1 to MC-6.
