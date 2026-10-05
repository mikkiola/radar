---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Model Citizen is an early-stage governance layer that decouples
  agent rules (guardrails, cost, roles) from runtime implementations via a synced
  control plane, enabling portable agent policies across Claude Code and Codex without
  changing orchestration.
evidence_log:
- date: '2026-10-05'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 974e47a92b3eae473826f273e6a6b1bd0b0608eb
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-10-05'
  verdict: CANDIDATE
---
# Agent control plane with guardrails

**Дата:** 2026-10-05
**Репозиторий:** https://github.com/JakeSelby/model-citizen
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "The control plane for your coding agents, however you run them. One checkout of rules, skills, subagents, hooks and stances, projected into Claude Code and Codex with your own primitives: hook-enforced guardrails, usage telemetry, cost postures and model tiering, under any rules library or orchestration layer."

## What Changes in the Ecosystem
Model Citizen introduces a novel control-plane abstraction layer that decouples agent governance rules (guardrails, cost policies, skill libraries) from specific runtimes (Claude Code/Codex). Rather than embedding rules into each agent spawn, rules become reusable, versioned primitives that sync bidirectionally and export observability to standard telemetry backends. This shifts the agent ecosystem from runtime-specific governance toward portable, declarative control patterns.

## Reasoning
The project presents early-stage but functionally coherent architecture for agent governance, evidenced by documented hooks, role-based cost tiering, and working sync/ownership mechanics. Maturity is low (2/5) because it shows prototype signs: single-author repository, nascent adoption signals, and reliance on specific Claude runtimes rather than vendor-agnostic portability. Novelty is high (4/5) because it introduces a genuine architectural layer—treating agent governance as a declarative, synced control plane rather than embedded instructions—which is absent from existing agent frameworks.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims to be "the control plane for your coding agents" with hooks, rules, skills, roles, cost tracking, and OTLP export. The file tree confirms architectural presence: ./claude/hooks/ (grade-bash.py, stop-gate.py, brief-guard.py, neutralize-tool-output.py), ./primitives/ (rules, stances, skills), ./claude/agents/ (reviewer.md, worker-a.md), ./codex-plugin/ and .claude-plugin/ directories for runtime integration, ./lib/ for core logic, and exports to Langfuse/Phoenix/Opik via OTLP. The ownership journal concept and sync mechanism are referenced in docs/. The CI badge and code structure (bin/citizen, config.example.json, product.json data model) support the working prototype status.
Подтверждено: Да

**Novelty checklist:** Is this a new protocol? No—uses existing Claude Code/Codex APIs and standard OTLP telemetry. Is this a new standard? No—builds on Claude Directory plugin convention. Is this a new architectural layer? Yes—introduces a declarative control plane layer that sits between orchestration and agent runtimes, managing guardrails, cost postures, and model tiering as first-class primitives that persist across multiple runtime targets (Claude Code and Codex). This is a distinct architectural abstraction for agent governance. Is this a new way of market interaction? Partial—it enables multi-runtime agent deployment with unified policy, but doesn't fundamentally change how agents are acquired or billed.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, Model Citizen is adopted by ≥2 independent organizations running Claude Code agents in production with declared cost postures and visible hook decisions logged via Langfuse/Phoenix.
**Если ошиблась:** Within 12 months, the project enters maintenance mode (infrequent commits, no new runtime integrations beyond Claude Code/Codex, no adoption announcements from external teams).

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-05 - CANDIDATE: первая оценка

## Связи
- [[Local-First_Project_Memory_for_AI_Agents 2026-09-06]]
- [[Execution_Safety_Layer_for_AI_Agents 2026-09-11]]
- [[AI_Agent_Authorization_Middleware 2026-08-15]]
- [[Local-First_Multi-Agent_Software_Platform 2026-09-17]]
- [[Верификационный_шлюз_для_агентских_действий_Claude 2026-06-14]]
