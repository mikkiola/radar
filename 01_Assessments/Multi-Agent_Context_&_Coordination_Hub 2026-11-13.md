---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: aisync is a novel local hub that introduces cooperative file claims,
  hash-chained verification, and mid-session rule injection as new coordination primitives
  for multi-agent AI coding workflows; it demonstrates working proof-of-concept with
  internal dogfooding but lacks production-scale adoption outside the author's ecosystem.
evidence_log:
- date: '2026-11-13'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 5909a8bc46504619dc2aaf436f25ee0bfca01ecd
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-11-13'
  verdict: CANDIDATE
---
# Multi-Agent Context & Coordination Hub

**Дата:** 2026-11-13
**Репозиторий:** https://github.com/MaxonT/aisync
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "aisync is a **local, verifiable hub** (`~/.ai-sync/`, a git repo) designed for multi-agent workflows: Context management: share and 3-way-sync rules; load core context up front and inject relevant context on demand, including mid-session updates where hooks are available. Multi-agent coordination: declare file claims, detect overlapping claims (exit code 3), release ownership, and surface blockers and other agents' activity. Observability & verification: inspect agent activity, blockers, and health through the journal, status reports, and board; `aisync verify` checks the journal's hash chain for tampering."

## What Changes in the Ecosystem
aisync introduces a shared coordination and context layer that sits between multiple AI coding agents, removing the isolation of their working contexts and file ownership. Agents previously worked in silos with no overlap detection, conflicting edits, or shared audit trail; aisync adds cooperative file claims, mid-session rule injection, and hash-chained verification. This shifts multi-agent workflows from disconnected parallel work to coordinated, observable collaboration within a single local git-backed hub.

## Reasoning
aisync is a working proof-of-concept with early adoption signals (6,700+ real journal events from 7 tools, active dogfooding, three native hook integrations). It introduces novel coordination primitives (cooperative file claims, overlap detection, hash-chain verification) and a new architectural tier (local verifiable hub) that did not exist before. However, it remains pre-1.0 (v0.2.5), lacks widespread production adoption beyond the author, and depends on agents voluntarily adopting its protocol—it does not enforce coordination at the OS level.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** YES. README claims: (1) native hooks for Claude Code, Codex, Cursor for mid-session news delivery; (2) cooperative file claims with overlap detection (exit code 3); (3) hash-chained journal with `aisync verify` for tamper detection; (4) MCP server, CLI, and shared instruction file integrations; (5) layered rule loading (When/Do/Not format). The manifest confirms Python 3.11+ packaging with optional MCP dependency, zero core dependencies (stdlib-only). File tree shows ai_sync/ module, tests/, docs/ (including install instructions, board, how-it-works), and CLI entry point at ai_sync.cli:main. The pyproject.toml keywords list claude-code, codex, cursor, mcp, coordination. The README demonstrates working two-agent overlap detection with exit code 3 and journal logging. The 6,700+ journal events from 7 tools over 4 weeks proves active dogfooding. All core claims are structurally supported.
Подтверждено: Да

**Novelty checklist:** New protocol: YES—cooperative file claims with overlap detection (exit 3) and hash-chained journal verification is a new coordination protocol for multi-agent workflows not standardized elsewhere. New standard: PARTIAL—While/Do/Not rule format is a structured approach but not yet a formal standard. New architectural layer: YES—aisync introduces a local verifiable hub layer between agents and file systems, distinct from agents themselves or existing orchestration. New market interaction: MINIMAL—primarily developer tool layer, not a new market mechanism. At least two of four are clearly yes.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, at least two major AI coding agent platforms (e.g., Claude Code, Codex, or Cursor) publicly announce integration with aisync's hooks or the aisync protocol is adopted in a competing or complementary multi-agent coordination tool, indicating structural lock-in of this coordination pattern.
**Если ошиблась:** Within 12 months, the project remains at or below v0.3.x, shows no new integrations beyond the initial three (Claude Code, Codex, Cursor), and the GitHub activity (commits, issues, stars) falls below one action per week, indicating the novelty was exploratory but failed to gain traction as a real coordination layer.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-11-13 - CANDIDATE: первая оценка

## Связи
- [[Локальный_мозг_агента_через_MCP_интеграцию 2026-07-09]]
- [[Локальный_профиль_агента_из_логов_Claude 2026-07-10]]
- [[Rules-and-receipts_layer_for_AI_agents_spending_mo 2026-09-18]]
- [[Агент-оркестратор_для_автоматизации_разработки 2026-06-12]]
- [[Терминал_для_управления_агентными_потоками 2026-07-17]]
