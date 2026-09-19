---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Foldkit-plus is an architectural framework that projects a single
  Foldkit state machine into typed agent, sync, and UI contracts through schema-first
  boundaries, eliminating secondary state and enabling safe exposure to MCP and LLM
  agents without duplicating business logic.
evidence_log:
- date: '2026-09-19'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 6ef5634f82deb5a9117802f898de626031bb3d12
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-09-19'
  verdict: CANDIDATE
---
# Schema-first agent layer for Foldkit

**Дата:** 2026-09-19
**Репозиторий:** https://github.com/doeixd/foldkit-plus
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "A Schema-first agent layer for Foldkit: project an application's Model and Message union into one contract, then expose it through WebMCP, MCP, or in-app agents."

## What Changes in the Ecosystem
Foldkit Plus introduces a typed projection boundary that allows single-reducer applications to safely expose their state machine to external agents (MCP, WebMCP, A2A) and UI frameworks (React, design systems) without creating secondary state or duplicate business logic. The architectural shift is moving from "application outputs to many backends" (each with its own reducer/cache) to "application state machine projects into typed contracts at explicit boundaries" (all replaying through one update function).

## Reasoning
Foldkit-plus addresses a real architectural problem: how to extend a single-state-machine application to agents, servers, and UIs without fragmenting state ownership. The novelty lies in the schema-first projection layer (Agent.forApplication, Sync.forApplication, Surface) that maintains referential integrity between contracts and the core update function. Maturity is early (many packages, active examples, CI passing) but adoption signals are limited; it appears to be a sophisticated framework authored primarily by Patrick Glenn with some community engagement (DeepWiki badge, CONTRIBUTING.md) rather than production-wide usage.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims foldkit-plus extends Foldkit applications outward to agents, servers, devices, URLs, and design systems while maintaining a single state machine. The manifest confirms a monorepo workspace with 26+ packages (visible in pnpm-workspace.yaml structure, package.json scripts reference multiple example/feature packages). The file tree shows: packages/ directory (containing the modular packages referenced in code), examples/ directory (demonstrating agents, sync, mixins, react, remote, todo-app scenarios), docs/ and skills/ directories. The concrete code example in README demonstrates Agent.forApplication(), Sync.forApplication(), Style.forSlots(), and Surface concepts—all consistent with the claimed architecture of projecting Model/Message unions into agent contracts, sync layers, and view systems. The agent/sync/mixins/surface packages are indeed present as separate concerns meeting at explicit application boundaries.
Подтверждено: Да

**Novelty checklist:** 1) New protocol: Partially yes—foldkit-plus proposes a schema-first contract pattern for exposing Foldkit state machines to MCP/WebMCP/A2A, but these are compositions of existing protocols (MCP is established, A2A is internal). 2) New standard: No—uses Effect Schema and Foldkit conventions, not a new standard format. 3) New architectural layer: Yes—introduces an explicit "agent boundary layer" that projects application state (Model/Message/update) into typed agent contracts without duplicating reducer logic. This is a new abstraction boundary not present in base Foldkit. 4) New way of market interaction: No—does not introduce a new market mechanism or commerce pattern.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, a publicly documented production deployment reports using foldkit-plus to safely expose a business-critical Foldkit state machine to LLM agents via MCP while maintaining audit consistency and replay semantics across sync/agent/UI layers.
**Если ошиблась:** Within 12 months, the project shows no new commits, examples remain toy applications (todo list), and no external projects adopt the agent/sync projection pattern, indicating the architectural benefit does not justify learning curve for real-world use cases.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-19 - CANDIDATE: первая оценка

## Связи
- [[Открытые протоколы координации агентов 2026-06-25]]
- [[Self-hosted_контроль_и_управление_агентами 2026-06-12]]
- [[Local-First_Multi-Agent_Software_Platform 2026-09-17]]
- [[Верифицируемый_харнес_для_свопаемых_моделей 2026-07-27]]
