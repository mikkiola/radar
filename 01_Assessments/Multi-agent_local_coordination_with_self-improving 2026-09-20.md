---
status: CANDIDATE_LOW_CONFIDENCE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: Sno Station introduces an open architectural layer for persistent,
  collaborative agent teams with human-verified self-improvement—combining cross-vendor
  coordination, encrypted local memory, and automated skill evolution—but is incomplete
  in shipping core integration pieces despite prototype evidence on authors' machines.
evidence_log:
- date: '2026-09-20'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: bbb01afeb56ac6058b426c56640885028979aae3
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-09-20'
  verdict: CANDIDATE_LOW_CONFIDENCE
---
# Multi-agent local coordination with self-improving skills

**Дата:** 2026-09-20
**Репозиторий:** https://github.com/sno-ai/sno-station
**Уверенность:** низкая
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "Sno Station is your agents' workstation: open-source software that turns the AI agents you already run, coding agents and general-purpose working agents alike, into one squad on your own machine. When one of them hits its rate limit, the other picks up with the context intact. They review each other's work, so fewer mistakes reach you. And the workspace they share gets smarter every night: it reads their sessions, proposes changes to their own skills, and waits for you to say yes."

## What Changes in the Ecosystem
Sno Station introduces a new architectural layer for persistent, self-improving agent teams: agents no longer operate in isolation but share encrypted workspace memory and can hand off tasks with context preservation across different vendors' harnesses. The RSI loop creates a feedback system where agent mistakes are automatically detected, proposed as skill improvements, and approved by humans—shifting from reactive to iterative agent capability refinement. This enables local-first, multi-vendor agent orchestration with human-verifiable automation of skill evolution.

## Reasoning
Sno Station presents significant novelty in agent coordination architecture (RSI self-improvement loop, cross-harness handoff, encrypted local memory) but remains in prototype stage: core packages exist but critical pieces (onboarding install, harness integrations, RSI automation) are explicitly marked "Not yet" or pending in the README. The evidence screenshots suggest real usage on the authors' own systems, but public availability and production hardening are incomplete.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** Partially verified. README claims: (1) shared encrypted memory on local machine - supported by package.json listing @snoai/sno-station-mem and crypto modules; (2) agent-to-agent messaging (Reach) - no explicit implementation files shown in manifest; (3) peer-review and handoff skills - mentioned as "Duo skills" but actual skill definitions not visible in provided files; (4) nightly RSI loop rewriting skills - described in README with evidence screenshots but actual automation code not shown in manifest; (5) multilingual memory storage - claimed but no language-specific implementation details in provided manifest. Core crypto and memory packages exist (@snoai/sno-station-core-crypto, @snoai/sno-station-mem), but agent harness integrations (mem-claw, mem-claude, mem-codex) are listed as pending or partial. The README explicitly states "Assembled in public" with opening "one piece at a time, starting 2026-09-18" and marks Install section "Not yet".
Подтверждено: Нет

**Novelty checklist:** New protocol? Partially - Sno Reach messaging layer appears novel for cross-harness agent coordination, but definition is incomplete. New standard? No - uses existing Claude API patterns. New architectural layer? Yes - the RSI (self-repair/self-improve) loop with human-in-loop skill rewriting is a new persistent learning layer for agents. New market interaction? Yes - the model is local-first, vendor-agnostic multi-harness coordination without cloud lock-in.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, the onboarding skill lands as the one-command install, all harness integrations (mem-claude, mem-codex, mem-claw) ship complete with documented API stability, and at least one third-party project successfully deploys Sno Station with documented results of cross-harness coordination or RSI skill improvement measurable in user reports.
**Если ошиблась:** Within 12 months, the Install section remains "Not yet", the RSI loop code does not ship as a reusable skill, at least two of the planned harness integrations are dropped or deprecated, or no public documentation emerges showing successful multi-harness coordination beyond the authors' internal evidence.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-20 - CANDIDATE_LOW_CONFIDENCE: первая оценка

## Связи
- [[Human-in-Loop_Agent_Verification_Loop 2026-07-29]]
- [[Cryptographic Trust as Native Agent Architecture 2026-08-04]]
- [[Персистентная локальная память агентов 2026-06-25]]
- [[Оркестрация множества коммерческих агентов 2026-07-23]]
