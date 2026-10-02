---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Herdsman is a novel orchestration layer introducing Chief/Manager/Lead/Agent
  role-based coordination and durable project-scoped work for coding-agent fleets,
  currently in early adoption with working integration but limited production deployment
  proof.
evidence_log:
- date: '2026-10-02'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 01f9b271383514af435cd3699627b205e153467e
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-10-02'
  verdict: CANDIDATE
---
# Pi agent orchestration and fleet management

**Дата:** 2026-10-02
**Репозиторий:** https://github.com/boadij/pi-herdsman
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "The orchestration layer between Pi and herdr. Pi Herdsman turns independent Pi sessions into a coordinated agent system, from one background Agent to parallel branch-based project work. Herdsman connects them through delegation, ownership, supervision, and project orchestration."

## What Changes in the Ecosystem
Herdsman adds explicit role-based orchestration (Chief/Manager/Lead/Agent) and durable project-scoped work coordination to the Pi + herdr ecosystem, enabling multi-agent parallel coding without collapsing responsibilities into a single controller. This changes how teams structure agent delegation from ad-hoc background tasks to managed, supervised, branch-tracked projects. The ownership and supervision model becomes a reusable architectural pattern for coding-agent fleets.

## Reasoning
Herdsman is a working orchestration layer (v0.18.0 published, CI/CD active, clear integration points) positioned at the junction between two established systems. It introduces novel coordination semantics and role hierarchy that didn't exist before, but maturity is limited to early adoption—no visible production fleet reports yet, and the pattern is still stabilizing.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** YES. README claims orchestration of Pi coding agents with background agents, parallel/nested delegation, project management through Manager role, and owned token usage tracking. The manifest confirms pi-extension architecture in package.json (piHerdsman.runtime specifying Pi 1.0.0 and herdr 0.9.3 integration), published npm package (version 0.18.0), and file tree shows docs/, extension/, docker/ supporting claimed capabilities. The skill-based architecture and herdr integration point confirmed in package.json pi.extensions field.
Подтверждено: Да

**Novelty checklist:** Is this a new protocol? PARTIALLY—it defines coordination semantics (supervision hierarchy, ownership trees, branch-based project durability) between Pi and herdr that don't exist in the wild separately, though each component is pre-existing. Is this a new standard? YES—the Chief/Manager/Lead/Agent role-based coordination model with explicit ownership and supervision boundaries is a new formalization in the multi-agent coding space. Is this a new architectural layer? YES—Herdsman explicitly positions itself as "the orchestration layer between Pi and herdr," adding a coordination and delegation abstraction above both. Is this a new way of market interaction? NO—it's open-source tooling for existing developer workflows, not a new market mechanism.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, Herdsman sees adoption by at least 3 independent teams managing parallel coding-agent projects in production, evidenced by GitHub discussions or issues from projects outside earendil-works/herdrdev org, with sustained npm download growth &gt;50% month-over-month.
**Если ошиблась:** Within 12 months, the project receives no substantive external PRs or adoption signals; version remains stuck below 1.0; or the coordination model is deprecated in favor of a simpler Pi-native extension (indicating the orchestration layer failed to become a durable pattern).

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-02 - CANDIDATE: первая оценка

## Связи
- [[Local-First_Multi-Agent_Software_Platform 2026-09-17]]
- [[Оркестрация множества коммерческих агентов 2026-07-23]]
- [[Локализация памяти и идентичности агента 2026-07-23]]
