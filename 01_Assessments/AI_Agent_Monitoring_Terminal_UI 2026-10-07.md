---
status: CANDIDATE_LOW_CONFIDENCE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: GhosttyEXTREME introduces a new observability and interactive coordination
  layer for managing multiple concurrent AI coding agents in real-time, transforming
  agent work from invisible background processes into visible, reviewable, and controllable
  workflows within the terminal environment.
evidence_log:
- date: '2026-10-07'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: 9ee6ee960231b792b00a48863b924453e96410dc
license_spdx_id: AGPL-3.0
license_baseline_origin: initial
verdict_history:
- date: '2026-10-07'
  verdict: CANDIDATE_LOW_CONFIDENCE
---
# AI Agent Monitoring Terminal UI

**Дата:** 2026-10-07
**Репозиторий:** https://github.com/steventsvik/GhosttyEXTREME
**Уверенность:** низкая
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "GhosttyEXTREME is Ghostty, the fast native macOS terminal, rebuilt for working with AI coding agents like Claude Code and Codex. You see every agent work, live: what it's doing in each tab, the code it's writing as it writes it, where it is in your project and what part of your backend it touches."

## What Changes in the Ecosystem
This project adds a new observability and coordination layer for AI coding agents, making agent work visible and interactive rather than hidden. It transforms the terminal from a passive output display into an active monitoring and intervention interface where developers can see exactly what each agent is doing, review its changes, and run multiple agents competitively. The ecosystem shift is from "agent-in-background" to "agent-as-visible-collaborator."

## Reasoning
GhosttyEXTREME introduces a novel architectural layer for real-time agent visibility and multi-agent coordination within the terminal environment, addressing a gap in developer tools for observing AI agent work. However, it remains a fork of Ghostty with specialized UI overlays rather than production-hardened infrastructure, and lacks sufficient adoption signals to claim maturity beyond prototype stage.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims comprehensive features for monitoring and managing AI coding agents in real-time: agent sidebar with live status, code editor that animates agent edits, code map visualization, backend/database views, review system, agent races, and visual fix tools. The file tree contains agent-hooks/ directory and AGENTS.md documentation supporting agent integration claims, and multiple UI elements suggested by feature descriptions. However, the manifest is missing and cannot be verified against specific architectural implementations of these features. The claimed real-time animation capabilities, multi-agent synchronization, and backend integration remain unverified against actual implementation structure.
Подтверждено: Нет

**Novelty checklist:** New protocol? No - it uses standard terminal protocols and agent communication methods. New standard? No - builds on existing Ghostty terminal and common agent interfaces (Claude Code, Codex, etc.). New architectural layer? Yes - introduces a dedicated visualization and coordination layer between AI agents and the developer environment that monitors real-time agent actions, animates changes, and provides cross-agent state visibility at the terminal/UI level. New way of market interaction? Yes - shifts agent usage from invisible background processes to observable, interactive workflows where developers watch and intervene in real-time agent work across multiple concurrent agents.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, major AI development tools (JetBrains, Cursor, VSCode) adopt similar real-time agent observation and visualization layers as standard features for managing concurrent AI agents.
**Если ошиблась:** Within 12 months, the project remains a niche fork with fewer than 5,000 GitHub stars and shows no adoption by significant coding platforms or integration into mainstream agent frameworks.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-07 - CANDIDATE_LOW_CONFIDENCE: первая оценка

## Связи
- [[Единая_панель_управления_для_кодирующих_агентов 2026-07-19]]
- [[Local-First_Project_Memory_for_AI_Agents 2026-09-06]]
- [[Local-First_Multi-Agent_Software_Platform 2026-09-17]]
- [[Execution_Safety_Layer_for_AI_Agents 2026-09-11]]
