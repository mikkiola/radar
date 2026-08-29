---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: Antifailure is a pre-1.0 testing orchestration layer that combines
  masked Postgres branches, network sandboxing, and agent-driven QA in disposable
  per-PR environments—novel architectural integration but prototype-stage production
  readiness, with significant adoption risk tied to multi-provider complexity and
  agent reliability.
evidence_log:
- date: '2026-08-29'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: ca65f7ca7ddeb21dc3b4da24261399ea79b35b49
license_spdx_id: NOASSERTION
license_baseline_origin: initial
verdict_history:
- date: '2026-08-29'
  verdict: CANDIDATE
---
# Production Stack Testing Automation

**Дата:** 2026-08-29
**Репозиторий:** https://github.com/antifailure/antifailure
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "A disposable copy of your production stack for every pull request. Masked Postgres branches, contained third-party APIs, agents that use the app like people, and load shaped like your real traffic."

## What Changes in the Ecosystem
Antifailure introduces a new architectural layer for pull-request-scoped testing: masked production database branches (with cryptographic verification), network sandboxing with granular interception modes (BLOCK/ALLOW/SANDBOX/CAPTURE/MOCK), and browser-driven agents that automate real-world workflows with video/trace capture. This shifts the testing paradigm from staging-environment drift and fixture limitations to deterministic, verified, production-shaped environments—moving QA automation from brittle assertions to agent-orchestrated end-to-end testing with built-in compliance verification (data masking attestation, query plan diffing, leak detection).

## Reasoning
Antifailure combines four known technologies (data masking, network namespacing, browser automation, database branching) into a novel integrated testing layer that runs as a disposable environment per PR. The maturity is prototype-grade (pre-1.0, explicit "under construction" status, component tracking by proven/written/planned states) with no evidence of production adoption beyond the authors. Novelty is high (4/5) because the architectural combination—verified masked data + sandboxed network + agent-driven workflow testing + deterministic replay—does not exist as a cohesive testing primitive in the ecosystem today.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims masked Postgres branches, sandboxed APIs, agent-driven testing with video/trace capture, automatic database migration review, network interception (BLOCK/ALLOW/SANDBOX/CAPTURE/MOCK modes), and support for Docker/Neon/Supabase/DBLab/RDS providers. File tree confirms architectural components: engine/ (likely core orchestration), runner/ (workflow execution), api/ (control plane), deploy/ (infrastructure setup), schemas/ (database logic), and tools/ for utilities. Status explicitly marked as "Pre-1.0 and under construction" with component tracking in docs/plan/STATUS.md. The manifest and provider interface abstraction are referenced but the file tree structure supports the claimed multi-provider, agent-driven architecture. No contradictions detected between claims and file organization.
Подтверждено: Да

**Novelty checklist:** New protocol: No, uses standard HTTP/SMTP/webhooks within the sandbox. New standard: No, no specification or protocol definition artifact evident. New architectural layer: Yes—the masked branch + network namespace sidecar + agent-driven verification layer is a novel testing infrastructure primitive that combines data masking verification, deterministic network interception, and multi-modal workflow automation in one coordinated system. New market interaction: Yes—disposable production-replica environments per PR with agent-driven QA is a new market interaction model that shifts QA from static fixtures/staging to dynamic, masked production mirrors.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, Antifailure reaches 1.0 release (announced in CHANGELOG), gains adoption by 3+ independent organizations cited in public case studies or GitHub stars exceed 2000 with documented production usage reports.
**Если ошиблась:** Within 12 months, Antifailure remains pre-1.0 with no major version release, gains no documented external adoption beyond the authors, or the project is archived/deprecated due to unresolved architectural complexity (e.g., network sandboxing maintenance burden, agent reliability issues, or provider integration fragility).

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-08-29 - CANDIDATE: первая оценка

## Связи
- [[Браузер как универсальный канал для агентов 2026-06-14]]
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[Self-hosted суверенитет над агентной инфраструктурой 2026-06-14]]
- [[MCP как слой интеграции сервисов 2026-06-14]]
- [[Инженерия_петель_для_долгоживущих_агентов 2026-06-22]]
