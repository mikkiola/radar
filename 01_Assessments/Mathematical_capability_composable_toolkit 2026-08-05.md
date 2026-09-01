---
status: VALIDATED_SHIFT
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Jacobian introduces separable verification-as-architecture for agent
  mathematics, decoupling solver discovery from checker-authorized trust via composable
  artifacts and role ownership, but remains early-stage (v0.8) with unproven adoption
  scaling beyond author ecosystem.
evidence_log:
- date: '2026-08-05'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
- date: '2026-09-01'
  event_type: ci_broken
root_commit_sha: 528500bf8691982d36d583dc7daf5f68e765cd32
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-08-05'
  verdict: CANDIDATE
- date: '2026-08-19'
  verdict: VALIDATED_SHIFT
---
# Mathematical capability composable toolkit

**Дата:** 2026-08-05
**Репозиторий:** https://github.com/morluto/jacobian
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README (description)
  локация: не указана
  цитата: "Jacobian gives AI agents small, composable mathematical operations rather than one opaque solver. An agent can construct an object, compute an invariant, search for a witness, and submit exact evidence to a separate checker. Every step remains visible as a typed result or artifact."

## What Changes in the Ecosystem
Jacobian introduces independent verification as a native architectural layer in agent-mathematics integration, decoupling evidence discovery from trust authorization. It transforms mathematical solvers from opaque black-box operations into composable, replayable capabilities with explicit artifact boundaries and role separation (agent, checker, provider). This shifts the agent ecosystem from solver-agnostic tool wrappers to verification-first capability design where every mathematical claim is bound to checker identity and certificate format.

## Reasoning
Jacobian achieves novelty by introducing verification-as-architecture and checker-role separation in agent tooling, but maturity remains low: version 0.8.0 with documentation-forward structure and limited evidence of production adoption beyond author ecosystem. It is actively maintained (PyPI + npm distributions, CI badges) and shows architectural clarity, but lacks the hardening and deployment scale of mature MCP tools. The state is Growing due to recent releases, multi-platform distribution setup, and documentation expansion.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims Jacobian is "an MCP server, CLI, and Python library...that gives AI agents a composable toolbox of mathematical capabilities with inspectable artifacts and independent verification." This is substantially supported by the manifest: pyproject.toml declares two entry points (jacobian CLI and jacobian-mcp server), specifies MCP==2.0.0 as a core dependency, and the file tree includes src/jacobian, src/jacobian_checkers, and docs/ confirming dual Python library + MCP adapter architecture. The "independent verification" claim is documented in verification-flow.jpg description and detailed capability portfolio across polynomial maps, algebra, linear algebra, graphs, SAT/SMT, and Lean. The manifest shows version 0.8.0 with structured dependencies (sympy, z3-solver, optional python-flint, cvc5) confirming deep mathematical backend coverage advertised in capabilities section. Installation patterns (npm launcher, uv setup, pip) match the "MCP server, CLI, and Python library" claim exactly.
Подтверждено: Да

**Novelty checklist:** Is this a new protocol? No—it uses the Model Context Protocol (MCP 2.0.0), an existing standard. Is this a new standard? No—it implements MCP and leverages existing solvers (sympy, z3, cvc5, Lean). Is this a new architectural layer? Yes—it introduces a distinct architectural separation between "agent strategy ownership," "capability exposure as one coherent outcome," "composable bounded values," and "checker-owned trust," creating a novel verification-first abstraction layer for mathematical agent tooling that decouples evidence-finding from verification-authorization. This separation (claim → search → independent check → verified record) is not a standard pattern in existing MCP integrations or mathematical solver stacks. Is this a new way of market interaction? Yes—it establishes a market-facing model where mathematical solvers are exposed as composable, inspectable, replayable artifacts with cryptographic separation between finder and checker roles, enabling third-party verification and trust delegation in agent-assisted mathematics.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, Jacobian becomes integrated into at least two independent agent frameworks (Anthropic Claude, OpenAI, or Google Gemini agent ecosystems) with published case studies showing verified mathematical claims tied to checker identity and replayable artifacts.
**Если ошиблась:** Within 12 months, Jacobian remains a single-author tool with no third-party verification adopters, no documented use in production agent systems, and releases plateau after v1.0 with minimal community contributions or dependent projects.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-08-19 - VALIDATED_SHIFT: карантин пройден (14+ дней), репозиторий активен - promote_candidates
- 2026-08-05 - CANDIDATE: первая оценка

## Связи
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[MCP как универсальный протокол агентной интеграции 2026-06-14]]
- [[Динамически расширяемая архитектура агентов 2026-06-14]]
- [[Верификация и доверие к действиям агентов 2026-06-14]]
- [[Верифицируемый_харнес_для_свопаемых_моделей 2026-07-27]]
