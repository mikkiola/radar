---
status: CANDIDATE_LOW_CONFIDENCE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: axstream compiles agent computer-use tasks into streaming JSONL
  macros executable at 100ms per action with outcome-verified clicks via a four-rung
  resolution ladder (AX element, OCR anchor, visual patch, window pixel), enabling
  deterministic replay and caching where agents currently re-screenshot and re-reason.
evidence_log:
- date: '2026-08-08'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: 904a251470d967a70dc2866463cc99be7c16bbc8
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-08-08'
  verdict: CANDIDATE_LOW_CONFIDENCE
---
# Streaming macro compiler for agent task automation

**Дата:** 2026-08-08
**Репозиторий:** https://github.com/milind-soni/axstream
**Уверенность:** низкая
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "A coding agent drives a Mac the expensive way: screenshot → reason → one click → screenshot again, seconds and tokens per step. axstream replaces the repeat of any task with a deterministic macro: clicks resolve through a verified ladder (accessibility element → OCR text anchor → visual patch → window-relative pixels) and every macro ends with an assert that only passes when the task actually happened."

## What Changes in the Ecosystem
The ecosystem shifts from real-time screenshot-reason-click loops (tokens and seconds per action) to deterministic compiled macros (100ms per action, verified-or-refused, never trusted until outcome gate passes). This introduces a new cached-action abstraction layer: agents author macros once (via streaming JSON), executors replay them instantly with cryptographic outcome verification, and the flywheel (do once → save → replay forever) becomes a primitive for agent task composition.

## Reasoning
axstream introduces a novel streaming action protocol and verified click ladder (AX→OCR→patch→pixel) that converts expensive online agent loops into compilable, cacheable, verifiable macros—a structural shift in agent architecture. However, at version 0.3.1 with no public adoption signals, it remains a well-engineered prototype without production validation.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims fast deterministic macro replay with a four-rung verified click ladder (AX element → OCR → visual patch → window pixel), MCP/skill integration for Claude agents, and per-action streaming verification. The manifest confirms axstream 0.3.1 is a PyPI package with accessibility/Vision dependencies for macOS, includes MCP integration (.mcp.json), skill definitions (skills/ directory), and a SPEC.md file. The file tree lists axstream/, commands/, tests/, docs/ directories supporting the claimed CLI, macro file system, and replay engine. However, the manifest and file list do NOT verify: (1) actual agent adoption beyond the author (Claude Code plugin integration is claimed in README but not confirmed in structure), (2) production use signals—version 0.3.1 with 119 tests suggests early-stage, (3) the claimed "34–78× speedup" or verification guarantees are not validated in manifest or file structure. The core technical claim (verified action replay via click ladder) is structurally sound but adoption markers are missing.
Подтверждено: Нет

**Novelty checklist:** New protocol? YES—the axstream SPEC.md (referenced but not quoted in detail) defines a line-oriented JSONL action protocol with streaming semantics and late binding. New standard? Partially—it integrates with Agent Skills standard and MCP, but does not itself define a new standard, rather implements existing ones. New architectural layer? YES—the verified click ladder (AX element→OCR→patch→pixel resolution with outcome gates) is a novel trust architecture for cached agent replay that did not exist before. New way of market interaction? NO—it is a task automation tool, not a market mechanism.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** In 12 months, axstream macros are used in >10% of Claude Code computer-use workflows, or a competing agent platform (Codex, Cursor, Windsurf) integrates the verified click ladder pattern natively.
**Если ошиблась:** In 12 months, the project is archived, or axstream replay usage remains <1% of agent computer-use tasks, or the click ladder introduces unrecoverable errors in >5% of macro executions in production.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-08-08 - CANDIDATE_LOW_CONFIDENCE: первая оценка

## Связи
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[MCP как универсальный протокол агентной интеграции 2026-06-14]]
- [[Верификация и доверие к действиям агентов 2026-06-14]]
- [[Human Verification Embedded in Agent Loops 2026-08-04]]
- [[Динамически расширяемая архитектура агентов 2026-06-14]]
