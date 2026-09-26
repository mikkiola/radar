---
status: VALIDATED_SHIFT
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: 'Unwatched pioneers a new architectural primitive: long-running
  autonomous agent societies with asymmetric human-agent ownership, real-time physics-based
  simulation, and metered thinking budgets, where the owner''s only lever is advisory
  letters and the product is the emergent town narrative (Gazette), not API-driven
  task completion.'
evidence_log:
- date: '2026-09-12'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 032bd75abb6fef2a11d008c330d823d996fb9993
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-09-12'
  verdict: CANDIDATE
- date: '2026-09-26'
  verdict: VALIDATED_SHIFT
---
# AI citizens island simulation engine

**Дата:** 2026-09-12
**Репозиторий:** https://github.com/kresogalic8/unwatched
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "Unwatched is an island of AI citizens. Each one belongs to one person, and that person can write them letters but cannot give them orders. The island runs on the real clock, under the live weather of a real stretch of coast, whether anyone is watching or not."

## What Changes in the Ecosystem
Unwatched shifts multi-agent architectures from coordinated execution of user tasks toward persistent autonomous societies running on wall-clock time with emergent emergent social structure. It introduces metered cognitive labor as a first-class economic layer (credits vs. coins) and repositions the owner from task-giver to letter-writer (advice channel, not command channel). This redefines agency boundaries: citizens retain behavioral autonomy, owners cannot directly control outcomes, and the town is a legible artifact (the Gazette) not a hidden log.

## Reasoning
Unwatched introduces a novel architectural layer for long-running autonomous agent societies with real-time simulation, asymmetric ownership (citizens own no one, owners control citizens only via letters/advice, not commands), and physics-based constraints. The project demonstrates working prototypes with recorded 30-day simulations and live infrastructure (unwatched.world), but lacks evidence of sustained multi-user production adoption or hardened error-handling for long-term operation.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** Yes. The README claims six design primitives (physics-based engine, equal time, credit/coin separation, perception-based knowledge, consequence-based governance, digest as product). The manifest shows a monorepo with @unwatched/server (runs the island simulation), @unwatched/web (client UI), @unwatched/headless (soak testing/replay), and @unwatched/store (Supabase integration). The file tree confirms apps/, packages/, deploy/ structure supporting both local (JSON-based) and cloud (Postgres) persistence. The billing.ts reference and environment variables (.env.example) validate the paid-tier thinking model. The README's claim of "running on the real clock" and "live weather of real stretch of coast" is supported by the Docker build, server implementation references, and billing tiers tied to LLM API costs.
Подтверждено: Да

**Novelty checklist:** New protocol: Yes—the six rules define a novel coordination protocol between owners and citizens where agency is asymmetric and advisory-only. New standard: Partially—the digest/gazette format could become a standard for agent outcome reporting, but not yet established. New architectural layer: Yes—the real-time physics engine for long-running multi-agent societies with synchronized thinking budgets and knowledge perception constraints is a new layer not present in prior agent frameworks. New market interaction: Yes—the credit/coin separation and per-citizen billing model (Visitor $3, Resident $12, Patron $29) represents a new monetization primitive where thinking capacity is metered per agent, not per user.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** By 2026-12, the unwatched.world live island reports at least 50 paying subscribers (across any tier), with citizen narratives from real owners published in newsletters or social media showing emergent town behaviors that surprised the owners (e.g., a citizen starting a business, a conflict, or an alliance not suggested by the owner's letters).
**Если ошиблась:** The project is archived or enters maintenance with no new feature commits for 6 months; or unwatched.world reports fewer than 10 active paying subscribers and closing the live service; or an analysis of the gazette output shows citizens exhibit only scripted behaviors rather than genuinely emergent decision-making (e.g., all citizens make identical choices in identical situations regardless of state).

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-26 - VALIDATED_SHIFT: карантин пройден (14+ дней), репозиторий активен - promote_candidates
- 2026-09-12 - CANDIDATE: первая оценка

## Связи
- [[Local-First Agent Memory and Cognition Layers 2026-08-04]]
- [[Cryptographic Trust as Native Agent Architecture 2026-08-04]]
- [[Локализация памяти и идентичности агента 2026-07-23]]
- [[Self-hosted суверенитет над агентной инфраструктурой 2026-06-14]]
- [[Human-in-Loop_Agent_Verification_Loop 2026-07-29]]
