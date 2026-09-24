---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Apeireth proposes a novel cognitive operating system kernel with
  mandatory safe Rust, preemptive quota scheduling, topological memory (Vietoris-Rips
  homology), causal world model forking, and cryptographic lineage governance. While
  architecturally innovative with strong engineering discipline, it remains early-stage
  (v2.0 RC1) without production adoption signals or fully-validated benchmarks, placing
  it in the Growing/Prototype quadrant.
evidence_log:
- date: '2026-09-24'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 4774d8b86aff4e2a87ba0bfc53285832dd1a4132
license_spdx_id: NOASSERTION
license_baseline_origin: initial
verdict_history:
- date: '2026-09-24'
  verdict: CANDIDATE
---
# Safe Rust AGI Operating System Kernel

**Дата:** 2026-09-24
**Репозиторий:** https://github.com/Apeireth/Apeireth
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "An AGI Operating System &amp; Cognitive Microkernel (Pure Safe Rust) — A Home for an Intelligence that Truly Remembers."

## What Changes in the Ecosystem
Apeireth introduces a formally isolated cognitive operating system layer with mandatory safe Rust execution, replacing ad-hoc orchestration patterns with preemptive scheduling and causal state branching. The topological memory engine (Vietoris-Rips homology + Kuramoto phase locking) creates a new abstraction for continuous agent state representation distinct from vector databases or graph stores. This shifts the ecosystem from agent-as-function to agent-as-persistent-entity with deterministic reproducibility through SAGA rollback and hypothesis branching.

## Reasoning
Apeireth is a structurally ambitious project introducing multiple novel architectural primitives (cognitive OS microkernel, topological memory engine, triple-onion governance protocol) in pure safe Rust, with strong engineering discipline and comprehensive documentation. However, maturity is hampered by: (1) v2.0.0-rc1 release status (pre-production), (2) benchmark claims marked as "⏳ re-measured" rather than CI-passing, (3) no evidence of production deployments or real-world adoption beyond the authors, (4) 18-crate architecture still stabilizing (legacy/ and research/ excluded from workspace). The project demonstrates rapid iteration and growing momentum, but lacks the production hardening, third-party adoption markers, and long-term reliability track record that would justify maturity &gt;2.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims 18-crate pure safe Rust AGI OS with continuous topological memory, causal world model, cognitive scheduler, Ember HUD, and triple-onion security. Manifest confirms workspace structure with 18 crates organized in foundation/engine/capabilities/adapters layers matching the narrative architecture. File tree shows Docker, Makefile, comprehensive testing CI (codecov.yml, clippy.toml), SECURITY.md, documentation (docs/ folder), and examples - supporting the infrastructure claims. However, README benchmarks claim sub-millisecond latencies and specific memory footprints with "VERIFIED" status, but the manifest only indicates "⏳ re-measured after assembly split" for workspace test suite, suggesting benchmarks are aspirational targets rather than currently validated production baselines. The core architecture claims structurally check out; production-ready performance claims are unverified.
Подтверждено: Да

**Novelty checklist:** Is this a new protocol? YES - the "triple-onion zero-trust governance" with E/S/A/M/O principles and L0-L5 escalation plus Colang DSL represents a novel security protocol architecture not standard in existing LLM agent frameworks. Is this a new standard? PARTIALLY - attempts to establish standardization around cognitive quota scheduling (Q=&lt;Token, Step, Cost, Depth&gt;) and lineage spawning with Ed25519 epigenetic invariance, but these are not yet industry consensus standards. Is this a new architectural layer? YES - the cognitive microkernel as a distinct layer (scheduler, world model, topological memory) positioned between LLM inference and adapters is a novel system architecture not common in existing agent stacks (most use orchestration frameworks, not OS-level kernels). Is this a new way of market interaction? NO - the project positions itself as infrastructure/OS, not a new market mechanism or economic model.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, Apeireth v2.0.0 stable is released with all benchmarks integrated into CI/CD pipeline (passing green in GitHub Actions), and at least one external autonomous agent or research team publicly announces using Apeireth kernel in production for continuous memory or causal state branching.
**Если ошиблась:** Within 12 months, the project remains at RC or early alpha status with benchmark re-measurement still pending; no third-party integrations announced; or major architectural rollback (e.g., reverting to traditional vector store for memory) occurs, indicating core assumptions did not survive production contact.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-24 - CANDIDATE: первая оценка

## Связи
- [[Local-First Agent Memory and Cognition Layers 2026-08-04]]
- [[Cryptographic Trust as Native Agent Architecture 2026-08-04]]
- [[Суверенная_операционная_система_для_автономных_аге 2026-07-04]]
- [[Persistent_Cognition_Sidecar_Architecture 2026-08-02]]
- [[Верификационный_шлюз_для_агентских_действий_Claude 2026-06-14]]
