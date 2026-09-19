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

## Product & Business Roadmap

Owner-confirmed annual Target State (confirmed 2026-09-18), separate
from the technical phases above. States each Objective's Outcome and
the Requirements needed to reach it — not how to build them. No KR,
no acceptance tests, no diagrams, no implementation detail — see
docs/BACKLOG.md for task-level work and docs/adr/ for any resulting
decisions.

### Objectives

**O1 — Attention concentration map**
Outcome: show where changes and engineering activity are
concentrating right now, not just list events — a topic → intensity
→ change map that is harder to get from ordinary reading.
Requirement: R1.1.

**O2 — Trajectory, not snapshot**
Outcome: show trajectory, not a single moment — a time series that
lets Radar distinguish a real shift from a random spike, so each
topic's movement over time is visible.
Requirement: R2.1.

**O3 — Technology Landscape**
Outcome: show the domain's structure, not a list of technologies —
group signals by capability/domain and show connections between
them, so a user can move from one project to its topic, neighboring
topics, and related changes.
Requirement: R3.1 (depends on R1.1).

**O4 — Technology lifecycle map**
Outcome: separate high attention from real momentum and maturity by
combining attention dynamics, independent Evidence count, and signal
duration into a model of a technology's state — explored as a
hypothesis, not adopted as a predefined truth.
No Requirement currently derivable.

**O5 — Wardley-like model (research hypothesis)**
Outcome: explore, as a research hypothesis, whether linking
technology/capability to user need and evolution lets Radar show how
a domain's structure changes.
No Requirement currently derivable.

**O6 — Evidence-backed Track Record**
Outcome: build a history of signal → trajectory → outcome, so Radar
can show which past signals held direction, changed, or were
disproven.
Requirement: R10.2.

**O7 — Decision Support**
Outcome: for a topic, show what changed → why it matters → Evidence
→ trajectory → implications, so a user can decide faster what to
research, try, change, or ignore.
No Requirement currently derivable — the underlying evidence/
interpretation separation is a design choice, not a logical
necessity of this Outcome.

**O8 — Concrete paid product**
Outcome: create a specific thing a person can buy, with a defined
price, a public entry point, and delivery of the paid result.
No technical Requirement derivable — this is a product/business
decision outside this Roadmap's scope.

**O9 — First real revenue from Radar**
Outcome: obtain a cumulative real revenue of ₽100,000 from Radar.
No technical Requirement derivable — same reason as O8.

**O10 — Repeatable payment and delivery**
Outcome: make the path from discovery to payment to delivery
repeatable without proportional growth in manual work.
No Requirement currently derivable — depends on O8/O9 first.

**O11 — Article Pipeline as a distribution engine**
Outcome: automatically turn Radar's strongest signals into articles;
Article Pipeline is a distribution mechanism for Radar's result, not
part of the Radar Engine itself.
No Radar-side Requirement currently derivable — blocked on Article
Pipeline's own readiness, not on Radar.

**O12 — Self-reinforcing loop**
Outcome: a loop where a good signal produces content, content brings
a user, the user uses Radar, Radar builds trust, some users pay, and
revenue improves Radar.
No Requirement currently derivable — an emergent effect of O1-O11,
not a separate technical property.

**O13 — Domain-independent Radar**
Outcome: make Radar a mechanism for building a Radar for any
fast-changing domain, not just AI — by separating domain-specific
rules from the core engine.
No Requirement currently derivable; not to be pursued before O9 is
reached.

**O14 — Prove the Radar Engine's portability**
Outcome: prove that the domain-specific part is genuinely separable
from the core, by building a second Radar with minimal core changes.
No Requirement currently derivable; not to be pursued before O9 is
reached.

**Additional goal — Evidence Base for Article Pipeline**
Outcome: Radar produces the verified, traceable Evidence base Article
Pipeline draws its material from.
No Requirement currently derivable — same blocker as O11.

**Additional goal — Radar for the owner's own technology decisions**
Outcome: Radar supports a controlled check-and-decide loop for the
developer's own projects, not just external recommendations.
No Requirement currently derivable.

**Additional goal — Feedback loop between Radar and projects**
Outcome: outcomes of the owner's own project decisions feed back into
Radar's Track Record.
No Requirement currently derivable; depends on the previous
additional goal.

### Requirements

| ID | Requirement | Objective | Depends on | Status |
|---|---|---|---|---|
| R1.1 | Signals must be attributable to a topic/category | O1 | — | Not implemented |
| R2.1 | A signal's history must be reconstructible | O2 | — | Implemented — `verdict_history` |
| R3.1 | Topics/capabilities must be related to each other | O3 | R1.1 | Not implemented |
| R10.2 | A signal's original interpretation and later observed state must be stored separately, so they can be compared | O6 | — | Not implemented |
