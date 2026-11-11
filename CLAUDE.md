# Radar project entry point

Radar's code branch contains collection, assessment, pattern and publication
logic. Its separate `vault` branch holds pipeline data.

## Sources of truth

Start with the section "How every repository works" of the
[universal rules](docs/tooltempest/universal-rules.md): the reading order, the
file that wins on a conflict, how a rule changes, and what each document is for.
If `docs/tooltempest/universal-rules.md` is missing: stop and run, from the
repository root:

```bash
( set -eu; D=$(mktemp -d "${TMPDIR:-/tmp}/tooltempest.XXXXXX"); trap 'rm -rf "$D"' EXIT; R=$(python3 -c 'import json; print(json.load(open(".tooltempest.lock"))["repository"])'); C=$(python3 -c 'import json; print(json.load(open(".tooltempest.lock"))["commit"])'); git clone -q --no-checkout "$R" "$D"; git -C "$D" checkout -q --detach "$C"; python3 "$D/scripts/tooling.py" materialize --root . --source "$D" --apply )
```

The command reads `repository` and `commit` from `.tooltempest.lock`, uses a new
temporary clean checkout that it removes on exit, and does not touch any other
ToolTempest clone.
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
