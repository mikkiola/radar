---
paths:
  - "src/**"
  - "tests/**"
---

# Pipeline implementation and tests

Read the root [SPEC](../../SPEC.md) and the relevant accepted decisions before
changing classification, lifecycle, vault writes or publication semantics.
Use the existing tests' synthetic paths and network/model doubles; inspect the
chosen fixture before execution rather than assuming every test is isolated.
Never use the live vault branch/worktree as a temporary test directory.
A fixture proves the tested code path, not model judgment or a live channel post.
Do not invoke production scripts or fetch external sources to validate prose.
