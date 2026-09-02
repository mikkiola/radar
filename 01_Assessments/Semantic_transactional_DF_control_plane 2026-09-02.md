---
status: CANDIDATE_LOW_CONFIDENCE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: A novel semantic transactional MCP control plane for long-lived
  agent-driven game civilization, with MVCC world state, witnessed plans, and deterministic
  replay, is designed but not yet operationally deployed; the compatibility registry
  is empty and mutations remain unimplemented, placing the project in prototype phase
  with high architectural novelty but unvalidated engineering maturity.
evidence_log:
- date: '2026-09-02'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: afd8cfee373b2ddf0c4439544eebd6efad7e7f22
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-09-02'
  verdict: CANDIDATE_LOW_CONFIDENCE
---
# Semantic transactional DF control plane

**Дата:** 2026-09-02
**Репозиторий:** https://github.com/Dicklesworthstone/dwarf_fortress_mcp
**Уверенность:** низкая
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "A semantic, transactional, replayable control plane for agents operating Dwarf Fortress as a long-lived civilization"

## What Changes in the Ecosystem
A new transactional semantic layer is introduced between autonomous agents and game state, replacing naive command-acknowledgement loops with witnessed plans, evidence-backed effects, and canonical observation capsules tied to exact source digests. The agent-environment interface shifts from stateless RPC to stateful turn packets that include continuity anchors, semantic briefings, ranked attention, and authority traces. Long-lived agent civilizations become possible through deterministic replay and anti-rollback floors on host deployment, decoupling agent intent from real-time DFHack protocol fragility.

## Reasoning
The project sketches a genuinely novel architecture layer (semantic transactional control over game state via MCP, with MVCC, deterministic replay, and evidence-backed effects), but implementation remains in phase-0B prototype status. README explicitly discloses that the compatibility registry is empty, no mutations exist yet, and protocol 1.1 is not in the production runner. The codebase structure and Rust safety practices (unsafe forbid, unwrap deny) show serious engineering intent, but cross-validation confirms the claimed capabilities are design targets, not deployed reality.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims authenticated protocol-1.0 read-only DFHack stack with exact compatibility, deterministic replay, and protocol-1.1 retained-announcement layer. Manifest shows 7 workspace crates (core, world, intent, adapter, lab, fortress-mcp, mcp) with strict unsafe_code forbid and unwrap denials, pinned fastmcp-rust fork, and deterministic serialization pins. File tree includes IMPLEMENTATION_STATUS.md, LIVE_ANNOUNCEMENT_IMPLEMENTATION_STATUS.md, architecture/live_compatibility_registry_v1.json, and bridge/ crate. However, README explicitly states: "The checked-in compatibility registry is **empty**", "No live tuple is admitted, protocol 1.1 is not in the production runner map, no live mutation RPC exists", and "the repository does not claim a runnable admitted live configuration." The capabilities claimed (semantic plans, witnessed effects, deterministic replay) are architectural design targets, not fully implemented features. Protocol 1.0 read-only bridge and protocol 1.1 announcement model are partially implemented but admission criteria R1-R5 are not met.
Подтверждено: Нет

**Novelty checklist:** New protocol: YES - Protocol 1.0 and 1.1 present a novel two-method RPC contract (Handshake, ReadObservation) with bounded nonce/token/frame domains and deterministic canonical observation capsules. New standard: PARTIAL - it targets MCP compatibility but is not yet a recognized standard; the MCP surface is frozen at 11 tools but the underlying protocol semantics around MVCC world state and transactional planning are new. New architectural layer: YES - the project proposes a semantic intent layer above raw observations with witnessed plans, evidence-backed effects, and deterministic replay isolation between agent turns, which is a new coordination abstraction for long-lived agent-environment interaction. New market interaction: NO - it does not introduce a new economic model or market primitive; it is a control plane for a single game environment.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, the first non-empty entry appears in architecture/live_compatibility_registry_v1.json with passing R1-R5 evidence, a complete protocol-1.1 announcement campaign is re-executed and committed, and a live agent successfully converges on a multi-turn fortress goal while proof-generating authoritative turn packets referencing deterministic replayed state.
**Если ошиблась:** Within 12 months, the project remains in read-only protocol-1.0 mode, the compatibility registry stays empty, protocol 1.1 is not integrated into the production runner, or the mutation RPC layer is abandoned without reaching the commit/plan surface described in the public MCP tool waist.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-02 - CANDIDATE_LOW_CONFIDENCE: первая оценка

## Связи
- [[MCP как универсальный протокол агентной интеграции 2026-06-14]]
- [[Инженерия_петель_для_долгоживущих_агентов 2026-06-22]]
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[Local-First Agent Memory and Cognition Layers 2026-08-04]]
- [[Верификация_доверия_для_сетей_агентов 2026-07-02]]
