---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: open-scion instantiates a server-centric VCS protocol for agent-heavy
  monorepos using server-side commit/rebase and content-addressed storage, a novel
  architectural layer not present in traditional distributed VCS, though currently
  at proof-of-concept maturity and single-machine scale.
evidence_log:
- date: '2026-10-15'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: 67abed60affd6c96ac96f52281911d90197b07f8
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-10-15'
  verdict: CANDIDATE
---
# Server-centric agent VCS in Rust

**Дата:** 2026-10-15
**Репозиторий:** https://github.com/bnsd55/open-scion
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "A version control system for large monorepos where most of the writers are AI agents. The server keeps the history and makes the commits; clients ask only for what they need."

## What Changes in the Ecosystem
The protocol layer shifts from Git's clone-everything-client-side-rebase model to server-centric commit, rebase, and storage. Agents no longer clone repositories; they request only needed files and ask the server to land changesets, eliminating redundant data transfer and local merge resolution. The storage abstraction changes from full-repository copies to immutable, content-addressed file trees with lazy derivation, enabling Anthropic's reported scale (30,000+ merges/day, 25M checkouts/day on 100GB history).

## Reasoning
open-scion is a proof-of-concept implementation of a genuinely new architectural pattern for version control—server-side commit/land/rebase—designed specifically for agent-heavy monorepos. While it is not yet production-ready (README explicitly states "proof of concept", benchmark on one machine, single-threaded landing) and draws inspiration from Anthropic's published design rather than inventing from scratch, it does instantiate a novel control-plane protocol and storage model not previously available in the open-source ecosystem. Maturity is low (1–2 range) due to stated limitations and proof-of-concept status; novelty is high (4 range) because it introduces a new architectural primitive, though not fully original research.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims this is a server-centric VCS for agent-heavy monorepos with core concepts of changesets, server-side rebasing, and file-level deduplication. The Cargo.toml workspace structure shows four crates: scion-core (object model), scion-proto (gRPC API), scion-server (storage and lands), and scn (CLI client). The file tree includes proto/scion.proto confirming gRPC implementation, docs/architecture.md and docs/format-v1.md detailing the design, and working build/test infrastructure. The README example (`scn cat main:src/lib.rs`, `scn commit`, `scn land`) matches the CLI binary structure. Benchmark output ("200 agents landed 10,000 changes at about 200 lands per second") is reproducible from the stated code path. The core claim—a server-side commit/rebase system instead of Git's client-side model—is structurally consistent with the provided manifest and crate organization.
Подтверждено: Да

**Novelty checklist:** Is this a new protocol? Yes—it defines a gRPC-based API (proto/scion.proto) for agent-server VCS interaction fundamentally different from Git's clone-fetch-push model. Is this a new standard? Not formally; it is a reference implementation of Anthropic's published design, not a standardization body output. Is this a new architectural layer? Yes—server-side commit/land/rebase as a primary architectural primitive for agent-heavy monorepos is a new control-plane pattern not present in distributed VCS systems. Is this a new way of market interaction? Partially—it enables agents to interact with repositories without cloning or local rebasing, shifting the operational model for CI/agent coordination at scale.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, the project achieves multi-machine deployment (distributed storage and landing), establishes a public instance or tutorial with real-world agent usage (e.g., Claude via MCP), and lands ≥2 independent third-party integrations or forks adapting the protocol.
**Если ошиблась:** Within 12 months, the project is archived or marked maintenance-only, Anthropic publishes a competing open-source Scion implementation that captures the mindshare, or adoption remains limited to the original author with no evidence of third-party agent integration or production deployment.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-15 - CANDIDATE: первая оценка

## Связи
- [[Execution_Safety_Layer_for_AI_Agents 2026-09-11]]
