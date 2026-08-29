---
status: VALIDATED_SHIFT
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Agent-Safe Pipeline defines a new cryptographic trust boundary layer
  where agents propose immutable intents, independent policy engines evaluate them,
  human verification is embedded, and SafeExecutor consumes single-use grants—establishing
  portable standards for autonomous action governance.
evidence_log:
- date: '2026-08-15'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: ef197b962c7a83dfeb31aad9117283dc5d0e4783
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-08-15'
  verdict: CANDIDATE
- date: '2026-08-29'
  verdict: VALIDATED_SHIFT
---
# AI Agent Authorization Middleware

**Дата:** 2026-08-15
**Репозиторий:** https://github.com/decionis/agent-safe-pipeline
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "Agent -> immutable intent -> Decionis -> ALLOW / ESCALATE / BLOCK -> SafeExecutor -> API"

## What Changes in the Ecosystem
The ecosystem gains a portable, standardized trust boundary for agent execution: agents no longer possess downstream credentials or authorization logic, and actions flow through an independent policy engine before a verified human approval and single-use grant bind intent to execution. This shifts responsibility from distributed agent logic to centralized, auditable authorization, enabling agents and policies to evolve independently while maintaining cryptographic accountability across the entire action lifecycle.

## Reasoning
Agent-Safe Pipeline introduces an architectural pattern that separates agent proposal from action authorization through cryptographically-bound immutable intent capture and independent policy evaluation. While the components (logging, policy engines, human approval workflows) are known individually, the specific composition of intent immutability → independent verdict → verified human approval → single-use grant binding is a notable architectural layer that addresses the critical trust problem of autonomous agent execution. The project demonstrates production-level documentation, comprehensive threat modeling, and conformance testing, but adoption signals remain early (0.1.1 version, reference implementation status).

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** Yes. README claims an immutable intent capture system, independent Decionis policy verdict flow, human verification via Presence, and a SafeExecutor that consumes single-use intent-bound grants. The manifest confirms: IntentCapture, DecionisGate, SafeExecutor, and Presence coordination exist in packages/pipeline; three runnable examples (basic-agent, shopify-refund-agent, github-deploy-agent) demonstrate ALLOW/ESCALATE/BLOCK flows; ARCHITECTURE.md and THREAT-MODEL.md are present; conformance vectors and canonical-hash test harness are documented. The file tree structure (packages/pipeline, examples/, conformance/, docs/) aligns with the architectural claims made in the README.
Подтверждено: Да

**Novelty checklist:** New protocol: The canonical-hash immutable intent wire format (agent-safe-intent-v1.json conformance vectors) is a novel protocol specification. New standard: Yes—the conformance test vectors and portable intent format define an interoperable standard for agent-safe intent capture. New architectural layer: Yes—the trust boundary that separates agent proposal from authorization execution is a new layer absent in typical agent frameworks. New way of market interaction: Partially—the three-party model (agent, policy engine, executor) with human-in-the-loop approval via Presence introduces a new coordination pattern, though not fundamentally a new market mechanism. At least three of four criteria are met.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, the first production deployment in an enterprise or platform context demonstrates that the intent-bound grant model successfully prevents unauthorized agent action escalation while maintaining human approval audit trails.
**Если ошиблась:** Within 12 months, a high-profile incident occurs where an AI agent bypasses or circumvents the authorization boundary (e.g., grant reuse, intent tampering, Presence spoofing), or the project is abandoned without adoption beyond the reference implementation.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-08-29 - VALIDATED_SHIFT: карантин пройден (14+ дней), репозиторий активен - promote_candidates
- 2026-08-15 - CANDIDATE: первая оценка

## Связи
- [[Cryptographic Trust as Native Agent Architecture 2026-08-04]]
- [[Human Verification Embedded in Agent Loops 2026-08-04]]
- [[Верификация и доверие к действиям агентов 2026-06-14]]
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[MCP как слой интеграции сервисов 2026-06-14]]
