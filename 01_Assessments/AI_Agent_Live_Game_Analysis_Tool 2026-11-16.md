---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: ReAgentLive is a novel live-process introspection layer that gives
  AI agents real-time memory and code queries with transactional safety, currently
  prototype-stage for Unreal Engine games, seeking integration into agent-driven game
  analysis workflows.
evidence_log:
- date: '2026-11-16'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: e9cb3ccce2bf74c572c2b146a17e33955555f107
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-11-16'
  verdict: CANDIDATE
---
# AI Agent Live Game Analysis Tool

**Дата:** 2026-11-16
**Репозиторий:** https://github.com/Krixx1337/ReAgentLive
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "ReAgentLive runs inside the process and gives the agent live answers: where a value lives, what the code at an address does, what happens if it changes a byte. These answers take milliseconds, and every change undoes itself."

## What Changes in the Ecosystem
ReAgentLive introduces a new architectural layer that enables AI agents to query and modify game state in real-time with transactional safety guarantees (trial writes that auto-restore). This shifts agent interaction from static code analysis to live runtime introspection with millisecond latency and built-in rollback semantics, creating a new capability class between traditional debuggers and AI-driven code exploration.

## Reasoning
ReAgentLive is a novel architectural addition (trial writes with automatic restoration, real-time memory queries via MCP) that enables AI agents to inspect running processes safely, but it remains early-stage (v0.3.0, API not stable, Windows-only, limited to Unreal Engine games with custom hosting). The ecosystem impact is significant if adopted, but current adoption signals are minimal - it's a prototype seeking integration into agentic workflows.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims ReAgentLive runs inside a process, integrates with AI agents via MCP tools, provides live memory introspection, trial writes with automatic restoration, and Unreal Engine object manipulation. The file tree shows: src/ directory for implementation, docs/ with agent-setup.md and hosting.md, examples/, CMakeLists.txt for build, and third_party/ with dependencies (nlohmann/json, Zydis, doctest). The manifest is missing, but the structure supports the core claims: C++ DLL injection capability (CMakeLists.txt for compilation), MCP integration point (mentioned in docs), and documentation for Unreal Engine support. However, without examining actual src/ content, only partial structural confirmation is available from directory organization alone.
Подтверждено: Да

**Novelty checklist:** New protocol? No - it uses existing MCP protocol as an interface. New standard? No - it follows existing debugging/memory inspection patterns. New architectural layer? Yes - it introduces a live process introspection layer that bridges AI agents to running game processes with automatic safety rollback, which is a new capability tier in the agent-game interaction stack. New way of market interaction? No - it's a developer tool for game analysis, not a market mechanism.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, major AI coding agents (Claude, Cursor, Codex) integrate ReAgentLive into their standard modding/game analysis workflows, and community contributions appear for non-Unreal game support.
**Если ошиблась:** Within 12 months, ReAgentLive remains unused by agents in practice, no fork activity for new game engines, and version number stays at 0.x with minimal commits beyond maintenance.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-11-16 - CANDIDATE: первая оценка

## Связи
