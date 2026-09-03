---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: SEMAPRAX establishes semantic graphs as a first-class intermediate
  layer between source and code generation, enabling deterministic agent inspection
  and replay-safe program changes—a novel architectural shift from text-centric to
  meaning-centric systems programming, though nascent and without production validation.
evidence_log:
- date: '2026-09-03'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: 36913f3c58c48a35140e60852f8612690c560264
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-09-03'
  verdict: CANDIDATE
---
# Agent-native systems programming language

**Дата:** 2026-09-03
**Репозиторий:** https://github.com/wavect/semaprax
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "An experimental systems programming language with a stable semantic program graph designed for humans and software agents."

## What Changes in the Ecosystem
SEMAPRAX introduces a deterministic semantic graph as a first-class artifact between canonical source and machine code generation, enabling agents to reason about program semantics before execution and replay changes with proof of correctness. This shifts the compilation model from text→AST→IR→binary to text→verified-graph→multi-target-backend, making semantic verification and agent-driven refactoring native operations rather than post-hoc analyses. Ownership and effect checking at the graph layer create a new verification boundary that did not exist in traditional systems language toolchains.

## Reasoning
SEMAPRAX is a pre-alpha (v0.2.0) systems language introducing a novel semantic graph architecture for agent-friendly program analysis and transformation. Its core novelty lies in the persistent @id identity and versioned semantic graph layer designed for agent introspection and replay-checked changes; this is a genuine architectural layer not found in mainstream compilers. Maturity is low (early prototype, pre-alpha, no production adoption signals) despite working examples and CI pipeline. State trend is Prototype because there is no evidence of community adoption or sustained momentum beyond initial research release.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims "agent-native systems programming language" with "stable semantic program graph" and "ownership" semantics. The manifest shows multiple crates for native hosting, Rust interop, WASM compilation, and "doctor" tooling, plus explicit @id-based identity preservation shown in the example. The file tree includes docs/, examples/, crates/ with components like semaprax-native-host, semaprax-offline-wasm-package, confirming multi-target compilation and semantic graph infrastructure. However, the pre-alpha badge and v0.2.0 status indicate this is early-stage. The core architectural claim (semantic graph as first-class citizen for agents) is structurally supported by workspace organization and example code, though "AI agents with payment capability" mentioned in the project description appears nowhere in README examples or manifest details.
Подтверждено: Да

**Novelty checklist:** New protocol? Partially—the semantic graph versioning and @id-based persistent identity mechanism represent a novel approach to source-semantics binding not standard in mainstream systems languages, though not yet formally specified as a protocol. New standard? No—it targets Rust/Clang/WASM backends, not a new standard. New architectural layer? Yes—the semantic graph as a query and replay interface between source and code generation is a new intermediate representation layer specifically designed for agent introspection and verification. New way of market interaction? No—this is a language, not a market mechanism.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** In 12 months, the project achieves stable v1.0 with documented adoption by at least one production AI agent system (observable via GitHub issues, papers, or public deployments) using the semantic graph for runtime verification or multi-agent coordination.
**Если ошиблась:** In 12 months, the project remains pre-alpha (v0.x), development activity declines to infrequent commits, and no public case studies emerge of agents using the semantic graph for real-world workloads beyond examples.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-03 - CANDIDATE: первая оценка

## Связи
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[Верификация и доверие к действиям агентов 2026-06-14]]
- [[Динамически расширяемая архитектура агентов 2026-06-14]]
- [[Верифицируемый_харнес_для_свопаемых_моделей 2026-07-27]]
- [[AI_Software_Engineering_Workflow_for_Agents 2026-08-13]]
