---
status: VALIDATED_SHIFT
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Hedgehog moves AI-assisted development from prompt-dependent improvisation
  into mechanically-enforced workflows using explicit dependency graphs, deterministic
  generation, and phase gates—a novel architectural layer that encodes discipline
  into codebase structure rather than agent memory.
evidence_log:
- date: '2026-08-13'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: ee0f3b630df1e243b742c9214099ab976f5b73de
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-08-13'
  verdict: CANDIDATE
- date: '2026-08-27'
  verdict: VALIDATED_SHIFT
---
# AI Software Engineering Workflow for Agents

**Дата:** 2026-08-13
**Репозиторий:** https://github.com/skyf0xx/hedgehog
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "Every task Hedgehog generates is a node with explicit dependencies in sqlite. Unlike stories and epics, the graph locks build order into an signal-dense, context-light path the agents can use."

## What Changes in the Ecosystem
Hedgehog shifts the AI-in-engineering problem from "better prompting" to "better system architecture." It encodes build order, dependencies, and verification into the codebase structure itself, allowing agents to operate within mechanical constraints rather than memorizing instructions. This decouples context load from project scale—a foundational difference in how AI-assisted development can scale.

## Reasoning
Hedgehog introduces a mechanical enforcement architecture for AI-driven code generation using explicit dependency graphs, TDD layering, and phase gates—moving beyond prompt-engineering into structural guarantees. The project is actively maintained (version 4.2.3, NPM distribution), gaining adoption signals (npm downloads badge, multi-agent support), yet lacks visible production deployments at scale.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims: (1) a disciplined build workflow with explicit dependency graphs stored in SQLite, (2) deterministic code generation via templates/generators, (3) integration with multiple agent hosts (Claude Code, Cursor, Gemini CLI), (4) adoption onto existing codebases without stack conversion. The manifest confirms: bin/cli.mjs entry point, agents and skills directories, golden-cores for template patterns, vendor-skills including BMAD, multi-host configuration. File tree shows .hedgehog/ (config), src/agents, src/skills, src/golden-cores, src/templates supporting the workflow claims. The architecture is present and structurally coherent.
Подтверждено: Да

**Novelty checklist:** New protocol? No—uses standard BMAD planning + TDD. New standard? Partially—proposes a mechanical build-order standard (SQLite dependency graph, phase gates) that could become one, but currently author-specific. New architectural layer? Yes—the constraint layer (enforced scoping, dependency-locking, deterministic generation) between agent reasoning and code output is architecturally novel. New market interaction? Yes—shifts AI coding from per-prompt negotiation to persistent, verified, constraint-driven workflows installed into the repository itself.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, Hedgehog's dependency-graph model becomes adopted by competing AI agent frameworks (e.g., Anthropic's own agent scaffolding, open-source competitors) as a standard way to structure multi-step coding workflows, increasing adoption velocity beyond single-author use.
**Если ошиблась:** Within 12 months, the project stalls at &lt;5K weekly npm downloads, major agent platforms (Claude, Cursor, Gemini) release native equivalents that make Hedgehog's CLI wrapper redundant, or no public case studies emerge showing production codebases shipped using Hedgehog's discipline.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-08-27 - VALIDATED_SHIFT: карантин пройден (14+ дней), репозиторий активен - promote_candidates
- 2026-08-13 - CANDIDATE: первая оценка

## Связи
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[Оркестрация множества коммерческих агентов 2026-07-23]]
- [[Динамически расширяемая архитектура агентов 2026-06-14]]
- [[Human Verification Embedded in Agent Loops 2026-08-04]]
- [[Слой_контроля_качества_для_ИИ-агентов 2026-06-17]]
