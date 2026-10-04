---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Bise introduces a persistent per-repo orchestration architecture
  where a main agent acts as team lead, automatically splitting tasks and managing
  sub-agents while keeping the human in focused flow—a novel architectural layer for
  multi-agent coordination, but currently pre-release with adoption signals absent.
evidence_log:
- date: '2026-10-04'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: c5eff5dcfd58604e9d97ade0b33a6f01c5c55bdd
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-10-04'
  verdict: CANDIDATE
---
# Multi-agent orchestration terminal interface

**Дата:** 2026-10-04
**Репозиторий:** https://github.com/gvergnaud/bise
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "meet your team lead. you stay in flow, it runs the agents. bise is a terminal app for multi-agent coding. there's one thread per repo. in it you talk to main, an agent that acts as your team lead: it splits your requests into jobs, starts an agent when a job needs one, answers their routine questions, and only comes back to you with the decisions that are yours."

## What Changes in the Ecosystem
Bise introduces a persistent stateful orchestration layer that keeps a main agent alive per repository, automatically managing sub-agent spawning, job scheduling, and context across sessions. This moves multi-agent interaction from ephemeral sessions to long-running coordinated workflows where the human stays in focus while agents handle delegation and routine decisions. The architectural shift is from "I manage agents sequentially" to "agents coordinate and I only handle real decisions"—reducing cognitive load in multi-agent scenarios.

## Reasoning
Bise demonstrates a novel architectural layer for multi-agent orchestration—a persistent team-lead agent managing sub-agents, task distribution, and user focus—but remains in early pre-release stage (macOS only, self-describing as "pre-release"). The implementation is substantive (complex file tree, voice mode, MCP integration) but adoption signals are absent from the README. Novelty is high (new coordination primitive not previously seen as a packaged interaction model), maturity is low (no production signals, alpha lifecycle).

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims a terminal-based multi-agent harness with capabilities including: (1) persistent per-repo threads with automatic agent orchestration; (2) main agent as team lead splitting tasks and managing sub-agents; (3) git worktree management; (4) voice mode (dictation and voice-to-voice); (5) MCP server integration; (6) agent-to-agent messaging coordination. The file tree shows: `.agents/`, `computer-use/`, `docs/`, `plugins/`, `prompts/`, `rust/`, `scripts/`, `site/`, `tests/`, and `bend/` directories. This structure aligns with a complex orchestration system with plugin architecture, multiple agent implementations, prompts library, and build/packaging infrastructure (`packaging/`, `run.sh`). However, no manifest was provided to cross-validate specific capability claims. The file tree is consistent with a sophisticated agent framework rather than a simple CLI tool, supporting the claimed orchestration model.
Подтверждено: Да

**Novelty checklist:** New protocol? No—uses existing MCP and LLM APIs. New standard? No—integrates standard protocols (MCP, OpenAI-compatible, Anthropic). New architectural layer? Yes—introduces a persistent stateful orchestration layer (main agent as team lead, per-repo threads, automatic job splitting and agent lifecycle management) that abstracts multi-agent coordination and maintains context across sessions. New market interaction? Yes—shifts from session-based interaction (Claude Code, typical ChatGPT) to always-on persistent team lead model where human stays in flow while agent handles delegation and routine decisions.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** In 12 months, bise achieves Linux release, gains documented production users (e.g., a publicly named team or company running it daily), and the GitHub repository shows 2k+ stars with active contributor community beyond the original author.
**Если ошиблась:** In 12 months, bise remains macOS-only, archived, or shows no meaningful adoption signals; the orchestration model is subsumed into Claude Code or other commercial products without sustained independent development.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-04 - CANDIDATE: первая оценка

## Связи
- [[Оркестрация множества коммерческих агентов 2026-07-23]]
- [[Local-First_Multi-Agent_Software_Platform 2026-09-17]]
- [[Персистентная_локальная_память_для_кодирующих_аген 2026-06-28]]
- [[Local-First_Project_Memory_for_AI_Agents 2026-09-06]]
