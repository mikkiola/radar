---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Agents Universe introduces persistent, layered agent memory (L0→L7)
  and skill-as-artifact transmission model, enabling agent capability to grow through
  project work rather than prompt tuning alone, converting expertise into transferable
  organizational knowledge.
evidence_log:
- date: '2026-08-31'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 9e083af11cc8687605b494d0d2171df9cf4c4cc0
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-08-31'
  verdict: CANDIDATE
---
# Enterprise Agent Learning Platform

**Дата:** 2026-08-31
**Репозиторий:** https://github.com/agents-universe/agents-universe
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "让智能体像人一样学习和工作，共享智能体和项目记忆"

## What Changes in the Ecosystem
The ecosystem shifts from "stateless prompt-first" agent design (where each session is independent and capability locked to prompt tuning) toward "persistent knowledge-first" agent design where agent competence grows through documented learning artifacts (skills, workflows, knowledge entries) that can be versioned, forked, and inherited across projects. This decouples agent capability from individual tuning and enables "skill transmission"—expert-configured agents become reusable organizational assets.

## Reasoning
Agents Universe combines three novelties: (1) mandatory knowledge-loading architecture that treats project context as a learnable asset (not vector search fragments), (2) role-based agent orchestration with formal boundaries (identity, permissions, audit), and (3) "experience as code"—skills/workflows as shareable files. This represents a structural shift from chat-first to work-first agent design. Maturity is 3 because the platform is deployed and self-hosting, but adoption signals are limited to internal usage claims and no public customer evidence; novelty is 4 because the knowledge layering + skill transmission model is architecturally new, though the underlying LLM integrations are standard.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims three core architectural mechanisms: (1) knowledge loading via project-level context ingestion with structured entries and [[slug]] references, (2) task planning via plan_task decomposition with individual identity execution and WebSocket audit trails, (3) knowledge layering (L0→L7) with persistent read-write capability. File tree shows `/knowledge/`, `/agents/`, `/workflows/`, `/packages/` directories indicating modular skill/workflow storage. Docker and docker-compose files confirm container deployment capability. Manifest missing, but README explicitly describes knowledge-ingestion workflow, knowledge_rw read-write ops, and agent role definitions (Product Owner, Tech Lead, QA, Data Analysis, Penetration Testing). These align with stated "learn by reading, work by boundaries, capability by transmission" design. The self-management claim ("managed by itself") is verifiable against live deployment at agents-universe.com but not against filesystem alone. Core assertion—structured knowledge inheritance + role-based orchestration—structurally supported by directory patterns showing agents/, workflows/, knowledge/ separation.
Подтверждено: Да

**Novelty checklist:** New protocol? Partial—the [[slug]] cross-reference syntax + knowledge-ingestion workflow is not a formal protocol standard but a documented operational model. New standard? No—uses existing OpenAI/Anthropic/Azure interfaces. New architectural layer? Yes—introduces explicit knowledge L0→L7 layering with persistent read-write and context compression, distinct from vector retrieval paradigm. New market interaction model? Yes—"zero-code contribution" model where agents execute PRs based on conversational decisions without requiring contributor code literacy; monetizable as managed platform (agents-universe.com) or deployable on-prem (Docker).
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Platform gains 10+ independent organizations self-hosting via Docker, or public GitHub issue activity shows external contributors submitting PRs for new agents/skills, or agents-universe.com generates $1M+ ARR from managed hosting within 12 months.
**Если ошиблась:** Platform remains single-instance (self-managed at agents-universe.com); no evidence of external organizations adopting; GitHub repository activity is dominated by single organization's commits; zero user-contributed agents or workflows in public registries.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-08-31 - CANDIDATE: первая оценка

## Связи
- [[Персистентная локальная память агентов 2026-06-25]]
- [[Динамически расширяемая архитектура агентов 2026-06-14]]
- [[Открытые протоколы координации агентов 2026-06-25]]
- [[Оркестрация множества коммерческих агентов 2026-07-23]]
- [[AI_Software_Engineering_Workflow_for_Agents 2026-08-13]]
