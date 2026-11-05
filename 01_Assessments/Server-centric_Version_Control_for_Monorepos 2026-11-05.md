---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: openscion is an independent Rust implementation of a server-centric,
  changeset-based version control protocol designed for agent-heavy monorepos, using
  server-side rebase and content-addressed sparse reads to eliminate per-agent clone
  overhead. Currently alpha, structurally novel, but unproven in production.
evidence_log:
- date: '2026-11-05'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: 5df81f3b2589bd471cb7bf27e78d939344c21bf9
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-11-05'
  verdict: CANDIDATE
---
# Server-centric Version Control for Monorepos

**Дата:** 2026-11-05
**Репозиторий:** https://github.com/bnsd55/openscion
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "Server-centric version control for agent-heavy monorepos, in Rust. An independent open-source implementation of the design from Anthropic's "Redesigning source control" post."

## What Changes in the Ecosystem
The ecosystem structure shifts from distributed full-clone workflows to server-centric sparse-read and server-side rebase. Agents no longer pull full repository history or manage local merge logic; they send content-addressed changesets and the server handles conflict detection and trunk movement. This reduces bandwidth per agent, eliminates merge rebasing on client machines, and enables high-frequency (30,000+ merges/day) writes to shared trunk without clone overhead.

## Reasoning
openscion is an alpha-stage (0.x) independent implementation of a published architectural pattern for server-centric monorepo control. It introduces a new protocol (gRPC changeset API) and a new architectural layer (server-side rebase, sparse reads, content-addressed storage) that differs structurally from git. Maturity is low (alpha, single-machine, no production signs) but novelty is high (new protocol, new architecture for monorepo+agent workflows). The project is gaining initial structure but shows no adoption signals yet.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** Yes. The README claims a "server-centric" model where "the server does the work" (history, commits, rebases), agents send changesets (files changed only), and landing is "server-side rebase" with compare-and-swap. The manifest confirms a workspace with multiple crates: scion-server (the server storage/commits), scn (client), scion-cache and scion-daemon (tiered caching), scion-core (object model), scion-proto (gRPC API). The file tree shows proto/ (for protocol definition), docs/architecture.md and docs/protocol-v1.md, and the README explicitly describes the three-command workflow (cat, commit, land) and the conflict model. The Cargo.toml lists gRPC dependencies (tonic, prost) and PostgreSQL is required for metadata. The structural components align with the claimed architecture.
Подтверждено: Да

**Novelty checklist:** Is this a new protocol? YES - the README and docs describe a custom gRPC-based protocol (proto/scion.proto, docs/protocol-v1.md) distinct from git's push/pull model. Is this a new standard? PARTIALLY - it implements Anthropic's published design (October 2026) but is not itself a ratified standard; it is an independent open-source implementation. Is this a new architectural layer? YES - the server-centric, changeset-based, sparse-read model is a fundamentally different layer from git's distributed model; it changes how version control interacts with monorepos and agent workflows. Is this a new way of market interaction? PARTIALLY - it targets agent-heavy workflows but the economic/market dimension is not primary to the design; the novelty is technical, not market-structural.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, openscion lands multi-machine deployment with distributed storage and replication, or a public instance reports handling 10,000+ daily agent writes at sub-second latency with &lt;1% conflict rate, indicating production viability.
**Если ошиблась:** Within 12 months, the project remains single-machine alpha, receives no third-party PRs or reported deployments, or the README's claim that "server-side rebase" eliminates merge conflicts for non-overlapping paths is refuted by field reports of correctness issues or hidden merge requirements.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-11-05 - CANDIDATE: первая оценка

## Связи
- [[Local-First Agent Memory and Cognition Layers 2026-08-04]]
- [[Agent-driven_desktop_development_environment 2026-10-20]]
- [[Инфраструктура_памяти_для_агентов_с_MCP 2026-07-12]]
