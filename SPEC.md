---
spec-state: idle
---

# SPEC.md

No active `/spec` focus right now.

Full decision history for the closed SPEC A / A.5 / A.6 / E / C / D
blocks that previously accumulated in this file now lives in
`docs/adr/0007` through `docs/adr/0012` respectively. SPEC B
(Repository Discoverability) has no dedicated ADR — see `git log` for
its record.

This file is the root `SPEC.md` (universal rule SP-1): the next `/spec`
session overwrites it wholesale once a new task becomes the active focus, and
the history of what it previously contained is retrieved via
`git log -- SPEC.md`, not preserved as a stub inside the file itself. It stays
in the repository between tasks and declares `spec-state: idle` (SP-3 and
Constitution section 13).
