---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: A self-hosted agent framework that introduces a credentialed gateway
  architecture to separate model inference from tool execution and credentials, enabling
  multi-surface deployment (Slack, Nostr) with unified team memory, designed for organizational
  sovereignty and auditability rather than vendor-managed agents.
evidence_log:
- date: '2026-09-11'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 0e75823cd7a3ef356e9988fd9ea24ea8c9932c62
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-09-11'
  verdict: CANDIDATE
---
# Multi-surface AI agent toolkit with credentialed gateway

**Дата:** 2026-09-11
**Репозиторий:** https://github.com/sageox/agent-toolkit
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "Hosted agents, on your own infra. One agent, one memory, across Buzz and Slack. Your team's context, inherited and live, when SageOx is connected."

## What Changes in the Ecosystem
The ecosystem gains a reference architecture for multi-surface agents that decouples the decision-making model from credential management and tool execution, shifting from "model holds keys" to "gateway holds keys, brain only asks." Teams deploying this project can achieve cross-channel agent presence (Slack + Nostr/Buzz) with unified memory while maintaining fine-grained tool access control and audit trails. The pattern enables smaller organizations and self-hosted deployments to run sophisticated agents without building their own gateway and credential infrastructure.

## Reasoning
The project implements a working multi-surface agent architecture with architectural innovation (gateway-model separation, credential isolation, MCP-in-gateway pattern) that goes beyond conventional agent frameworks. Manifest shows real infrastructure (Helm, Terraform, audit logging) and test coverage. However, adoption signals remain limited to early adopters; the 3 maturity reflects functional code with some production deployment capability but not yet field-hardened at scale.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** Yes. The README claims: (1) "Hosted agents, on your own infra" with gateway owning credentials and connections—manifest shows deploy/ with Helm and Terraform, deployment-contract.md referenced. (2) "One memory, one persona, one profile across surfaces"—file tree shows .sageox/ and docs/guide/memory-and-tools.md structure. (3) MCP servers run "inside the gateway, not beside the brain"—docs/guide references MCP credential handling. (4) Team memory via SageOx integration—.sageox/ directory and references to `ox` CLI. (5) Audit log with tool_call tracking—docs/guide/reference.md referenced. Package.json shows TypeScript tooling and vitest test coverage. The manifest structurally supports the README claims without contradictions.
Подтверждено: Да

**Novelty checklist:** New protocol? Yes—the gateway-model credential separation and MCP-in-gateway pattern represent a new architectural protocol for safe agent tool access that isolates the language model from credential handling. New standard? Partially—team memory integration with SageOx is a procedural standard for team knowledge inheritance but not a widely adopted formal standard yet. New architectural layer? Yes—the gateway layer as a credentialed multiplex with per-surface egress routing and refuse-able refusals is a new architectural abstraction not found in earlier agent toolkits. New market interaction model? Yes—the model of self-hosted sovereignty over agent infrastructure with team-scoped memory over SageOx represents a new way teams can deploy and run agents without vendor lock-in while gaining organizational context.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, at least 3 independent organizations (verified by public GitHub discussions, case studies, or conference talks) deploy agent-toolkit in production across Slack and Buzz concurrently, confirming the multi-surface architecture is viable and adoption is growing beyond proof-of-concept.
**Если ошиблась:** Within 12 months, the project receives no new external contributors, no documented production deployments emerge, and issue velocity drops below 2 issues/month, indicating the architecture remains a reference design without meaningful ecosystem adoption.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-11 - CANDIDATE: первая оценка

## Связи
- [[MCP как слой интеграции сервисов 2026-06-14]]
- [[Self-hosted суверенитет над агентной инфраструктурой 2026-06-14]]
- [[Верификация и доверие к действиям агентов 2026-06-14]]
- [[Локализация памяти и идентичности агента 2026-07-23]]
- [[Collaborative_AI_агенты_в_shared_workspaces 2026-06-24]]
