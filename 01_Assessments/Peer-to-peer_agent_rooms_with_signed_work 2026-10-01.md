---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: Valhalla is a novel peer-to-peer agent communication layer that
  distributes signed authorship and room discovery across participant-chosen peers
  rather than a platform intermediary. It represents new cryptographic trust and decentralized
  routing primitives, but remains in prototype stage with no live network, incomplete
  transport validation, and experimental Iroh integration.
evidence_log:
- date: '2026-10-01'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: dd0dd2863fa47ae087d64e96864a70d6019bd23e
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-10-01'
  verdict: CANDIDATE
---
# Peer-to-peer agent rooms with signed work

**Дата:** 2026-10-01
**Репозиторий:** https://github.com/hraness/valhalla
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "Valhalla is open-source software for peer-to-peer rooms shared by AI agents and the people who run them. Every post is signed by the key that wrote it."

## What Changes in the Ecosystem
Valhalla introduces a new primitive: cryptographic proof-of-authorship baked into agent-to-agent/agent-to-human communication, removing the platform as a trust intermediary. It shifts the architectural layer from "hosted room + accounts on homeserver" to "peer-selected network + key-based identity + signed message protocol". This enables agents to own their identity and routing separately from where conversations persist.

## Reasoning
Valhalla proposes a novel architectural layer (signed peer-to-peer protocol for agents) and a new market model (decentralized, platformless agent rooms). However, it is explicitly pre-release ("In development"), has no public network, incomplete transport coverage (Iroh still experimental in builds, TLS as fallback), and unvetted multi-NAT/relay scenarios. The project demonstrates architectural novelty but remains at prototype maturity with early momentum.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims peer-to-peer rooms with signed posts, encrypted private rooms using MLS, Iroh transport, and MCP server integration. The Cargo.toml structure (crates/) shows modular CLI, browser, and networking components; package.json confirms web/browser presence. The file tree includes docs/ with release-readiness.md, iroh-private-rooms.md, cli-agents.md confirming the README's architectural claims. However, README explicitly states "In development" and "There is no public network or hosted service to join yet", indicating core features remain incomplete.
Подтверждено: Да

**Novelty checklist:** New protocol: YES – Valhalla introduces a custom peer-to-peer protocol combining signed posts, MLS encryption, and Iroh transport that differs from existing agent communication standards. New standard: PARTIAL – it proposes patterns for agent identity/signing but lacks formal standardization. New architectural layer: YES – it establishes a cryptographic trust layer (signed work, key-based identity) and transport abstraction (Iroh relay/direct) that sits between agents and messaging. New way of market interaction: YES – decentralized signed agent-to-human/agent-to-agent rooms without platform intermediation represent a shift from hosted services like Moltbook or Matrix's homeserver model. All four questions yield affirmative answers.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, a documented federated agent network using Valhalla's protocol runs with at least 3 independently operated peers plus published benchmarks showing message latency, relay reliability under NAT, and replay checkpoint safety across restart cycles.
**Если ошиблась:** Within 12 months, no public Valhalla network launches; the project remains archived or in 0.x.x state with fewer than 100 active agents, or a critical architectural flaw in the MLS/Iroh integration surfaces that requires non-backward-compatible changes.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-01 - CANDIDATE: первая оценка

## Связи
- [[Cryptographic Trust as Native Agent Architecture 2026-08-04]]
- [[Local-First Agent Memory and Cognition Layers 2026-08-04]]
- [[Persistent_Cognition_Sidecar_Architecture 2026-08-02]]
- [[AI_Agent_Authorization_Middleware 2026-08-15]]
