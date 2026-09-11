---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: CTRLRun defines a new architectural layer for agent action governance,
  introducing formal state machines, cryptographic receipts, and explicit approval
  workflows that decouple AI model confidence from consequential execution permission,
  enabling structured human-in-the-loop control over agentic transactions.
evidence_log:
- date: '2026-09-11'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: de509a56242eae8e7bdc5720504ecd5dc8a36f05
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-09-11'
  verdict: CANDIDATE
---
# Execution Safety Layer for AI Agents

**Дата:** 2026-09-11
**Репозиторий:** https://github.com/CTRLRun/ctrlrun
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README (github.com/CTRLRun/ctrlrun)
  локация: не указана
  цитата: "A Python library that sits between the decision to act and the call that acts. A consequential action happens at most once, exactly as approved, and leaves a receipt."

## What Changes in the Ecosystem
CTRLRun introduces a formalized safety/approval layer as a distinct architectural primitive for agentic systems, moving from ad-hoc tool safety to declarative, stateful action governance. It enables the market to structure agent-executed transactions (refunds, grants, deployments) with cryptographic receipts and explicit approval/delegation workflows, decoupling AI confidence from action permission. This shifts agent frameworks from "model decides, execute blindly" to "model proposes, control layer enforces, human gates consequential acts."

## Reasoning
CTRLRun is a working Python library (v0.7.0 on PyPI) with active maintenance, test coverage, and documented examples, but has not reached the "widely adopted in production" stage that defines maturity level 5. It addresses a novel problem—formalizing safety guarantees for consequential agent actions—by introducing an architectural layer with state machines, approval workflows, and receipt chaining; this is more than incremental improvement on existing patterns and qualifies as novelty level 4. The project shows signs of gaining momentum (recent SPEC versions, CI/CD infrastructure, security hardening) rather than declining.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims CTRLRun is "a Python library that sits between the decision to act and the call that acts" with four core guarantees: (1) exact argument matching, (2) exactly-once execution, (3) unknown outcome detection, and (4) receipt keeping. The pyproject.toml confirms it is published as a production library on PyPI (version 0.7.0, Apache-2.0). The file tree shows src/, tests/, docs/, examples/, adapters/, and audit/ directories, consistent with a working system supporting multiple execution patterns (file-based and Postgres). The README demo is self-contained and runnable. README explicitly states MCP support as a detected pattern. All major claims—effect keys, ambiguous state handling, policy engines, delegation, and approval verification—are substantiated by the presence of test infrastructure and example configurations. Cross-validation passes: the architecture is documented and the file organization supports the stated capabilities.
Подтверждено: Да

**Novelty checklist:** Is this a new protocol? Partial—CTRLRun itself is not a protocol but implements protocol-like semantics (effect keys, state transitions, receipts) that formalize agent action safety. Is this a new standard? Yes—it proposes a de facto standard for "consequential action once exactly as approved" with an open SPEC (referenced in pyproject comments as "SPEC-v0.3" and "SPEC-v0.5"). Is this a new architectural layer? Yes—it explicitly positions itself as a layer "between the decision to act and the call that acts," creating a new control plane above tool execution. Is this a new way of market interaction? Partially—it enables new market interactions by allowing agents to operate under explicit approval and audit trails, but this is a consequence of the architectural layer, not the primary innovation. Three of four are strong affirmatives.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, CTRLRun is integrated into at least two major agent frameworks (e.g., LangGraph, OpenAI agents) as a native approval layer, or the SPEC achieves adoption by a competing safety library, confirming the architectural layer is becoming ecosystem-standard.
**Если ошиблась:** Within 12 months, CTRLRun remains niche (under 10k monthly downloads, no framework integrations beyond MCP), or a competing approach (built-in to a framework or from a larger vendor) obsoletes its standalone role.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-11 - CANDIDATE: первая оценка

## Связи
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[Human Verification Embedded in Agent Loops 2026-08-04]]
- [[Self-hosted_контроль_и_управление_агентами 2026-06-12]]
- [[Human-in-Loop_Agent_Verification_Loop 2026-07-29]]
- [[Верифицируемая_изоляция_для_self-hosted_агентов 2026-06-24]]
