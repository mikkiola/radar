---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: VibeValley implements a novel local-first agent orchestration layer
  that makes human-agent-human verification loops and multi-agent coordination on
  shared code repositories a persistent, auditable first-class primitive, currently
  in working alpha/beta with active development but not yet production-proven.
evidence_log:
- date: '2026-11-05'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 7f336d2ca3b797ffcb749af08ba82b9df1e1875a
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-11-05'
  verdict: CANDIDATE
---
# Local-first multi-agent coding orchestrator

**Дата:** 2026-11-05
**Репозиторий:** https://github.com/vibevalleyhq/vibevalley
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "A team of coding agents you direct by voice or chat, drawn as a pixel farm. Runs on your own machine."

## What Changes in the Ecosystem
VibeValley introduces persistent, human-verified agent coordination as a first-class primitive. Instead of humans scripting or monitoring agents in isolation, the system makes the manager→worker→chat feedback loop a durable, replayable artifact stored locally, enabling retrospective human intervention at any step and non-linear task composition (branching, replanning). It treats the project repository as the single source of truth (agents work on real branches), not a simulation, shifting the agent-code-human loop from "prompt→output→evaluate" to "task→branch→audit→merge" with full replay capability.

## Reasoning
VibeValley is a working, deployable multi-agent orchestrator with proven coordination patterns (manager dispatch, worktree isolation, human-in-the-loop verification) already in use on macOS. However, it remains early-stage in adoption (internal deployment focus, active development with schema changes), lacks production hardening signals (explicit monolithic design, single-user local scope, no clustering), and does not yet claim real production usage at scale. Its novelty lies in combining persistent task audit trails, local-first agent memory, and human-verification workflows into a cohesive architectural layer—genuinely new in the AI coding space, but the implementation is still maturing.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** Yes. The README claims: (1) a team of coding agents orchestrated through a single manager ("你只和**管家**说话"), directed by voice or chat; (2) agents work on isolated branches/worktrees in the actual project repository; (3) event-driven state management with pure functions folding "facts" into UI state; (4) a pixel-art farm visualization of work progress mapped to real agent execution. The manifest confirms: TypeScript server (apps/server/) with Effect v4 and PGlite for state+storage, oar runtime driving different agent backends (pi, Claude Code, Codex, DeepSeek), web UI (apps/web/ in Solid 2), protocol definitions shared across server and client (packages/protocol/), Electron desktop wrapper. The file tree shows dedicated services for task dispatch, execution sessions, chat ("田头"/farmhead), project management, and a plugin system for external connectors (WeChat, Feishu, QQ). All claimed subsystems—manager agent, worktree isolation, multi-agent coordination, persistent audit trail—are structurally present.
Подтверждено: Да

**Novelty checklist:** New protocol? Partially—the task-event model (facts→state) and the manager-worker-chat workflow differ from standard CI/CD and project management, but not a formal protocol specification. New standard? No, it does not propose a standard for other systems to adopt. New architectural layer? Yes—it introduces a local-first agent orchestration and memory layer (persistent task audit trail, worktree isolation per agent, manager-mediated coordination, voice/chat interface) that did not exist as a cohesive layer in the AI coding ecosystem. New way of market interaction? Partially—it enables direct human-agent-human loops (skip middle management) over existing tooling (GitHub, local git), but this is more UX pattern than market structure shift. Overall: YES on architectural layer and substantial YES on protocol/coordination model.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, VibeValley reports production adoption by a team of 10+ developers on a non-trivial codebase, or a public case study from an external organization demonstrates measurable time-to-merge and conflict-resolution improvements via the manager-mediated coordination model.
**Если ошиблась:** Within 12 months, the project is archived or enters long-term maintenance with no external adoption signals, or the core manager-agent coordination model is substantially rewritten (indicating the current architecture did not survive real-world testing).

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-11-05 - CANDIDATE: первая оценка

## Связи
