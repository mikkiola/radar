---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Monid introduces a new declarative protocol and metering standard
  for agent-tool integration, enabling dynamic per-call endpoint discovery and outcome-based
  billing, but remains early in adoption with strong architectural momentum and limited
  production-scale validation.
evidence_log:
- date: '2026-09-17'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 645141deb9e43e66729617df68af442818678ee6
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-09-17'
  verdict: CANDIDATE
---
# Unified agent tool integration layer

**Дата:** 2026-09-16
**Репозиторий:** https://github.com/monid-ai/monid
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "OpenRouter, but for agent tools. One base URL, one key, and an agent can reach 2,000+ tools across 72+ providers"

## What Changes in the Ecosystem
Monid introduces a declarative, compile-time protocol for agents to discover and invoke tools from multiple providers through a single gateway, shifting tool integration from hard-coded vendor bindings to dynamic per-call endpoint selection. The metering model (charging on actual response data, not requests) decouples cost attribution from provider error rates. The sealed-unit compilation approach (functions replaced by content-hash references) creates a new security model for agent tool execution.

## Reasoning
Monid is a structured innovation in the agent-tool integration layer: it proposes a new protocol, standard, and architectural pattern for how agents access tools at scale, with explicit per-call metering and discovery semantics. However, the project shows signs of active development and conceptual maturity in its design (tooling, test strategy, documentation) but limited evidence of production adoption or large-scale real-world usage yet. The state shows strong momentum (CI/CD, npm package, comprehensive docs, explicit agent-writing guides) but is still in the early-to-growing phase.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** Partially. The README claims Monid is "OpenRouter for agent tools" providing "2,000+ tools across 72+ providers" with unified discovery, inspection, and execution via a single base URL and key. The file tree shows connectors/ (exa, tinyfish references in README), engine/, openspec/, and shared/ directories supporting this architecture. However, the manifest file was not provided, and we cannot verify the actual connector count or the live operational state of the 2,000+ tools claim. The declarative connector format (provider.ts, endpoint.ts with schemas) is structurally present in the repository organization, and the README demonstrates a working connector example (tinyfish). The core technical claim—a unified protocol for integrating multiple provider endpoints—is consistent with the file structure and README examples showing how connectors are defined and compiled.
Подтверждено: Да

**Novelty checklist:** Is this a new protocol? Partially yes—Monid defines a declarative connector format (provider.ts + endpoint.ts structure) that standardizes how agent tools are described and metered, which is not identical to existing API gateway patterns. Is this a new standard? Yes—it proposes a unified schema and metering model for agent tool integration that positions itself explicitly as "OpenRouter for agent tools," creating a new standard for tool discovery and billing. Is this a new architectural layer? Yes—Monid sits between agents and tool providers as a dedicated metering and discovery layer with compile-time sealed units and content-hash references for tamper checking. Is this a new way of market interaction? Yes—the per-call metering model tied to actual response envelopes (not requests) and per-call endpoint selection via discovery changes how agents negotiate tool access and cost attribution.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, Monid's catalog reaches 1,000+ live connectors with measurable agent request volume, multiple independent agents report successful production integration, and the project becomes recognized as a de facto standard for agent-tool metering in the ecosystem.
**Если ошиблась:** Within 12 months, adoption remains limited to proof-of-concept integrations, the connector catalog stalls below 100 active providers, competing platforms (MCP or similar) gain dominant mindshare for agent-tool integration, or Monid's metering model proves commercially unviable against simpler request-based pricing.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-16 - CANDIDATE: первая оценка

## Связи
- [[MCP как слой интеграции сервисов 2026-06-14]]
- [[MCP как универсальный протокол агентной интеграции 2026-06-14]]
- [[Динамически расширяемая архитектура агентов 2026-06-14]]
- [[Оркестрация множества коммерческих агентов 2026-07-23]]
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
