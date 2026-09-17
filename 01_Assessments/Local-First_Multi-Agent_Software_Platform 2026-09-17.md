---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: TaskTrooper is a maturing local-first multi-agent coordination platform
  that introduces board-driven orchestration and role-based agent specialization with
  self-evolution loops, offering heterogeneous runtime support but facing uncertain
  production adoption at scale.
evidence_log:
- date: '2026-09-17'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: ee1cdd9649be28cdfff8c98b7b24dce1cd102f60
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-09-17'
  verdict: CANDIDATE
---
# Local-First Multi-Agent Software Platform

**Дата:** 2026-09-17
**Репозиторий:** https://github.com/makifbaysal/tasktrooper
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "A local-first agent platform for software teams of one. A board of tasks, a set of role agents (product manager, architect, backend, frontend, QA), and a runtime that hands each task to Claude Code (or another agent CLI) on your own machine"

## What Changes in the Ecosystem
TaskTrooper introduces board-driven agent orchestration as an architectural primitive—agents don't execute on manual trigger but react to column transitions on a Kanban board, automating task routing across role-specialized agents. It establishes local-first agent runtime as a structural pattern, embedding backend, database, and code execution on the developer's machine rather than cloud infrastructure. It enables multi-model agent teams where different agents can use different CLIs and providers simultaneously on the same board, breaking the single-model-per-team assumption.

## Reasoning
TaskTrooper combines existing components (Claude Code, MCP, LLM APIs, embeddings) into a novel orchestration pattern: board-state-driven agent workflows with self-evolution, local embedding/memory, and cross-runtime heterogeneity. The maturity is working-with-adoption (releases available, web presence, brew install, documented features) but not yet production-hardened at scale. The novelty lies in the architectural orchestration layer (Kanban-driven dispatch, role agents, self-reflection gates) rather than individual protocols—this is a meaningful system-level novelty (4/5). Growth trajectory appears positive: dedicated website, releases, homebrew distribution, and ambitious feature set suggest active development.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims a local-first agent platform with board coordination, role agents (product-manager, architects, developers, QA), Claude Code integration via MCP, semantic code search with local embeddings, self-evolution through reflection/golden gates, and multi-runtime agent support (Claude Code, Cursor, API providers). File structure confirms: desktop/ (Electron app), server/ (Go backend), evidence of embedded Postgres, MCP integration points, and agent configuration. The features are substantiated by file presence and documented capabilities, though full implementation details cannot be fully verified from manifest alone (manifest absent), the file tree structurally aligns with the claimed architecture (backend, desktop UI, docs, integration tooling).
Подтверждено: Да

**Novelty checklist:** New protocol? Partial - TaskTrooper uses standard MCP (Model Context Protocol) for agent integration, not a new protocol itself, but applies it in a novel way. New standard? No - relies on existing standards (GitHub API, cloud provider APIs, MCP). New architectural layer? Yes - the board-driven agent orchestration with column-based routing, role-based delegation, self-evolution reflection loops, and usage-limit-aware session resumption represent a new coordination paradigm not standard in agent frameworks. New way of market interaction? Yes - local-first with embedded runtime (no cloud, no account), combined with editable agent templates and cross-CLI support (Claude Code + Cursor + Antigravity + OpenCode on same board) introduces a new model of multi-agent team collaboration.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, TaskTrooper gains adoption by at least one mid-size software team (5+ developers) who publicly share workflows or case studies showing agents completing multi-step tasks end-to-end with board coordination, and the project reaches 2000+ GitHub stars with regular release cadence.
**Если ошиблась:** Within 12 months, the project is archived or moved to maintenance status due to insufficient adoption, or major features (self-evolution, multi-runtime support) are removed/deprecated as technically infeasible at the claimed scale.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-17 - CANDIDATE: первая оценка

## Связи
- [[MCP как слой интеграции сервисов 2026-06-14]]
- [[Self-hosted суверенитет над агентной инфраструктурой 2026-06-14]]
- [[Персистентная локальная память агентов 2026-06-25]]
- [[Оркестрация множества коммерческих агентов 2026-07-23]]
- [[AI_Software_Engineering_Workflow_for_Agents 2026-08-13]]
