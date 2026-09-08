---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Click introduces revision-aware verification evidence reuse for
  agent iterations via protocol-defined safety policies and commit-backed shard orchestration,
  positioned as a new architectural layer above existing test tools, currently at
  early adoption with high novelty but low production maturity.
evidence_log:
- date: '2026-09-08'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 886e46589977ae9121141480e00fa9ab653c72b9
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-09-08'
  verdict: CANDIDATE
---
# Incremental verification for AI coding agents

**Дата:** 2026-09-08
**Репозиторий:** https://github.com/grapefruit0205/click
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "Click provides incremental verification for coding agents. It records which checks ran, what changed, and whether an earlier result still applies through revision-aware evidence. Click does not replace Nx, Bazel, pytest, or Jest. It sits above existing verification tools and manages which verification evidence remains applicable across AI-agent iterations."

## What Changes in the Ecosystem
Click introduces a verification-centric intermediate layer that transforms how iterative agents reuse test results. Instead of re-running full test suites on every iteration, the ecosystem can now make fine-grained, policy-backed decisions about which checks remain valid. This shifts verification from a stateless tool call into a stateful, auditable process with explicit reuse contracts, changing the cost/speed tradeoff for agent-driven development workflows.

## Reasoning
Click is a novel architectural layer (protocol + standard) that sits above existing verification tools and manages evidence lifecycle across AI-agent iterations through revision-aware reuse rules and policy-driven sharding. However, maturity is still low: the project is at v0.94.1, distributed as a Codex plugin (not widely adopted beyond that ecosystem), has limited documentation of production usage, and the README emphasizes it "does not prove that the code is correct" and acknowledges "known regressions." The file tree shows active development (hooks, skills, docs, evals) and momentum indicates growth within the agent-development niche, but adoption signals remain constrained to Codex users.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims: (1) incremental verification that records which checks ran and what changed; (2) revision-aware evidence with reuse rules; (3) automatic sharding of test suites; (4) local dashboard with multi-language support; (5) two operating modes (Evidence default, Guarded opt-in). File tree shows: .click/ config directory, hooks/, skills/ (containing Click implementation), tests/, docs/ with verification profiles and evidence shards references, VERIFICATION_EFFICIENCY.md, RELEASE_NOTES.md, and specific references to evidence-reuse.json and evidence-dependencies.json policies. The directory structure and document titles (evidence-shards-v1, authoritative-observer-v2, verification-profiles) structurally support the README's claims about policy-driven reuse decisions, sharding orchestration, and revision-aware evidence management. Dashboard, multilingual docs, and hook system are mentioned in README and reflected in file tree. Cross-validation PASSES.
Подтверждено: Да

**Novelty checklist:** Is this a new protocol? YES - Click defines a revision-aware verification protocol with explicit reuse rules (same revision, committed safe-change policies, authoritative input observation) that sits above existing test runners and manages evidence lifecycle. Is this a new standard? YES - the .click/evidence-reuse.json and evidence-dependencies.json schemas represent a new verifiable contract format for test reuse decisions in iterative agent workflows. Is this a new architectural layer? YES - Click is explicitly positioned as a layer above existing tools (Nx, Bazel, pytest, Jest) that manages verification evidence state and reuse applicability across iterations. Is this a new way of market interaction? PARTIAL - it changes how coding agents and verification workflows interact, introducing an approval/contract workflow (Guarded mode) and evidence-based reuse negotiation, but this is more a consequence of the architectural layer than an independent market innovation.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, Click is integrated into at least two major agent development platforms (beyond Codex) or demonstrates >50% reuse-rate across a tracked agent-driven codebase, with documented case studies showing token/latency reduction from evidence reuse.
**Если ошиблась:** Within 12 months, Click remains a single-ecosystem plugin (<0.5% adoption outside Codex), the v0.95+ release delays beyond 6 months with no production user testimonials, or a competing simpler reuse strategy (e.g., caching at the LLM context level) makes Click's overhead unjustified for mainstream agent workflows.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-08 - CANDIDATE: первая оценка

## Связи
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[Human Verification Embedded in Agent Loops 2026-08-04]]
- [[AI_Software_Engineering_Workflow_for_Agents 2026-08-13]]
- [[Верифицируемая_изоляция_для_self-hosted_агентов 2026-06-24]]
