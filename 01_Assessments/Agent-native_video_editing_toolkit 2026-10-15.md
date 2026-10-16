---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: Yap introduces a novel agent-native media toolkit that decouples
  human expression (raw recording) from production (agent-driven editing), using evidence
  primitives to enable agents to make editorial decisions, creating a new architectural
  layer for agent-media interaction in the AI ecosystem.
evidence_log:
- date: '2026-10-16'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: 63d1e2db6d8084782ded2d92c8d8b99de69bccbb
license_spdx_id: null
license_baseline_origin: initial
verdict_history:
- date: '2026-10-16'
  verdict: CANDIDATE
---
# Agent-native video editing toolkit

**Дата:** 2026-10-15
**Репозиторий:** https://github.com/dzhng/yap
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "Yap is an agent toolkit, not a video editor. Yap deliberately has no editing timeline, transcript editor or house style for people to operate. You tell your agent what you want, and the agent uses Yap's CLI or MCP operations to inspect evidence, choose the changes and make a non-destructive revision."

## What Changes in the Ecosystem
Yap introduces a media toolkit architecture where agents (Claude Code, Codex, MCP servers) control video/audio operations via evidence-based primitives (transcripts, frames, waveforms, loudness) rather than timeline UIs. This shifts video editing from human manual work to agent-driven composition, and creates a new integration surface for AI agents to act on media that humans record naturally. The ecosystem gains a new category: agent-native media manipulation, positioning agents as editors and reviewers rather than content creators working within human-designed tools.

## Reasoning
Yap is a category-creating toolkit that positions video editing as an agent capability, not a human activity. While individual components (transcription, ffmpeg-based editing, MCP) are mature, the integration as a non-destructive, evidence-driven system for agent-assisted media work is novel in the agent market. Early-stage adoption signals (single platform, recent release pattern, no evidence of production-scale use beyond creator) place it in Prototype state despite functional maturity of subsystems.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims Yap provides screen recording, transcription, video editing, audio cleanup, non-destructive revision, multi-range cuts, captions, noise reduction, voice regeneration, and MCP/CLI operations for agents. The manifest shows a monorepo structure (apps/cli, apps/macos, packages for test-harness, helpers for ffmpeg, model-runtime, speaker, alignment) with Turbo build orchestration and test suites, plus evals/ for agent testing. The file tree lists .agents/, skills/, specs/ directories that would contain MCP specifications and agent integrations. This structurally supports the README's claim of a toolkit designed for agent interaction, though the absence of visible MCP server code in the manifest makes "MCP" agent claims harder to fully verify from this data alone.
Подтверждено: Да

**Novelty checklist:** 1) New protocol? No—uses existing MCP and standard CLI. 2) New standard? Partially—the combination of non-destructive video editing + agent-native operations via evidence (transcripts, frames, waveforms) as input/output is a new structuring of how agents interact with media, not a standard itself. 3) New architectural layer? Yes—introduces a "media-agent bridging layer" that sits between recording/editing operations and agent decision-making, with explicit evidence primitives instead of human-driven UI. 4) New market interaction? Yes—enables a new workflow (record → ask agent → agent edits → undo cycle) that decouples human expression from production, targeting async team communication and agent-assisted demo creation.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** By Q4 2025, at least two major AI coding agents (Claude Code, GitHub Codex, or equivalent) integrate Yap as a documented, first-class capability for handling video evidence in agent workflows, with visible usage examples in agent prompt libraries.
**Если ошиблась:** By Q4 2025, Yap remains a single-platform (macOS) tool with no integration into agent frameworks beyond manual CLI calls, and GitHub activity shows no significant third-party adoption or agent-specific feature development.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-15 - CANDIDATE: первая оценка

## Связи
- [[Local-First_Multi-Agent_Software_Platform 2026-09-17]]
- [[Local-First_Project_Memory_for_AI_Agents 2026-09-06]]
- [[Персистентная_локальная_память_для_кодирующих_аген 2026-06-28]]
- [[MCP_сервер_GitHub_v2 2026-06-07]]
- [[Единая_панель_управления_для_кодирующих_агентов 2026-07-19]]
