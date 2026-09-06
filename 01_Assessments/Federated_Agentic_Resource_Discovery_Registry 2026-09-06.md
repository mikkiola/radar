---
status: CANDIDATE_LOW_CONFIDENCE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: ARD is a new open specification and federated search architecture
  that moves agent capability discovery from static configuration to dynamic runtime
  lookup across multiple registries, with Neuronto as the reference implementation
  providing verified tool introspection and hybrid lexical-semantic retrieval.
evidence_log:
- date: '2026-09-06'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 4d7ebc52036cc80b752f61e153c3bd1e2395741f
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-09-06'
  verdict: CANDIDATE_LOW_CONFIDENCE
---
# Federated Agentic Resource Discovery Registry

**Дата:** 2026-09-06
**Репозиторий:** https://github.com/neuronto/agentic-resource-discovery
**Уверенность:** низкая
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "ARD is short for Agentic Resource Discovery, an open specification for how AI agents find the tools, skills, agents and APIs they need, published in June 2026 by a working group including Google, Microsoft, Hugging Face, AWS, Cisco, GitHub, Nvidia, Salesforce and Snowflake."

## What Changes in the Ecosystem
ARD moves agent capability binding from static context windows and hard-coded integrations into a federated search abstraction, enabling agents to discover tools and services at runtime across multiple registries. This shifts the ecosystem from monolithic agent deployment (where every tool must be pre-installed) to a plugin-discovery model where new resources become available dynamically. Organizations can now publish internal service manifests on their own domains and have them indexed alongside public capabilities, creating a unified discovery plane for both external APIs and private infrastructure.

## Reasoning
ARD is a novel federated discovery specification with working reference implementation, but shows early production signals rather than established real-world adoption. The project implements four distinct novelties (protocol, standard, architectural layer, market model), yet the minimal manifest and missing database/verification infrastructure details suggest the implementation shown may be incomplete or partially abstracted. State is "Growing" because it represents a newly published standard (June 2026) from major vendors with active development and ecosystem integration (MCP, A2A support), though adoption evidence is limited to the registry itself.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims ARD is an open specification implemented as a federated search service with hybrid retrieval, verified tool introspection, and support for MCP/A2A protocols. The manifest confirms FastAPI/Uvicorn infrastructure for a service backend. The file tree shows app/, clients/, sdk/, web/ directories consistent with a multi-protocol discovery service. However, the manifest is minimal (4 dependencies only), suggesting either the core logic is elsewhere or the project structure is incomplete in what was provided. The README's claim of "32,183 verified tools across 2,223 servers" and live endpoint probing cannot be verified from the provided files alone—these would require database/cache schemas not shown. The core claim of federated search + verified tool introspection is structurally sound but the verification infrastructure depth is not evidenced in the minimal manifest.
Подтверждено: Нет

**Novelty checklist:** New protocol? Yes—ARD (Agentic Resource Discovery) is presented as an open specification published in June 2026 by a multi-vendor working group (Google, Microsoft, Hugging Face, AWS, etc.), defining how AI agents discover capabilities at runtime. New standard? Yes—ARD defines a formal specification with conformance testing, media types, federation modes, and API contracts (POST /search, POST /explore, GET /agents, etc.). New architectural layer? Yes—ARD represents a new indirection layer between agents and resources, moving capability selection from compile-time (hard-coded integrations) to runtime discovery, analogous to how DNS/search shifted the web from curated directories to dynamic lookup. New market interaction? Yes—enables vendors to publish manifests on their own domains and become discoverable without centralized marketplace gatekeeping, decoupling discovery from curation.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, ARD query endpoints report 100+ verified MCP servers indexed in the public registry with measurable agent-driven discovery traffic, and at least 3 major AI platform operators (Claude, GitHub Copilot, or equivalent) integrate ARD discovery into their standard agent runtimes, evidenced by public API documentation or SDK releases mentioning ARD conformance.
**Если ошиблась:** Within 12 months, the ARD specification remains published but adoption stalls: fewer than 50 verified public servers in the index, no measurable third-party platform integrations beyond the Neuronto reference implementation, and competing discovery proposals emerge from major vendors without convergence on the ARD schema, indicating market rejection of the federated model.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-06 - CANDIDATE_LOW_CONFIDENCE: первая оценка

## Связи
- [[MCP как слой интеграции сервисов 2026-06-14]]
- [[Открытые протоколы координации агентов 2026-06-25]]
- [[Динамически расширяемая архитектура агентов 2026-06-14]]
- [[Self-hosted суверенитет над агентной инфраструктурой 2026-06-14]]
- [[MCP как универсальный протокол агентной интеграции 2026-06-14]]
