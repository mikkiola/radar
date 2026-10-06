---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: BashCut is a novel architectural bridge between video editing and
  AI agent autonomy, exposing timeline composition as an MCP-native, undoable state
  machine that allows coding agents (Claude, Codex) to orchestrate complex editorial
  workflows alongside human UI operators, with working implementations and early adoption
  signals but limited production footprint.
evidence_log:
- date: '2026-10-06'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 1607c564339e5064e0198f26b2b0c172fc731030
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-10-06'
  verdict: CANDIDATE
---
# Agent-Driven Native macOS Video Editor

**Дата:** 2026-10-06
**Репозиторий:** https://github.com/dongnguyenvie/BashCut
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "Everything the UI does, Claude Code and Codex can do through the bashcut CLI or MCP server"

## What Changes in the Ecosystem
BashCut transforms video editing from a GUI-only paradigm to an agent-native platform: AI agents (Claude, Codex, custom models via Director plugin) become first-class operators on a JSON project model with atomic, undoable edits. The ecosystem gains a new integration layer where coding agents can read, reason about, and manipulate video compositions programmatically through the same command interface as human UI interaction. This shifts video editing from a creative tool exclusively for humans toward a system where agents can orchestrate complex editorial workflows autonomously.

## Reasoning
BashCut combines three elements: native macOS video editing (proven, mature domain), agent-first architecture (emerging pattern), and MCP integration (novel in video). The core novelty lies in exposing a timeline composition engine as a state machine accessible to multiple AI agents through unified CLI/MCP APIs, with undo/history semantics—a new architectural layer for collaborative agent-human video workflows. The project shows working adoption (TestFlight, Homebrew, documented plugins) and active development (M0–M5 milestones, multiple agent bindings), but lacks evidence of large-scale production deployment or external ecosystem adoption beyond the author's own plugin registry.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims BashCut is a native macOS video editor where "everything the UI does, Claude Code and Codex can do through the bashcut CLI or MCP server." The file tree confirms CLI, MCPBridge, and agent-related directories (BashCut/, CLI/, MCPBridge/, .agents/, .claude/) are present. Package.swift and project.yml suggest active build infrastructure. The README also documents a full feature set (layered timeline, captions, voiceover, plugins, agent dock with real Claude/Codex terminals) and references bashcut-agent-kit and bashcut-plugins repositories. The claimed MCP server capability and CLI automation align with presence of MCPBridge/ directory. No manifest file was provided to cross-check package dependencies, but the Swift package ecosystem and documented plugin registry support the architectural claims. The file tree and README structure are internally coherent: agent capabilities are substantiated by agent-related source directories and documented automation guides.
Подтверждено: Да

**Novelty checklist:** New protocol: Partial—BashCut introduces an MCP server bridge for video editing (not a new protocol itself, but a novel application of MCP to real-time timeline control). New standard: No—uses existing MCP and CLI conventions. New architectural layer: Yes—a unified "project as JSON" + "undoable edit operations exposed to agents" layer is new in the video editing domain; agents and UI share the same atomic edit model, which is architecturally distinct from traditional GUI-only editors. New way of market interaction: Yes—positioning the editor as an agent-accessible service (not just a standalone app) where Claude Code and Codex integrate natively as first-class operational partners, rather than external plugins, is a novel market model for video editing tools.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, a third-party uses BashCut's agent API to integrate automated video editing into a production SaaS platform (e.g., marketing automation, podcast production, social media workflow), demonstrating sustained agent-driven adoption beyond hobby/demo use.
**Если ошиблась:** Within 12 months, the project is archived or enters maintenance mode (no releases for 6+ months, agent features remain experimental, MCP server is undocumented or broken in practice), indicating the agent architecture was not sufficiently valuable to sustain ongoing development.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-06 - CANDIDATE: первая оценка

## Связи
- [[Local-First_Multi-Agent_Software_Platform 2026-09-17]]
- [[Execution_Safety_Layer_for_AI_Agents 2026-09-11]]
- [[Persistent_Cognition_Sidecar_Architecture 2026-08-02]]
- [[Единая_панель_управления_для_кодирующих_агентов 2026-07-19]]
- [[MCP_сервер_GitHub_v2 2026-06-07]]
