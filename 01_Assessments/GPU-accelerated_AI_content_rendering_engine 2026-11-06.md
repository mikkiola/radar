---
status: CANDIDATE_LOW_CONFIDENCE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: raea introduces a unified React+Bevy rendering substrate where AI
  agents natively author, inspect, and iterate visual media (video, games, 3D) as
  queryable code, not external artifacts—a new architectural layer for agent-native
  content synthesis that did not exist in prior AI stacks.
evidence_log:
- date: '2026-11-06'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 91c544d21b25d6dc34989e5794ee9628a72beb3b
license_spdx_id: NOASSERTION
license_baseline_origin: initial
verdict_history:
- date: '2026-11-06'
  verdict: CANDIDATE_LOW_CONFIDENCE
---
# GPU-accelerated AI content rendering engine

**Дата:** 2026-11-06
**Репозиторий:** https://github.com/shinyobjectz/raea
**Уверенность:** низкая
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "Tell your AI what to make. Videos, motion graphics, 3D and games, written as React and TypeScript (the code your AI already writes) and rendered on your own GPU, faster than they play."

## What Changes in the Ecosystem
Agents gain native ability to author, preview, and validate videos, motion graphics, and games without leaving TypeScript/React code, eliminating hand-off to external rendering pipelines. Visual content generation becomes introspectable as queryable data, enabling iterative AI refinement without human-in-the-loop approval cycles. The GPU becomes a shared, standardized engine for media consumption and agent skill execution, lowering friction for AI-driven creative automation.

## Reasoning
raea combines React/TypeScript UI composition with Bevy 3D rendering and GPU encoding, positioning content generation as a native agent capability. While React rendering and Bevy game engines exist separately, their unified integration as a declarative framework for AI-driven video/game/3D synthesis represents a notable architectural shift in how agents author visual media. The canary status and active skill/plugin ecosystem indicate early adoption momentum despite production gaps.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** Partially confirmed. README claims: (1) React/TypeScript composition framework—Cargo manifest shows `runtime/react`, `sdk/raea` TypeScript SDK, composition API examples in README. (2) Bevy 3D integration—manifest includes `engine/bevy-*` crates and `systems/` subdirectories for 3D, lights, materials, splats. (3) GPU rendering/encoding—manifest includes `gpu/device`, `io/codec`, `io/av1`, `io/apple` (VideoToolbox), `systems/filters`, `systems/compose`. (4) Multi-platform (macOS/Linux/Windows)—README and badge confirm. However, the manifest shows a very large, complex workspace (100+ crates) with many experimental systems (speech, ML, music, foley). README acknowledges "Canary…breaks daily" and "rough edges," suggesting claimed capabilities are aspirational rather than fully integrated. The file tree confirms structure exists, but horizontal integration across all these subsystems for seamless agent use is not evident from static structure alone.
Подтверждено: Нет

**Novelty checklist:** Is this a new protocol? No—it uses standard React, TypeScript, Bevy, and video codecs. Is this a new standard? No—it proposes no ecosystem standard, only a product SDK. Is this a new architectural layer? Yes—it introduces a unified "content as code for AI agents" abstraction, merging declarative UI (React) with real-time 3D (Bevy) and hardware encoding into a single queryable rendering target. Agents can now author, inspect, and iterate visual media natively without invoking external tools. Is this a new way of market interaction? Tentatively yes—it positions visual content generation as an agent-native primitive (via `~/.claude/skills` integration), shifting from "agent calls rendering API" to "agent writes composition, engine renders, agent validates"—a feedback loop not standard in current AI stacks.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, Claude Code or another mainstream agent reports rendering 1000+ raea compositions in production workflows (e.g., bulk video generation, game asset creation), with adoption metrics published on raea.io/made or in agent telemetry.
**Если ошиблась:** Within 12 months, raea remains in canary status with no >100-frame-per-second consistency on Linux or Windows GPU drivers, or the agent skills remain unused (0 public examples of agent-authored raea compositions beyond demos), indicating architectural integration failed.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-11-06 - CANDIDATE_LOW_CONFIDENCE: первая оценка

## Связи
- [[Agent_control_plane_with_guardrails 2026-10-05]]
- [[Self-hosted_3D_среда_для_агентных_операций 2026-06-14]]
