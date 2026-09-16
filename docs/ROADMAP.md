# Radar — Roadmap

State as of 2026-08-27. Phases, sequencing, dependencies, and the
current execution pointer only — no task detail (→ `docs/BACKLOG.md`),
no rationale (→ `docs/adr/`). Rewritten wholesale on each revision;
full history lives in `git log` and `docs/adr/`, not here.

| Phase | Status |
|---|---|
| SPEC A → A.5 → A.6 → E → C → B → D (foundational implementation & hardening) | Closed |
| GitLab → GitHub platform migration | Closed |
| DocOps / Rules-compliance (ADRs + canonical docs rewrite) | Closed — `ARCHITECTURE.md`, `BACKLOG.md`, `ROADMAP.md` (this file), and `CONSTITUTION.md` all rewritten to the Documentation Rules structure |

## Current pointer

DocOps/Rules-compliance closed 2026-08-27. Done: 24 ADRs total (14
verbatim + 10 inferred from pre-existing `CONSTITUTION.md` prose), and
all four canonical docs (`docs/ARCHITECTURE.md`, `docs/ROADMAP.md`,
`docs/BACKLOG.md`, `docs/CONSTITUTION.md`) rewritten to the
Documentation Rules' structure.

`[B-001]` and `[B-004]` are both pulled as the current P1 work pool.
`[B-001]` (graph rendering) is directly actionable now — a
verification task (trigger a fresh `pages.yml` run and a
hard-cache-clear check), no decision required. `[B-004]` (prompt
injection) is blocked on a dedicated `/spec` session to resolve the
isolation-vs-risk-acceptance choice before any implementation
starts — it is not pullable for direct work until that session
happens. Most of the remaining P2/P3 queue (`[B-005]`, `[B-006]`,
`[B-010]`–`[B-012]`) is event-triggered — waiting on accumulated data,
a scheduled cron firing, or a checkpoint being reached — not pullable
on demand regardless of priority.

## Dependency chain

```
SPEC A → A.5 → A.6 → E → C → B → D
        (closed)
              |
              v
GitLab -> GitHub platform migration
        (closed)
              |
              v
DocOps / Rules-compliance (closed)
  +-- ARCHITECTURE.md   (done)
  +-- BACKLOG.md        (done)
  +-- ROADMAP.md        (done -- this file)
  +-- CONSTITUTION.md   (done)
              |
              v
Next task (undetermined -- pulled from docs/BACKLOG.md by priority
or owner decision)
  B-005, B-006, B-010, B-011, B-012 -- independent of each other and
  of this phase closing; each waits on its own external/data trigger
```

## Open decisions

See `docs/BACKLOG.md`'s "Owner decisions needed" section — currently
one entry, `[B-002]` (whether `vault` needs GitHub branch protection
now that the GitLab mirroring reason for it is gone).
