---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Foremerge is a new coordination protocol that detects intent collisions
  between parallel AI agents before they write conflicting code, using declared semantic
  scopes and a shared SQLite store in Git, addressing a gap where Git's text-diff
  strategy cannot see non-overlapping edits that undo each other's architectural assumptions.
evidence_log:
- date: '2026-09-17'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: ae2f9e151ad44bf93912e15440bafa1ff7a56ec0
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-09-17'
  verdict: CANDIDATE
---
# Multi-agent Git conflict detection protocol

**Дата:** 2026-09-16
**Репозиторий:** https://github.com/naw103/foremerge
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "Foremerge is the open-source coordination protocol for coding agents, built above Git. Agents keep isolated worktrees while sharing intent, semantic claims, dependencies, provisional ChangeSets, decisions, validation, and provenance."

## What Changes in the Ecosystem
Foremerge shifts the locus of conflict detection from line-based textual diffs to intent-based semantic declarations, enabling agents to reason about work collision before code is written. It inserts a coordination layer between isolated worktrees and shared Git, making the hidden intent visible across parallel agents. This allows teams to deploy multiple commercial AI models on the same codebase simultaneously without sequential handoffs or merge conflicts that reflect undone work rather than text overlaps.

## Reasoning
Foremerge introduces a new protocol layer for multi-agent coordination by declaring intent via semantic scopes before code changes, coupled with a SQLite-backed shared awareness store in .git/, detection of operation-level conflicts (replace vs extend), and verification-gated lifecycle. This moves beyond Git's text-based merge strategy into semantic intent spaces—a structural innovation. Maturity is 3 (working MVP with CLI, MCP, and SQLite implemented, but pre-1.0, no public multi-machine mode, and no production adoption signals beyond author). State is Growing due to active CI, release pipeline, agent integration files (.claude/, .codex/, .cursor/), and clear design for commercial model adoption.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** YES. The README claims Foremerge is a coordination protocol built above Git that detects intent conflicts before code conflicts through declared scopes, semantic claims, and verification gates. The manifest confirms this is implemented: (1) the Cargo.toml lists dependencies like rusqlite for SQLite store, axum for MCP server, and tokio for async I/O, all required for the claimed architecture; (2) the root file structure includes .mcp.json (MCP integration), src/ (CLI+library), .claude/.codex/.cursor/ (agent integrations), and tests/, which structurally support the README's claim of local Git-folder database with per-client wiring; (3) bin names foremerge+fmg confirm the dual-binary pattern described; (4) the existence of examples/terminal-session.txt validates the release demo reference. The verification-gated lifecycle, scope detection, and conflict advisory system described in README are backed by the codebase structure.
Подтверждено: Да

**Novelty checklist:** New protocol: YES—Foremerge defines a coordination protocol using declared semantic scopes and provisional ChangeSets above Git, with deterministic conflict detection before code conflicts, which is not part of standard Git or existing coordination tools. New standard: PARTIALLY—it does define schemas for intent declaration and conflict severity (HIGH/LOW advisory taxonomy), though marked as pre-1.0 with possible schema changes. New architectural layer: YES—it introduces a shared awareness layer above Git using SQLite in .git/ folder, visible to all agents in isolated worktrees, mediating coordination without file locks. New way of market interaction: PARTIALLY—it enables parallel multi-agent coding workflows on commercial models (Claude, Codex, Cursor), which shifts from sequential to coordinated parallel agent deployment, though primarily as a coordination enabler rather than a new market mechanism.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, a GitHub workflow or issue announces successful parallel deployment of two or more commercial coding agents (Claude Code + Cursor, or similar) on the same private repository using Foremerge, with documented incident of Foremerge-detected intent conflict that prevented silent work-undoing.
**Если ошиблась:** Within 12 months, the project moves to Archived state, or the README documents that Git's native worktree + merge strategy sufficiently prevented the PaymentService-like collisions in practice, making Foremerge's semantic layer unnecessary.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-16 - CANDIDATE: первая оценка

## Связи
- [[Открытые протоколы координации агентов 2026-06-25]]
- [[MCP как слой интеграции сервисов 2026-06-14]]
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[Оркестрация множества коммерческих агентов 2026-07-23]]
- [[AI_Software_Engineering_Workflow_for_Agents 2026-08-13]]
