---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Xyne Spaces redefines org coordination by collapsing connector silos
  into a unified, permission-scoped context layer that agents and humans query through
  identical APIs; the three-tier sandbox (gateway | runtime | VM) is a novel security
  primitive for production agent code execution within user permission boundaries.
evidence_log:
- date: '2026-08-27'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 6ae359754ecbdc784e784b667c6bcc09a1488f3d
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-08-27'
  verdict: CANDIDATE
---
# Org OS with Agent Sandbox

**Дата:** 2026-08-27
**Репозиторий:** https://github.com/juspay/xyne-spaces
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "At the center: your org's context. Connectors bring in what your organization already knows — Slack, Google Workspace, Microsoft 365 and more — normalised into a store built for records and retrieval, and served back to your people and your agents through permission-aware org-context APIs, so every caller gets exactly the slice they're allowed to see."

## What Changes in the Ecosystem
Xyne Spaces introduces a unified org context layer that merges human collaboration, agent automation, and permission enforcement into a single architectural tier—moving from siloed connectors (Slack, Jira, Confluence) to a normalized, searchable, permission-aware store. Agents now inherit user permissions rather than operating as privileged actors, inverting the security model for agentic systems. The three-tier sandbox (gateway with secrets, runtime without secrets, bash in VMs) creates a new primitive for running untrusted agent code safely in production orgs.

## Reasoning
Xyne Spaces is a sophisticated implementation of org context and agent orchestration (maturity 2: post-demo, clear deployment targets, but limited adoption signals beyond authored ecosystem). The novelty is substantial (4/5): it introduces a new architectural layer (permission-scoped org context as a primitive) and inverts agent security models (agents inherit user permissions, writes require approval). The project shows growing momentum with CI/CD, monorepo discipline, multiple app suites, and explicit infrastructure-as-code; however, production adoption signals are absent from the repo alone.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** Yes. README claims: (1) unified org context store with permission-aware APIs from multiple connectors (Slack, Google Workspace, Microsoft 365), (2) real-time collaborative apps (Chat, Call, Canvas, Tickets, Support Desk), (3) agent sandbox with split security tiers (gateway with secrets, runtime without secrets, bash in isolated Kata VMs), (4) MCP tool support. File tree confirms: monorepo structure with apps/ (xyne-claw, xyne-spaces-backend, xyne-spaces-dashboard), packages/, claw-deployments/, docker-compose configurations for local dev, vespa-core/ for search, package.json showing TypeScript 5, pnpm workspace, and build scripts for shared libs (storage, icons, agentic-framework). Manifest lists CI workflow, contributing guidelines, MCP integration (`.mcp.json`), and infrastructure-as-code patterns (Nix, flake, Docker Compose profiles). The claims about permission layers, agent isolation, and multimodal app integration are structurally supported by the repo layout.
Подтверждено: Да

**Novelty checklist:** Is this a new protocol? Partially—MCP is leveraged but not invented here; however the permission-aware context API layer and agent-sandbox protocol (three-tier HMAC-signed dispatch with Kata isolation) appears novel in combining these patterns. Is this a new standard? No—it adopts MCP, TypeScript, Docker Compose, Postgres, Redis as standards. Is this a new architectural layer? Yes—the unified org context store that normalizes connectors into a single permission-scoped retrieval layer, served to both UI and agents, is a new abstraction tier that didn't exist before. Is this a new way of market interaction? Yes—positioning agents and humans as co-workers in the same context/permission model, rather than separate access paths, represents a shift in how orgs coordinate automation with human context.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** In 12 months, Xyne Spaces reaches 50+ external organizations deploying it as a self-hosted org backbone, with documented case studies showing agent-assisted workflows reducing ticket-triage time by >40%.
**Если ошиблась:** In 12 months, the project remains primarily used by Juspay's internal teams; no external production deployments are documented, and contribution velocity from non-Juspay developers remains below 5% of commits.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-08-27 - CANDIDATE: первая оценка

## Связи
- [[MCP как универсальный протокол агентной интеграции 2026-06-14]]
- [[Self-hosted суверенитет над агентной инфраструктурой 2026-06-14]]
- [[Human Verification Embedded in Agent Loops 2026-08-04]]
- [[Верификация и доверие к действиям агентов 2026-06-14]]
- [[Динамически расширяемая архитектура агентов 2026-06-14]]
