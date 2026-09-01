---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: ACRYL is an early-stage architectural layer that decouples agent
  identity from persistent project context, enabling agent-agnostic continuity through
  a Cordis-based capability relay—a novel pattern not yet production-proven but structurally
  sound and actively developed.
evidence_log:
- date: '2026-09-01'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: 028515d36d9bd464dd68bcd8e1464b1fa2f7304c
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-09-01'
  verdict: CANDIDATE
---
# Persistent Agent Context Workspace Layer

**Дата:** 2026-09-01
**Репозиторий:** https://github.com/acryldev/acryl
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "ACRYL is an agent-agnostic Agentic Development Environment and continuity layer for software work. The project does not belong to Claude Code, Codex, OpenCode, Pi, Gemini CLI, DeepSeek, or any other individual agent. ACRYL owns the persistent workspace, project context, tasks, artifacts, and handoffs. Coding agents are replaceable workers that enter and leave the same development scene."

## What Changes in the Ecosystem
ACRYL shifts the agent economy from agent-centric (context locked to one agent) to workspace-centric (context persists across agent swaps). This reframes multi-agent coding work as session handoffs over a durable event stream, not file synchronization. It decouples agent identity from project continuity, enabling Claude → DeepSeek → future-agent workflows within the same workspace.

## Reasoning
ACRYL introduces a novel architectural primitive (persistent cross-agent context via Cordis-based capability relay) but is explicitly in early development (v0.1.26, "early development" badge in README). Manifests and file tree confirm the claimed multi-surface, plugin-based design. However, no evidence of production adoption beyond author; the README itself warns interfaces may change. Maturity=2 (working prototype, no signs of real-world usage yet); Novelty=4 (new architectural layer separating agent lifecycle from context persistence); State=Prototype (high conceptual momentum but very early execution).

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** ACRYL describes itself as an "agent-agnostic Agentic Development Environment and continuity layer" with "one persistent workspace, one persistent project context" supporting multiple interchangeable agents. The manifest (package.json v0.1.26) shows multiple surface builds (acryl-control, acryl-tui, acryl-web, acryl-desktop, acryl-development-canvas) and the file tree includes acryl-harness-runtime, confirming the claimed architecture. The README explicitly states core principles around persistent context ownership separate from disposable agent sessions, and describes Cordis-based plugin architecture with lifecycle management. The file structure includes AGENTS.md and capability provider documentation, supporting the claim of agent-agnostic multi-provider support. However, the README explicitly states "ACRYL is in active early development. Interfaces, workflows, and packaging may change" - functionality exists but production hardening is incomplete.
Подтверждено: Да

**Novelty checklist:** New protocol: No - ACRYL uses existing protocols (MCP compatibility mentioned, based on Cordis). New standard: Partially - the "canonical event stream + durable tasks + context projections" model for agent continuity could become a de-facto standard but it is not yet an established standard. New architectural layer: Yes - the persistent context relay and agent-agnostic session continuity layer fundamentally changes how coding agents interact with shared state, separating "agent lifecycle" from "project context lifecycle." New market interaction pattern: Yes - enables a model where agents are swappable workers within stable workspaces, shifting from agent-vendor lock-in to agent-neutral infrastructure.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, ACRYL reaches v1.0 with stable APIs, at least 2+ major coding agents (Claude + one other) formally integrate handoff support, and 50+ GitHub stars/active fork evidence of external teams testing cross-agent continuity.
**Если ошиблась:** Within 12 months, the project is archived or remains below v0.2 with no external integrations from major agent vendors, indicating the cross-agent context layer lacks product-market fit or adoption friction is too high.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-01 - CANDIDATE: первая оценка

## Связи
- [[Динамически расширяемая архитектура агентов 2026-06-14]]
- [[Оркестрация множества коммерческих агентов 2026-07-23]]
