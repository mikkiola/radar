# Radar project entry point

Radar's code branch contains collection, assessment, pattern and publication
logic. Its separate `vault` branch holds pipeline data; a neighboring vault
worktree is not a disposable fixture or part of an instruction-edit task.

## Sources of truth

Read [CONSTITUTION](docs/CONSTITUTION.md), [PROJECT](docs/PROJECT.md),
[ARCHITECTURE](docs/ARCHITECTURE.md), [ROADMAP](docs/ROADMAP.md),
[BACKLOG](docs/BACKLOG.md) and [CURRENT_MISSION](CURRENT_MISSION.md).
Use the active mission for the operational task and [SPEC](SPEC.md) for its
bounded implementation requirements. Consult [docs/adr](docs/adr/) before
changing an accepted decision. This file is a navigation layer, not a duplicate
project specification or strategic goal registry.

Open owner decisions in PROJECT remain open. A working script or successful
fixture does not settle a product outcome, business goal or definition of done.
Brain and Article Pipeline are separate systems; no cross-project integration
is authorized by proximity in the workspace.

## Code and tests

- [src](src/) contains pipeline modules, including model/network entry points.
- [tests](tests/) contains the existing pytest cases; scope and source-path
  configuration are in [pyproject.toml](pyproject.toml).
- [README](README.md) describes the repository and existing execution surfaces;
  commands there are not automatically authorized smoke tests.

Select an existing test module after inspecting its network/model doubles:

```bash
python3 -m pytest tests/test_vault_write.py -q
python3 -m pytest tests/test_check_frontmatter.py -q
```

Use `.claude/rules/pipeline.md` for pipeline changes. For instruction-only edits,
check links, path scopes, exact diff and `git diff --check`; do not run pipeline
entry points, workflow dispatch, Telegram publication or live API calls.

## Existing workflows

The [session-end skill](.claude/skills/session-end/SKILL.md) is explicit and
owner-triggered. It handles BACKLOG closure, not Article Pipeline's structural
sync procedure. Reuse that workflow and installed shared skills; do not add
another closer, automatic session detector or copied global skill.
A ToolTempest source pin does not install or activate a skill.

Preserve the primary code checkout, existing worktrees and their histories.
Permission to prepare a change is separate from permission to commit/push it.
This offline instruction task changes no settings, permissions, hooks or MCP.
