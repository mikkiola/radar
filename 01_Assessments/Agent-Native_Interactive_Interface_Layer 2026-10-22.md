---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: ShowAI is a new architectural layer that mediates agent-human interaction
  by replacing text output with interactive, persistent, evolving component-based
  interfaces, enabling collaborative steering and template evolution.
evidence_log:
- date: '2026-10-22'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 7d18c11c34e8d51ad5d45dcba0ac84f8af8d185d
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-10-22'
  verdict: CANDIDATE
---
# Agent-Native Interactive Interface Layer

**Дата:** 2026-10-22
**Репозиторий:** https://github.com/Renaissance-Mind/ShowAI
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "The evolving interface between humans and agents. Your agent's answers become interfaces — interactive, archived, and evolving as you use them."

## What Changes in the Ecosystem
ShowAI shifts the output paradigm from agent-as-text-generator to agent-as-interface-builder: responses become interactive pages with dynamic components (charts, calculators, diagrams) that humans can adjust and persist. This enables a feedback loop where agents continue from human edits, creating templates and evolving interfaces—fundamentally changing how agent work is understood, steered, and reused in the ecosystem.

## Reasoning
ShowAI introduces a new architectural layer—the interface between agents and humans—where agent outputs become interactive, editable, and evolving components rather than static text. This represents a structural shift in how agent cognition is presented and co-created with humans, but the desktop implementation is still early (v0.10.0, Apple silicon only, not yet notarized).

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims ShowAI provides "interactive, archived, and evolving" interfaces built by agents through components (charts, calculators, diagrams), plugins for Claude Code and Codex, and a workbench app. The manifest confirms: (1) multi-agent support (Claude Code, Codex, DeepSeek Harness, Kimi Work, MCP clients) via plugin system; (2) component architecture ("components express information"—text, images, tables, charts, flow diagrams, sliders); (3) Pages and Boards for organizing content; (4) platform coverage (macOS desktop app, browser edition, MCP server); (5) persistent storage and export. The file tree includes plugin directories (plugins/, plugins-kimi/), agent integration layers (src/agent/), desktop app scaffolding (src/desktop/), and component catalog documentation (docs/catalog-lifecycle.md). No contradictions detected between claims and structure.
Подтверждено: Да

**Novelty checklist:** New protocol? Partially—MCP integration is standard, but the ShowAI plugin protocol for agent-to-interface serialization appears novel. New standard? No clear new standard format beyond existing MCP/artifact patterns. New architectural layer? Yes—ShowAI introduces the "interface layer between humans and agents" as an explicit architectural tier, where agent outputs are not consumed as text but as interactive, persistent, evolving components managed by a dedicated runtime. New way of market interaction? Yes—the workbench model for co-creation and template evolution creates a new market interaction pattern where archived interfaces become reusable templates and sharable deliverables, shifting from agent-as-service to agent-as-collaborator-in-interface-building.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** In 12 months, ShowAI reaches cross-platform stability (Windows, Linux notarization for macOS), achieves 5K+ monthly active users, and the agent ecosystem (Claude, DeepSeek, Kimi) ships native ShowAI support without manual plugin installation, validating the interface layer as an ecosystem primitive.
**Если ошиблась:** In 12 months, ShowAI remains macOS-only with v0.x versioning, plugin adoption stalls (agents revert to text/HTML artifact output), and no major agent platform adds native integration—indicating the interface layer is a niche tool rather than an ecosystem-level shift.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-22 - CANDIDATE: первая оценка

## Связи
- [[Local-First_Project_Memory_for_AI_Agents 2026-09-06]]
- [[Persistent_Cognition_Sidecar_Architecture 2026-08-02]]
- [[Единая_панель_управления_для_кодирующих_агентов 2026-07-19]]
