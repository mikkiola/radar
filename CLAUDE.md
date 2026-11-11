# Radar project entry point

Radar's code branch contains collection, assessment, pattern and publication
logic. Its separate `vault` branch holds pipeline data.

## Sources of truth

Start with the section "How every repository works" of the
[universal rules](docs/tooltempest/universal-rules.md): the reading order, the
file that wins on a conflict, how a rule changes, and what each document is for.
If the file is absent, run the command in
[.gitignore](.gitignore). If
`docs/tooltempest/universal-rules.md` is missing: stop and run, from the
repository root, `D=$(mktemp -d) && git clone -q --no-checkout ~/Dev/github.com/mikkiola/tooltempest "$D" && git -C "$D" checkout -q --detach <commit> && python3 "$D/scripts/tooling.py" materialize --root . --source "$D" --apply; rm -rf "$D"`.
`<commit>` is the `commit` field of `.tooltempest.lock`.
`$D` is a new temporary clean checkout that the last command removes; the
ToolTempest main clone, which can be dirty, is only read.
Project rules are in
[CONSTITUTION](docs/CONSTITUTION.md); [SPEC](SPEC.md) holds the bounded
implementation requirements. This file routes to these sources. The working
rules for code and tests are in Constitution sections 5 and 6; for task
discipline and neighboring projects, in section 15.

## Code and tests

- [src](src/) contains pipeline modules, including model/network entry points.
- [tests](tests/) contains the existing pytest cases; scope and source-path
  configuration are in [pyproject.toml](pyproject.toml).
- [README](README.md) describes the repository and existing execution surfaces.

Example test commands:

```bash
python3 -m pytest tests/test_vault_write.py -q
python3 -m pytest tests/test_check_frontmatter.py -q
```

Pipeline rules: `.claude/rules/pipeline.md`.

## Existing workflows

The [session-end skill](.claude/skills/session-end/SKILL.md) handles BACKLOG
closure, not Article Pipeline's structural sync procedure.
