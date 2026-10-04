---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: omabox implements a novel agent-scoped virtual desktop isolation
  layer atop Omarchy/Hyprland, enabling parallel UI testing without host interference;
  early adoption, high specialization, architectural innovation within niche ecosystem,
  growing momentum.
evidence_log:
- date: '2026-10-04'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 62c9a1c1dd0988d20517e6d904bd81609c592f80
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-10-04'
  verdict: CANDIDATE
---
# Hidden execution environment for AI agents

**Дата:** 2026-10-04
**Репозиторий:** https://github.com/diogochaves/omabox
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "Your agents get desktops of their own. Yours stays untouched. omabox gives every AI agent a whole Omarchy desktop, invisible and in parallel, to launch, click, type and screenshot apps and shell plugins in."

## What Changes in the Ecosystem
omabox introduces a new layer: agent-scoped virtual execution environments that intercept and isolate desktop interactions (screenshots, window management, input) without sandbox restrictions. This enables parallel agent testing within Omarchy without UI conflict on the host, shifting the ecosystem from shared-screen multi-agent coordination to partitioned-execution models. Agents gain independent desktop state while maintaining host OS access under observation.

## Reasoning
omabox is a novel architectural layer providing isolated virtual desktops for agent execution, but maturity is early: it is tightly coupled to Omarchy 4/Hyprland, requires GPU render nodes, carries unmerged patches for NVIDIA/aquamarine, and shows signs of active development (0.2.0 stable, documented workflows) without widespread adoption beyond Omarchy ecosystem. The project is growing with clear documentation, agent integration, and multiple operational modes, but remains specialized infrastructure for a niche agent platform.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims omabox provides a "whole Omarchy desktop" for AI agents with Hyprland config, shell components (bar, menu, tray, notifications), theme inheritance, and interactive/headless modes. File structure confirms: bin/ (likely CLI commands matching 'omabox up/run/shot/keys/etc'), plugin/ (integration with Omarchy), skill/ (agent skill registration), patches/ (Hyprland/aquamarine patches), share/ (config/theme data), and test/ (validation). The README specifies exact capabilities (screenshot, window control, Lua access, idle timeout, session naming) and the file tree structurally supports multi-component implementation. install.sh automates setup. No manifest file exists to contradict, but the file organization aligns with claimed architecture of a private Hyprland session with persistent state and agent-scoped environments.
Подтверждено: Да

**Novelty checklist:** New protocol? No - uses existing Hyprland/Omarchy protocols. New standard? No - integrates into existing Omarchy standard. New architectural layer? YES - introduces an agent-scoped virtual desktop/session isolation layer as a primitive that separates agent UI interactions from host desktop, operating as a lightweight container-like abstraction. New market interaction? No - preserves standard agent/Omarchy integration patterns. One novelty criterion is met.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, omabox is adopted by at least 2 major commercial AI agent platforms (Claude Code, Codex, or equivalent) as a default or recommended execution backend, evidenced by official integration docs or agent skill references outside the omabox repo.
**Если ошиблась:** Within 12 months, omabox remains functionally exclusive to Omarchy, shows no adoption by competing agent platforms, or is archived due to Hyprland/Omarchy incompatibility changes.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-04 - CANDIDATE: первая оценка

## Связи
- [[Local-First_Multi-Agent_Software_Platform 2026-09-17]]
- [[Execution_Safety_Layer_for_AI_Agents 2026-09-11]]
- [[Суверенная_ОС_для_локальных_ИИ-агентов 2026-06-20]]
- [[Persistent_Cognition_Sidecar_Architecture 2026-08-02]]
- [[AI_Agent_Authorization_Middleware 2026-08-15]]
