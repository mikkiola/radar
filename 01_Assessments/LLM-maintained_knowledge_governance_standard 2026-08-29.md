---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: Cambium defines a formal, multi-layer governance protocol for agent-maintained
  knowledge corpora, introducing kernel semantics, resumable state machines, and human-verifiable
  checkpoints—a structural innovation in agent work coordination, but currently prototype-stage
  with no production deployments.
evidence_log:
- date: '2026-08-29'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: ee08bf64ab82c9069ffcc95d2d6948face2f022c
license_spdx_id: NOASSERTION
license_baseline_origin: initial
verdict_history:
- date: '2026-08-29'
  verdict: CANDIDATE
---
# LLM-maintained knowledge governance standard

**Дата:** 2026-08-29
**Репозиторий:** https://github.com/KimGLee/Cambium
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "Cambium is a governance standard and reference toolset for knowledge repositories maintained with LLM agents."

## What Changes in the Ecosystem
Cambium shifts knowledge corpus maintenance from unstructured agent autonomy to formally governed, resumable, verifiable work. It introduces a kernel+profile separation that allows domain-specific policies while preserving governance invariants. The three-ledger model and state recovery semantics enable long-running LLM work with human oversight checkpoints and audit trails.

## Reasoning
Cambium is a novel governance protocol and architectural framework for LLM-maintained knowledge, evidenced by its kernel semantics, formal profile extension system, and deterministic state machine. However, maturity is low: it is explicitly uninstantiated (no real corpus deployed), no production users mentioned, and several key runtime features (agent dispatch, assignment lifecycle, actor identity) are roadmapped but not shipped. The repository is a reference toolset and standard template, not a production implementation.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims Cambium is "a governance standard and reference toolset for knowledge repositories maintained with LLM agents" with specific kernel governance semantics, profiles, Cards, Read Sets, and a three-ledger runtime model. File tree confirms kernel/, Card/, Read Set/, Tools/, profiles/ directories exist with governance-related content. Tools/README.md, Tools/runtime_paths.py, and schema files (profile_adoption_plan.template.yaml) support the toolset claim. Kernel standards (K00/19 reference) and profile interview mechanisms are referenced and structurally present. README explicitly states "This repository is intentionally uninstantiated" - it provides a governance template, not a deployed system. Cross-validation: the architecture described (kernel + profile + state layers) aligns with the actual directory structure and tool organization in the repository.
Подтверждено: Да

**Novelty checklist:** New protocol? Cambium defines a formal governance protocol for LLM-maintained corpora with deterministic state transitions and verification semantics - YES, this is a new protocol layer. New standard? It is explicitly marketed as "a governance standard" with normative kernel rules and extension points - YES. New architectural layer? It introduces a three-ledger runtime model (Coverage, Required Queue, Progress) plus kernel/profile/state separation for agent-human collaboration - YES. New market interaction? It enables a new mode: operator-controlled governance boundaries over agent-maintained knowledge - PARTIALLY YES (market relevance is unclear, but organizational/workflow relevance is high).
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, at least one public fork or external organization adopts Cambium's kernel governance model for their LLM-maintained knowledge repository and reports closure of tasks through Cambium's state ledgers.
**Если ошиблась:** Within 12 months, the project remains uninstantiated with no evidence of real adoption beyond the author; the governance protocol is superseded by a simpler or competing agent-knowledge standard that gains wider adoption.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-08-29 - CANDIDATE: первая оценка

## Связи
- [[MCP как универсальный протокол агентной интеграции 2026-06-14]]
- [[Инженерия_петель_для_долгоживущих_агентов 2026-06-22]]
- [[Верификация и доверие к действиям агентов 2026-06-14]]
- [[Открытые протоколы координации агентов 2026-06-25]]
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
