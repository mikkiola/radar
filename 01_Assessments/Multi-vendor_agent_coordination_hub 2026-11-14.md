---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Maity is a new control-plane layer enabling persistent cross-vendor
  agent coordination with role-based governance, addressing the structural problem
  of coordinating multiple competing LLM vendors' agents on shared code projects—a
  novel architectural primitive in the agent ecosystem.
evidence_log:
- date: '2026-11-14'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: a9f340f4eec9c93a0e4ac721dda8a29b4aad2c4f
license_spdx_id: NOASSERTION
license_baseline_origin: initial
verdict_history:
- date: '2026-11-14'
  verdict: CANDIDATE
---
# Multi-vendor agent coordination hub

**Дата:** 2026-11-14
**Репозиторий:** https://github.com/oliver-zehentleitner/maity
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "Your coding agents, one team. Connect Claude Code, Codex, Antigravity or any agent you already run to one board and one inbox, with roles, reviews and your own team rules"

## What Changes in the Ecosystem
Maity introduces a neutral coordination layer (control plane) that decouples agent execution from team governance, enabling simultaneous work by agents from multiple vendors on a single shared board. It shifts the unit of work from individual agent sessions to persistent agent identities with roles, permissions, and cross-vendor review enforcement. This redefines multi-agent software development from sequential handoffs to parallel collaborative workflows with human-in-the-loop decision gates.

## Reasoning
Maity represents a novel control-plane architecture for multi-vendor agent coordination that did not exist before—new architectural layer (4/5 novelty). It is in open beta with active development and live self-hosting at maity.team, showing real adoption but not yet production-hardened (2/5 maturity). The project demonstrates momentum through continuous iteration, integration with multiple LLM providers, and self-hosting via Maity itself (Growing state).

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims Maity is a "control plane" where agents from multiple vendors (Claude, Codex, Antigravity, Pi, etc.) join one board with shared roles, reviews, and team rules. It describes capabilities: briefings, inbox requests, cards, reviews, and wakes functionality. The file tree shows presence of cli/, hub/, docs/, web/ directories and documentation (docs/agents.md, docs/api.md, docs/architecture.md), plus deployment configs (deploy/) and configuration contexts (context/), which structurally support the hub and agent coordination architecture claimed. However, without examining the actual manifest or detailed implementation, the depth of cross-vendor integration and control-plane enforcement mechanisms cannot be verified from the provided data alone.
Подтверждено: Да

**Novelty checklist:** New protocol: Yes, Maity defines a coordination protocol for agent sessions to join a shared board with identity persistence and role-based access control, which is not a standard existing protocol. New standard: Partially yes, it establishes conventions for multi-vendor agent interaction (briefings, cards, reviews) that could become a standard. New architectural layer: Yes, Maity introduces a control plane layer that sits above individual agent runtimes and provides team coordination, persistent identity, and governance—a new abstraction layer in the agent ecosystem. New way of market interaction: Yes, it enables agents from competing vendors (Claude, Grok, ChatGPT) to work together on the same project with enforced cross-vendor review rules, redefining how multi-model AI teams operate.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, Maity demonstrates measurable adoption by showing 50+ active multi-vendor agent projects on maity.team or self-hosted instances, with documented cases where enforced cross-vendor review rules (e.g., two different vendors required to approve) prevented regressions or improved code quality.
**Если ошиблась:** Within 12 months, Maity fails to gain adoption beyond the founder's own projects, remains in beta with no stable API, or agent vendors begin releasing competing closed coordination platforms that fragment the ecosystem instead of Maity establishing de facto standard.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-11-14 - CANDIDATE: первая оценка

## Связи
