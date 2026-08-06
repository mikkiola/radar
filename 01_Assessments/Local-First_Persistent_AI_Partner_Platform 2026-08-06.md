---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Troth decouples AI partner cognition (memory, goals, identity) from
  the LLM model via persistent local substrate, enabling model swaps without partner
  reset. This is architecturally novel but operationally early, with growing interest
  in local-first agent sovereignty but limited production adoption signals.
evidence_log:
- date: '2026-08-06'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: c57607ee8eac941dac83c075584d3a3dc99d9aa0
license_spdx_id: AGPL-3.0
license_baseline_origin: initial
verdict_history:
- date: '2026-08-06'
  verdict: CANDIDATE
---
# Local-First Persistent AI Partner Platform

**Дата:** 2026-08-06
**Репозиторий:** https://github.com/xgre1/troth
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "Its identity, memory, goals and refusal walls live in a local SQLite substrate (`~/.troth/state.db`) that you own. Nothing about the partner is stored in any vendor's account, and swapping engines never resets it."

## What Changes in the Ecosystem
The ecosystem shifts from vendor-lock model-as-subject architectures (where memory and identity die on provider swap) to decoupled substrate-centric agents where cognition persists across competing model providers. This creates: (1) true model interchangeability without partner reset; (2) local data sovereignty as a competitive requirement for AI tools; (3) incentive alignment toward fine-grained model selection (routing to the cheapest/fastest capable model rather than subscription inertia).

## Reasoning
Troth introduces a structurally novel architecture—substrate-as-cognitive-subject with models as rented faculties—but execution is still early (v0.1.9, limited adoption signals). The novelty is genuine (architectural inversion), but maturity is prototype-to-early-working stage with adoption primarily within developer communities and proof-of-concept usage patterns.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** YES. The README claims a local SQLite substrate (`~/.troth/state.db`) that persists identity, memory, goals and refusal walls separately from the LLM model. The manifest shows: (1) `better-sqlite3` as a core dependency for local storage; (2) the project structure includes `proxy/`, `shared-core/`, `adapters/` and `plugin/` directories supporting multi-provider routing; (3) test suites (`tests/`) and security documentation (`SECURITY.md`) indicate working implementation; (4) the `bin/troth.js` CLI entry point and setup scripts (`scripts/`) confirm functional tooling. The architecture diagram reference in README describes substrate-as-subject separation which is structurally supported by the codebase organization (state isolation vs. adapter layer). The claim that "swapping engines never resets" the partner is architecturally sound given the persistent SQLite separation.
Подтверждено: Да

**Novelty checklist:** Is this a new protocol? NO - uses existing Claude/ChatGPT/OpenAI protocols, routes through standard OpenAI API endpoints. Is this a new standard? NO - MCP is an existing standard, not invented here. Is this a new architectural layer? YES - the separation of cognitive substrate (engrams, goals, walls, audit) from the LLM model as a swappable faculty is a novel inversion of conventional agent architecture where memory is vendor-bound and model-specific. This substrate-as-subject + model-as-faculty separation represents a new cognitive architecture primitive. Is this a new way of market interaction? YES - the ability to swap LLM providers without resetting partner identity and memory creates new market dynamics: breaking vendor lock-in for long-running AI relationships, enabling provider competition at the model layer only, and allowing users to maintain continuous AI partnerships across different commercial offerings.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, evidence of troth powering multi-month AI relationships with documented model-swap events (Claude→ChatGPT→local) where the partner retained memory, goals and personality state across transitions, with public case studies or testimonials demonstrating adoption beyond the author.
**Если ошиблась:** Within 12 months, troth remains under 100 GitHub stars with no evidence of production use, the substrate layer is superseded by competing approaches (e.g., vendor-native memory persistence), or the project is archived/unmaintained due to insufficient adoption momentum.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-08-06 - CANDIDATE: первая оценка

## Связи
- [[Local-First Agent Memory and Cognition Layers 2026-08-04]]
- [[Cryptographic Trust as Native Agent Architecture 2026-08-04]]
