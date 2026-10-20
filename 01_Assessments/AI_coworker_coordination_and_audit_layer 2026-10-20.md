---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Tedix is an early-stage, novel coordination layer for AI agents
  that introduces approval workflows, risk-stratified budgets, and audit trails—a
  new architectural primitive shifting agents from stateless tools to accountable
  coworkers, currently in beta with growing (but unproven) adoption momentum.
evidence_log:
- date: '2026-10-20'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 13c3bcafc0d15bca7ca49a7a35de457f44c9aa1c
license_spdx_id: AGPL-3.0
license_baseline_origin: initial
verdict_history:
- date: '2026-10-20'
  verdict: CANDIDATE
---
# AI coworker coordination and audit layer

**Дата:** 2026-10-20
**Репозиторий:** https://github.com/tedix-hq/tedix
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "Tedix gives your team AI coworkers, called **tedis**, for recurring work. They ask before risky steps, and every run leaves a record: what the tedi did, which tools it used, and who approved it."

## What Changes in the Ecosystem
Tedix introduces a coordination primitive for multi-stakeholder AI agent systems: Work Items as first-class entities with risk stratification, approval workflows, and immutable audit trails. This shifts the agentic ecosystem from "stateless tool use" toward "accountable agent employment" with explicit human approval gates and compliance records. Organizations can now integrate Claude, ChatGPT, and MCP clients as persistent "teammates" rather than stateless assistants, fundamentally changing how delegation, budgets, and risk governance operate in agentic workflows.

## Reasoning
Tedix is a beta-stage, actively developed platform that introduces a novel coordination layer for AI agents: Work Items with approval workflows, risk levels, budgets, and audit trails. It bridges the gap between stateless LLM chat and persistent, accountable agent employment. The MCP integration + approval + audit architecture is genuinely new to the AI agent ecosystem, though the platform is not yet production-hardened (beta status, limited public adoption signals). The project shows active development (recent GitHub source release), clear architectural vision, and multi-client integration strategy (Claude, ChatGPT, MCP), indicating growing momentum despite limited maturity.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims: (1) "AI coworkers" (tedis) that perform recurring work, (2) ask before risky steps with approval workflows, (3) maintain audit records of all actions. Manifest shows: monorepo with apps/ (API, OS, MCP gateway), packages/ (db, schemas, core logic), plugins/ (Claude/ChatGPT integration), and examples/ (supplier-review). File tree includes SECURITY.md, CONTRIBUTING.md, database migrations, MCP schema validation, and CLI tooling. The package.json scripts reference db migrations, MCP surface validation, and multi-workspace builds. The architectural pattern detection lists "MCP" and "Memory". The claimed ability to integrate with Claude, ChatGPT, and MCP-compatible clients is structurally supported by the plugins/ directory and multi-app architecture. The approval workflow and audit trail mechanics are consistent with the core concept of "Work Items carry an owner, a risk level and a budget" mentioned in README. The tech stack (Cloudflare Workers, D1, Durable Objects) aligns with a distributed agent coordination platform. No significant structural contradiction detected.
Подтверждено: Да

**Novelty checklist:** New protocol? YES - the combination of MCP gateway + approval workflow + audit trail for AI agents forms a novel coordination protocol not present in standard LLM or agentic frameworks. New standard? PARTIAL - Tedix adopts MCP (existing standard) but extends it with risk-aware approval and budget constraints, which is a layer above the standard itself. New architectural layer? YES - the "Work Items" abstraction with ownership, risk classification, and approval state represents a new layer between agent action planning and execution. New market interaction? YES - enables the market pattern of "AI agents with approval gates and audit trails that can be delegated as recurring coworkers"—a shift from stateless chat to stateful, accountable agent employment. At least one affirmative (actually three strong yeses) confirms novelty pass.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, at least one enterprise adopts Tedix in production for recurring AI agent workflows requiring approval sign-off, and publicly documents the use case or deployment size in a blog post, case study, or GitHub discussion, OR the GitHub repository reaches 3000+ stars with demonstrable user-submitted examples in discussions/issues, OR a major LLM platform (Anthropic, OpenAI, similar) officially integrates Tedix's approval/audit patterns into native agent orchestration.
**Если ошиблась:** Within 12 months, the GitHub repository receives fewer than 500 stars, no public case studies or enterprise adopter announcements emerge, the beta status is not lifted despite being available for over 18 months, or the core Tedix Cloud service shuts down or is delisted from the contact/onboarding page, signaling inability to sustain the platform or lack of real demand for approval-gated agents.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-20 - CANDIDATE: первая оценка

## Связи
- [[Human Verification Embedded in Agent Loops 2026-08-04]]
- [[Верификационный_шлюз_для_агентских_действий_Claude 2026-06-14]]
- [[Execution_Safety_Layer_for_AI_Agents 2026-09-11]]
- [[Local-First_Multi-Agent_Software_Platform 2026-09-17]]
- [[AI_Agent_Authorization_Middleware 2026-08-15]]
