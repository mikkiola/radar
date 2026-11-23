---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: OpenGuardrail is a novel decoupled guardrail service introducing
  an architectural layer for deterministic, evidence-based gating of AI agent actions
  with audit trails; currently in development preview with claimed Alibaba production
  use but no broad external adoption yet.
evidence_log:
- date: '2026-11-23'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: 085665ed2519c106ed1ef5ff97c3aec70d85461e
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-11-23'
  verdict: CANDIDATE
---
# Evidence-based action guardrails for AI agents

**Дата:** 2026-11-23
**Репозиторий:** https://github.com/alibaba/open-guardrail
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "Evidence-based action guardrails for AI agents"

## What Changes in the Ecosystem
OpenGuardrail introduces a new service tier in agent-based systems: a decoupled guardrail layer that separates policy definition, evidence collection, and decision verification from both agent reasoning and tool execution. This enables organizations to enforce traceable compliance gates without embedding checks in agent prompts or modifying execution tools—shifting from implicit safety (agent judgment) to explicit, auditable decision infrastructure. The ecosystem gains a reusable infrastructure primitive for high-stakes agent deployments (data deletion, production rollouts, infrastructure changes).

## Reasoning
OpenGuardrail is a novel architectural layer for AI agent execution safety—it creates a dedicated "decision verification" service that agents submit evidence to, receive gate decisions from, and whose decisions execution tools verify before acting. This is architecturally distinct from existing agent frameworks (which embed safety in prompts) or guardrail middleware (which filter outputs). However, the project is still in "development preview" (v1alpha1 API), with evidence of only internal Alibaba production use mentioned, no visible community adoption, and no hardened production markers yet.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims OpenGuardrail is a "standalone guardrail service for AI agents that operate real systems" with "evidence-based action guardrails" enforcing policy checks at execution time. The manifest shows Go 1.27+ backend with PostgreSQL/SQLite support, OpenAPI integration, and database migrations. The file tree confirms server/, storage/, api/, integrations/, and examples/ directories supporting the claimed architecture of an HTTP API service with audit trails, Run reports, and policy validation. The examples/agent-demo/ contains working checkout scenario (first_batch.py, first-batch.yaml) demonstrating the claimed agent + guardrail + execution tool flow. The README's claimed "evidence-based decision recording with ALLOW/DENY and validity window" is structurally supported by storage layer and OpenAPI endpoints mentioned. However, the status is explicitly "development preview" with "v1alpha1 API", confirming this is not production-hardened yet.
Подтверждено: Да

**Novelty checklist:** Is this a new protocol? Partially - OpenGuardrail defines a novel evidence submission and verification protocol for AI agent action gating (agent proposes checks → guardrail validates → execution tool verifies), not a standard protocol but a custom one. Is this a new standard? No - it uses OpenAPI/HTTP standards. Is this a new architectural layer? Yes - this introduces a dedicated "decision verification layer" between agent intent and tool execution that did not exist as a reusable service before. Is this a new way of market interaction? Yes - it shifts from "agents self-enforce checks" to "third-party guardrail as service validates and gates action execution with audit trails for compliance."
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, OpenGuardrail reaches v1 (stable API), has at least 3 documented integrations in live production outside Alibaba (e.g., via agent frameworks like LangChain, AutoGen, or cloud provider marketplaces), and shows measurable community GitHub activity (100+ stars, active issues/PRs, external contributors).
**Если ошиблась:** Within 12 months, the project remains in alpha/beta, shows no adoption beyond Alibaba's internal use, has fewer than 100 GitHub stars, and no stable v1 release is announced; or the core concept is absorbed into major agent frameworks (Claude, OpenAI agents) as built-in features, making the standalone service redundant.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-11-23 - CANDIDATE: первая оценка

## Связи
- [[Верификационный_шлюз_для_агентских_действий_Claude 2026-06-14]]
- [[Org_OS_with_Agent_Sandbox 2026-08-27]]
- [[Governable_Pipeline_для_AI-кодирования 2026-06-23]]
- [[Верификационные_промпты_для_ИИ-агентов 2026-07-06]]
