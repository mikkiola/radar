---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Rta-Smriti Brain is a novel local-first architectural layer that
  makes project state, decisions, and evidence explicitly queryable by AI agents through
  MCP, replacing context-rebuilding per session with verifiable, durable project cognition.
  Alpha maturity reflects functional MCP integration and documentation completeness,
  but limited production adoption evidence.
evidence_log:
- date: '2026-09-06'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 90e0c93b57a2f76c8009fd70138e4f1107c98f57
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-09-06'
  verdict: CANDIDATE
---
# Local-First Project Memory for AI Agents

**Дата:** 2026-09-06
**Репозиторий:** https://github.com/sulabhdubey/rta-smriti-brain
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "A sovereign local project-memory and evidence layer for AI coding agents. The `v1.1.0-alpha` prerelease adds preview-first trusted operation without turning the brain into an execution harness."

## What Changes in the Ecosystem
Rta-Smriti introduces a local, agent-accessible project-state abstraction layer that makes code context, decisions, and verification status explicit and reusable across agent sessions. Instead of agents rebuilding project understanding from scratch in each chat, they can query a persistent, evidence-grounded memory layer running on the developer's machine. This shifts from ephemeral agent-project interaction to verifiable, durable project cognition as a shared service between developer and AI tools.

## Reasoning
The project introduces a deterministic project-state layer with bitemporal truth, evidence verification, and MCP-mediated agent access—a notable architectural addition to the agent ecosystem. It is v1.1.0-alpha with documented lifecycle, cross-platform builds, CI/CD, and adoption signals (featured coverage), but remains in alpha with limited production evidence, warranting maturity=3. Novelty=4 reflects new architectural primitives (Project Cognition layer, evidence-aware memory protocol) without creating a fundamentally new market interaction pattern.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** Yes. README claims: (1) "deterministic Project Cognition projection" reconciling sources and decisions - manifest shows 40+ doc files including ARCHITECTURE.md, v1.1.0-alpha prerelease structure with "Trusted Lifecycle Supervisor"; (2) "local SQLite" indexing - pyproject.toml and rta_brain/ directory present; (3) "MCP server" integration - dashboard-src/, operator-tests/, and MCP references in docs; (4) "governance, context packs, verification" - docs/ folder contains RELEASE_VERIFICATION.md, usage guides; (5) "preview-first lifecycle" (v1.1) - package.json shows vite-based operator console. File tree supports the claims: Python backend (rta_brain/), React dashboard (dashboard-src/), test suites (operator-tests/, tests/), and comprehensive documentation structure all present.
Подтверждено: Да

**Novelty checklist:** New protocol? YES - MCP-compatible evidence and memory protocol with bitemporal truth and verification receipts for AI agents is not a standard protocol before this. New standard? PARTIAL - README describes "immutable task contracts, explicit acceptance and stop conditions" as bounded interaction standards, but primarily instantiated in this project. New architectural layer? YES - "deterministic Project Cognition projection" that reconciles indexed sources, decisions, observations into an explicit readiness/coverage/conflict layer between project and agent is a new architectural primitive for local-first agent memory. New market interaction? NO - this is not a new marketplace model or transactional mechanism.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** In 12 months, Rta-Smriti reaches v1.0 stable release, published documentation shows active adoption by at least 2 mainstream AI code editors (e.g., Cursor, Claude Code, Zed), and GitHub shows sustained monthly commits and real-world usage patterns in forks or public issue discussions.
**Если ошиблась:** In 12 months, the project remains at alpha or pre-release status with no stable v1.0 release, zero documented production deployments, and commit frequency declines to sporadic maintenance-only activity; or the architectural approach (verification-first Project Cognition) is superseded by simpler context-passing patterns that agents/IDEs adopt instead.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-06 - CANDIDATE: первая оценка

## Связи
- [[Local-First Agent Memory and Cognition Layers 2026-08-04]]
- [[MCP как универсальный протокол агентной интеграции 2026-06-14]]
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[Human Verification Embedded in Agent Loops 2026-08-04]]
- [[Self-hosted суверенитет над агентной инфраструктурой 2026-06-14]]
