---
status: VALIDATED_SHIFT
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: h5i-orchestra is a novel architectural layer for reproducible multi-agent
  workflows using Git-backed sandboxed turns with neutral verification, but remains
  in early prototype (v0.1.0 alpha) with no signals of production adoption or real-world
  usage beyond tutorial examples.
evidence_log:
- date: '2026-08-05'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: 0b909a8365a1b1b61227a2fddfe140990d2a1293
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-08-05'
  verdict: CANDIDATE
- date: '2026-08-19'
  verdict: VALIDATED_SHIFT
---
# Python SDK for Multi-Agent Orchestration

**Дата:** 2026-08-05
**Репозиторий:** https://github.com/h5i-dev/h5i-orchestra
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "A real workflow must specify: who implements; who reviews whom; when an agent must revise its work; which candidates are independently tested; how the winner is selected; and when the selected change is applied to the original branch. Each agent works inside its own sandboxed Git worktree, so it cannot overwrite the original checkout or another agent's work."

## What Changes in the Ecosystem
The h5i-orchestra SDK introduces Git-backed sandboxed agent orchestration as a coordination primitive — each agent operates in isolation, work is journaled as Git artifacts, and selection happens through neutral verification (tests, reviews, comparison). This shifts multi-agent workflows from message-passing or sequential patterns into an auditable, reproducible, fork-and-merge model native to development work.

## Reasoning
h5i-orchestra introduces a novel architectural layer: Git-backed, sandboxed multi-agent workflows with neutral verification and auditable artifact selection. However, maturity is very early — version 0.1.0, alpha status, proof-of-concept implementation with examples but no signals of production adoption or real-world usage beyond tutorials and paper re-implementations. The project is in prototype phase with clear momentum (40 published patterns implemented, structured examples) but lacks production hardening and real-world deployment evidence.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims the SDK defines and executes multi-agent workflows with Git-backed artifacts, agent sandboxing in Git worktrees, review/revision cycles, testing, selection, and application as auditable workflows. The manifest shows version 0.1.0 in alpha status (Development Status :: 3 - Alpha), with zero runtime dependencies and pure stdlib implementation. The file tree includes examples/papers/ (40 published patterns), examples/tutorial/ (8 basic patterns), and src/h5i/ implementation. The async API and Conductor class in the quickstart match the examples structure. However, the manifest explicitly states "Deliberately zero runtime dependencies: the SDK is stdlib-only (asyncio + json + dataclasses) and all heavy lifting lives in the `h5i` binary it drives" — the actual orchestration engine is the external Rust `h5i` binary, not this SDK. The SDK is a thin Python wrapper around that binary, confirmed by the install instructions requiring separate `h5i` engine installation.
Подтверждено: Да

**Novelty checklist:** New protocol? Not exactly — it wraps existing agent protocols (Claude, Codex, etc.). New standard? Partial — it proposes a standard workflow model (who implements, who reviews, when to revise, which candidates to test, how to select winners, when to apply). New architectural layer? Yes — Git-backed sandboxed worktrees with journaled multi-agent turns and neutral verification form a new coordination substrate. New way of market interaction? No — it does not change how agents are compensated, acquired, or traded. The architectural layer (sandboxed multi-agent workflows with Git-backed artifacts and neutral verification) is structurally novel in the ecosystem.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, a major AI coding platform (Claude, GitHub Copilot, or similar) announces native support for h5i-orchestra workflows or adopts its Git-backed sandboxed multi-agent pattern as a standard orchestration layer.
**Если ошиблась:** Within 12 months, the project remains at 0.x version with no adoption signals beyond its own examples, and the h5i binary (external dependency) does not mature into production use across multiple agent runtimes.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-08-19 - VALIDATED_SHIFT: карантин пройден (14+ дней), репозиторий активен - promote_candidates
- 2026-08-05 - CANDIDATE: первая оценка

## Связи
- [[Оркестрация множества коммерческих агентов 2026-07-23]]
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[Верификация и доверие к действиям агентов 2026-06-14]]
- [[Открытые протоколы координации агентов 2026-06-25]]
- [[Self-hosted суверенитет над агентной инфраструктурой 2026-06-14]]
