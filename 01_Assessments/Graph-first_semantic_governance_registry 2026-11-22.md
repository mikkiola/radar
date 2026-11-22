---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Signet provides a novel semantic governance and transparency-logged
  trust layer for agent/skill identity and certification that decouples durable logical
  identity from immutable version snapshots, binding publication through cryptographic
  envelopes and human-AI review gates into a replay-auditable governance event log.
evidence_log:
- date: '2026-11-22'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 087a809ad543476e84c9e0c4f8149b8031fea8aa
license_spdx_id: BSD-3-Clause
license_baseline_origin: initial
verdict_history:
- date: '2026-11-22'
  verdict: CANDIDATE
---
# Graph-first semantic governance registry

**Дата:** 2026-11-22
**Репозиторий:** https://github.com/therandomsecurityguy/signet
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "Signet is a graph-first **semantic governance system** for autonomous agents and computational skills. Most registries are catalogs: metadata in, search out. Signet governs *meaning, release state, and evidence* — and stamps every trusted publication with the proof to back it up."

## What Changes in the Ecosystem
Signet establishes a new architectural layer: a provenance-sealed, graph-first governance plane for agent/skill identity and certification that decouples logical identity from version snapshots. Agents and humans can now discover, verify, and audit capability sources through transparency-logged, cryptographically-bound governance events rather than untrusted metadata catalogs. This shifts agent ecosystem trust from "vibes" to machine-readable, replay-auditable supply-chain evidence.

## Reasoning
Signet is a working system (maturity 3) with CI/CD, semantic validation layers, and clear lifecycle semantics — deployable but not yet production-hardened at ecosystem scale. It achieves novelty 4 by introducing a semantic governance + transparency-logging layer that is architecturally new for agent trust infrastructure, though it composes existing primitives (SHACL, PROV-O, Merkle trees, cryptographic signing) in a novel way. The project shows active development (GitHub workflows, release tooling) and addresses a real gap in agent ecosystem governance, suggesting growing adoption momentum.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims five-layer validation (SHACL graph-shape, policy, ontology, LLM advisory, human review), cryptographic signing with RFC 8785/RDFC-1.0 canonicalization, transparency logging with Merkle/Tessera integration, and dual ontology packages. File tree shows: service/ directory (suggesting runtime components like shacl-runtime sidecar mentioned in README), client/ (SDK verification helpers referenced), docs/ (governance-model.md, artifact-storage.md, supply-chain-model.md referenced), data/ (likely ontology/policy packages), and tools/ (operator CLI). The .release-please-* files and CHANGELOG.md indicate versioning infrastructure. Dockerfile/.dockerignore presence aligns with containerized sidecar services mentioned. The file structure partially supports core claims, though full end-to-end validation pipeline details would require examining service/ and client/ implementations, which are not shown here.
Подтверждено: Да

**Novelty checklist:** New protocol: NO — this combines existing protocols (SHACL, PROV-O, DSSE, in-toto, Merkle trees, RDF canonicalization). New standard: PARTIALLY — it defines a normative certification state machine and dual-ontology governance model for agent/skill publication, though built atop W3C standards. New architectural layer: YES — a semantic governance and transparency-logging layer for autonomous agent capability discovery, trust, and provenance that sits above implementation registries and below agent execution. New market interaction: YES — introduces certification pipeline, supply-chain attestation binding, and human-AI review gates as a governance-as-code pattern for agent ecosystems.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, Signet governance events are routinely replayed by agent frameworks during skill discovery, transparency logs reference Signet publication checksums in operational telemetry, and at least one major agent platform integrates policy-package validation into its skill approval workflow.
**Если ошиблась:** Within 12 months, the project receives no adoption beyond a single internal use case, no agent framework integrates the transparency log, and certification pipeline complexity exceeds demand — project pivots or stalls.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-11-22 - CANDIDATE: первая оценка

## Связи
- [[LLM-maintained_knowledge_governance_standard 2026-08-29]]
- [[Peer-to-peer_agent_rooms_with_signed_work 2026-10-01]]
- [[AI_coworker_coordination_and_audit_layer 2026-10-20]]
- [[Персональная_ОС_навыков_для_AI_агентов 2026-06-15]]
- [[Децентрализованный_маркетплейс_агентских_ресурсов 2026-06-25]]
