---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: LayerX Network is a deterministic execution and accounting infrastructure
  layer that orders autonomous agent activities through a canonical append-only log,
  enforces nondeterminism-free state transitions, and periodically settles batch checkpoints
  to a Paxeer custody network, enabling provable agent commerce at scale without continuous
  on-chain transactions.
evidence_log:
- date: '2026-09-10'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 9f40c1e5800d4611be2d04a52b3102aac55ac907
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-09-10'
  verdict: CANDIDATE
---
# Deterministic Agent Execution Network

**Дата:** 2026-09-10
**Репозиторий:** https://github.com/Sidiora-Labs/LayerX-Network
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "LayerX Network is a deterministic execution and accounting network for autonomous agents. Every state-changing operation enters as a signed, canonically encoded `Activity`. The protocol verifies the actor and its authority, consumes the account sequence, orders the activity on one global sequence, applies a deterministic state transition, and returns a signed receipt tied to the resulting state root."

## What Changes in the Ecosystem
LayerX introduces a dedicated deterministic execution layer that separates agent instruction ordering (via canonical Activities) from settlement finality (via Paxeer checkpoints), allowing autonomous agents to operate with provable ordering and accounting without continuous on-chain transactions. The append-only activity log as single authority, combined with signed receipts tied to state roots, shifts the agent execution model from ad-hoc RPC calls to deterministic consensus-critical state machines. The settlement-layer separation and 402 HTTP payment integration create a new market primitives for agent commerce, where actions are ordered and accounted locally, with batch settlement to an external custodial network.

## Reasoning
LayerX Network presents a novel architectural primitive: a deterministic execution and accounting layer specifically designed for autonomous agents, with consensus-critical operations excluding nondeterministic sources, settlement separation, and cryptographic accountability through signed receipts. The project demonstrates working testnet, multi-language SDKs, and substantial engineering (C17 runtime, Rust interface, Solidity contracts, comprehensive platform tooling), placing it at maturity level 3 (working, some adoption signs via testnet and SDK readiness). Novelty is high (4/5) because it combines deterministic execution ordering, agent-native accounting, and settlement separation in a way that doesn't map directly to existing blockchain or agent frameworks.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims LayerX is a "deterministic execution and accounting network" with activity logging, settlement via Paxeer, checkpoint registration, agent programs (WebAssembly), and multi-SDK support (Rust, Python, TypeScript, Go, JVM, .NET, Swift). The manifest shows extensive TypeScript middleware/integrations (buyer, merchant, seller), agent SDKs, and platform examples. The file tree confirms C17 runtime (`src/`, `include/`), Rust agent interface (`agent/`), Solidity contracts (`contracts/`), settlement integration (`paxeer-network/`), and developer platform components (`platform/`). The structure supports the core architectural claims of deterministic consensus, agent execution, and settled checkpoints. Testnet quickstart commands and multi-language SDK paths are present, indicating working implementation beyond proof-of-concept.
Подтверждено: Да

**Novelty checklist:** New protocol: YES - LayerX defines a deterministic execution and accounting protocol with signed Activities, sequence ordering, state roots, and settlement via Paxeer; this is architecturally distinct from existing blockchain/agent patterns. New standard: PARTIAL - KVX specifications are mentioned but not fully detailed in the excerpt; the LXT-20 token interface suggests emerging standardization. New architectural layer: YES - the append-only activity log as consensus authority, with disposable projections and signed receipts, combined with agent execution determinism and periodic settlement checkpoints, constitutes a new execution and accounting layer for autonomous agents. New way of market interaction: YES - the 402 HTTP commitment model and merchant-buyer-seller middleware suggest a new payment and settlement coordination mechanism within agent networks.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, LayerX testnet processes a documented 1M+ activities from autonomous agents with verified deterministic replay, state root consensus, and successful settlement batches to Paxeer with dispute-free claim processing, demonstrating production-grade ordering and accounting infrastructure.
**Если ошиблась:** Within 12 months, LayerX fails to launch a stable mainnet, the activity log determinism claims are refuted by unresolvable replay discrepancies, agent SDK adoption remains under 100 active users, or the settlement integration with Paxeer is abandoned in favor of a simpler centralized model.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-10 - CANDIDATE: первая оценка

## Связи
- [[Cryptographic Trust as Native Agent Architecture 2026-08-04]]
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[Открытые протоколы координации агентов 2026-06-25]]
- [[Self-hosted суверенитет над агентной инфраструктурой 2026-06-14]]
- [[Оркестрация множества коммерческих агентов 2026-07-23]]
