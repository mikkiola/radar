---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Factory is a novel runtime layer that abstracts the orchestration
  of coding agents through deterministic verification gates and CI/review enforcement,
  enabling autonomous agent contributions to software systems at scale with early
  signs of adoption momentum but low production maturity.
evidence_log:
- date: '2026-08-29'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: ac24f5d4a5ce91d8fdb34c2e791368093be7f269
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-08-29'
  verdict: CANDIDATE
---
# Self-improving agentic orchestration runtime

**Дата:** 2026-08-29
**Репозиторий:** https://github.com/watt-mind/factory
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "The factory that builds software — and itself. A runtime for self-improving agentic loops: the tracker is the control plane, git is the truth, CI is the gate."

## What Changes in the Ecosystem
Factory introduces an orchestration layer that decouples coding agents from process responsibility: agents become stateless workers, while the runtime becomes the standing control loop. This shifts the market model from "agent produces diff → human merges" to "agent produces diff → runtime verifies → human reviews provable artifact". The ecosystem gains a reusable primitive for agent-authored code pipelines across any GitHub/git-based repository, reducing friction for autonomous contribution workflows.

## Reasoning
Factory is genuinely novel as an architectural layer: it solves the process gap around coding agents with a purpose-built runtime that enforces verification gates and prevents agent-state fragmentation. Maturity is low (v0.1.0, young, sharp edges) despite active self-use; the badge showing autonomous PR merges indicates real usage momentum but not production hardening yet. State_value is "Growing" because the project is being actively maintained and used by its authors at scale (742 PRs/month), with clear adoption signals.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims factory is "a runtime for self-improving agentic loops" with a specific architecture: tracker as control plane, git as truth, CI as gate. The manifest confirms this via package.json keywords (agent, agentic, dispatch, orchestration, ci, coding-agent) and files: orchestrator/, event-runtime/, lib/runners/, and tools/ directories support the claimed event-driven routing and dispatch system. The badge badge shows 742 PRs merged autonomously this month, confirming active self-use. The root files include orchestrator scripts (linear-reaper, dispatch, merge, janitor) matching the claimed loop stages (Triage → agent-ready → PR → Done). However, the version is 0.1.0 and README states "Young software, used in earnest every day — expect sharp edges", indicating prototype-to-early-production transition rather than hardened deployment.
Подтверждено: Да

**Novelty checklist:** New protocol: Partially yes — factory establishes a formal coordination protocol between human ticketing systems, AI agents, and CI gates. New standard: Not explicitly; no formal spec is claimed. New architectural layer: Yes — the runtime layer that sits between coding agents (Claude, Gemini, Cursor) and git/CI as a deterministic control plane is novel; it abstracts agent dispatch, work-tree isolation, and verification-before-merge as a composable layer. New way of market interaction: Yes — it enables autonomous agent contributions to software that survive human code review, shifting from "agent as code suggester" to "agent as author in verified workflow".
Проходит: Да

## Falsifiable Hypothesis
**Если права:** In 12 months, factory reaches v1.0, receives adoption by 3+ public projects beyond watt-mind, and the badge reports 1000+ PRs merged autonomously across multiple repositories with zero critical security incidents.
**Если ошиблась:** In 12 months, the project remains at v0.x with only watt-mind's internal use, incident reports of agent commits bypassing intended review gates, or core abstractions (ControlPlane adapter, event-runtime) are rewritten due to architectural mismatch discovered in production.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-08-29 - CANDIDATE: первая оценка

## Связи
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[MCP как универсальный протокол агентной интеграции 2026-06-14]]
- [[Оркестрация множества коммерческих агентов 2026-07-23]]
- [[Human Verification Embedded in Agent Loops 2026-08-04]]
- [[Открытые протоколы координации агентов 2026-06-25]]
