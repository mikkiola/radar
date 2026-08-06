---
status: VALIDATED_SHIFT
maturity_score: null
novelty_score: null
assertion_vector: null
evidence_log:
- date: '2026-08-05'
  event_type: ci_broken
root_commit_sha: null
license_spdx_id: MIT
license_baseline_origin: migration
verdict_history:
- date: '2026-08-01'
  verdict: VALIDATED_SHIFT
---
# Local Episodic Memory for Agents

**Дата:** 2026-08-01
**Репозиторий:** https://github.com/nossa-y/activity-frames
**Оценка:** СДВИГ
**Уверенность:** высокая
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v1.0
**Часть паттерна:** [[Local-First Agent Memory and Cognition Layers 2026-08-04]] (не новый сигнал - 1-е подтверждение, 2026-08-06)
**Источник:**
  файл: GitHub project description
  локация: не указана
  цитата: "Records your screen locally, compiles it into structured activity frames, serves them over MCP. No cloud, no LLM in the loop."

## What Changes in the Ecosystem
This project establishes local, verifiable episodic memory as a first-class architectural layer for AI agents independent of cloud infrastructure and LLM processing. It demonstrates that agent context and continuity can be built on client-side structured recording + MCP distribution rather than requiring centralized memory services. This shifts the infrastructure dependency from cloud-based memory systems to decentralized, locally-verified activity frames.

## Reasoning
Activity-frames addresses a fundamental gap in current agent architecture: persistent local memory without cloud lock-in or LLM-in-the-loop processing overhead. By combining local screen recording, structured compilation, and MCP protocol exposure, it establishes a new pattern where agent continuity becomes a sovereign, verifiable infrastructure primitive—not a service dependency. This is a new architectural layer, not merely a tool implementation.

## Falsifiable Hypothesis
**Если права:** Within 12 months, multiple agent frameworks adopt activity-frames-style episodic memory as a standard component, with at least two major agent platforms (Anthropic Claude agents, open-source frameworks) natively supporting local activity frame recording and MCP serving without requiring external memory services.
**Если ошиблась:** Activity-frames remains a niche utility for a narrow use case and does not influence mainstream agent architecture patterns; major frameworks continue relying on cloud-based memory services or in-context window management rather than adopting local episodic memory protocols.

## Оценка Claude
- 2026-08-01 - СДВИГ: первая оценка автоматически

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-08-01 - СДВИГ: первая оценка

## Связи
- [[Персистентная локальная память агентов 2026-06-25]]
- [[MCP как универсальный протокол агентной интеграции 2026-06-14]]
- [[Self-hosted суверенитет над агентной инфраструктурой 2026-06-14]]
- [[Локальная_плоскость_контроля_агентов 2026-06-19]]
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
