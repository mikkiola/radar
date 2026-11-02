---
status: CANDIDATE_LOW_CONFIDENCE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: Dokimi introduces the first systematic paired-comparison instrumentation
  layer for measuring whether agent guidance (skills, docs, MCP configs) actually
  improves agent performance, with per-model statistical validation and novelty classification—a
  novel architectural pattern for agent evaluation but early in adoption.
evidence_log:
- date: '2026-11-02'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: 41b3d8dfe0274e173144e57e70d42a6bfbcbe040
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-11-02'
  verdict: CANDIDATE_LOW_CONFIDENCE
---
# Agent Context A/B Testing Framework

**Дата:** 2026-11-02
**Репозиторий:** https://github.com/intel/dokimi
**Уверенность:** низкая
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "Dokimi runs the same questions or coding tasks with and without one change, grades both the same way, and reports the difference with its p-value, per model."

## What Changes in the Ecosystem
Dokimi adds a systematic measurement layer to the agent ecosystem by introducing paired statistical validation of agent guidance (skills, docs, MCP configurations). It shifts the ecosystem from "popular or claimed" to "tested and measured" by codifying a grading methodology (the novelty matrix: added/redundant/missing/degraded) and making per-model evaluation standard rather than one-shot benchmarking. This enables evidence-based curation of agent augmentations and guidance.

## Reasoning
Dokimi is a novel evaluation instrumentation layer (architectural), but currently exists as an early-stage tool with limited adoption signals. The codebase appears active (CI/CD present, documentation framework in place), but lacks evidence of production deployment beyond proof-of-concept demonstrations within Intel or academic contexts. The novelty checklist passes on the architectural layer criterion—this is the first ecosystem-wide pattern I observe for systematic paired validation of agent guidance quality.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims Dokimi performs: (1) paired on/off A/B comparisons of agent context, (2) novelty analysis showing which skill parts are already-known vs. added vs. broken vs. missing, (3) repository scans with graded agent runs, and (4) model-specific verdicts. The file tree shows `/dokimi/` as the main package directory, `AGENTS.md` (meta-reference to agent guidance), `VISION.md` (strategic intent), and references to skills as data artifacts (`.data/skills/dokimi-design-evals/SKILL.md`). The structure indicates a Python CLI tool (`dokimi` command) with evaluation subsystems (arms, novelty, catalog, repo scanning). However, the manifest is absent, so structural confirmation of claimed capabilities (grading pipeline, statistical testing, per-model evaluation) cannot be fully verified from the provided file list alone. The presence of GitHub workflows (docs, codecov, scorecard) and test coverage infrastructure suggests active development, but detailed capability verification would require examining actual source code and configuration files not listed here.
Подтверждено: Нет

**Novelty checklist:** New protocol? No—A/B testing methodology is established; this applies it to agent context evaluation. New standard? Partially—proposes a measurement standard for agent skill/doc quality (the 2x2 novelty matrix), but not a formal standards body artifact. New architectural layer? Yes—introduces an evaluation instrumentation layer for AI agents that didn't exist as a distinct ecosystem pattern before; specifically a grading and statistical validation loop for agent guidance content. New market interaction? No—this is a tool for internal quality assurance, not a new market mechanism.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, major open-source agent frameworks (e.g., LangChain, LlamaIndex, or similar) integrate Dokimi-style A/B evaluation workflows as a standard step in evaluating agent skills or documentation contributions, with publicly visible measurement reports.
**Если ошиблась:** Within 12 months, no significant adoption beyond Intel internal use is observed; the project remains a research prototype with no independent forks or external teams reporting results using Dokimi's measurement framework on their own skills/agents.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-11-02 - CANDIDATE_LOW_CONFIDENCE: первая оценка

## Связи
- [[Agent_control_plane_with_guardrails 2026-10-05]]
