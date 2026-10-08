---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: AgentEnv Framework establishes a new protocol-driven containerized
  environment abstraction and deployment model for agentic RL evaluation, with working
  SDK and multi-backend support, but remains in beta with limited external adoption
  signals and requires protocol/deployment patterns to prove ecosystem viability beyond
  single-vendor.org infrastructure.
evidence_log:
- date: '2026-10-08'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 816b0c4973821b4aa8f6fda70e4aed3ecc9d27c7
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-10-08'
  verdict: CANDIDATE
---
# Agentic Environment Framework with Protocol

**Дата:** 2026-10-08
**Репозиторий:** https://github.com/scaleapi/agentenv-framework
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "AgentEnv Framework is a Python SDK and CLI for building, deploying and running agentic environments and the tasks that grade agents inside them. Environments are containerized servers that speak the open `agentenv-framework-protocol`"

## What Changes in the Ecosystem
This framework introduces standardized containerized environments as first-class deployment objects with protocol-based communication, replacing ad-hoc environment definitions. It shifts the RL/agentic evaluation workflow from monolithic simulator ownership to composable, versioned, gateway-deployed environments. The plugin system creates a market structure for environment builders, task authors, and sandbox providers to contribute independently.

## Reasoning
AgentEnv Framework is a substantially complete SDK (v0.9 beta, PyPI published, documented) with working CLI, multi-backend sandbox support, and active plugin architecture. The core novelty is the explicit agentenv-framework-protocol and the deployment model (containerization + versioning + gateway pattern), not a new protocol implementation. Maturity is 3 (working with adoption signals—PyPI presence, documentation site, multiple optional backends) rather than 5 because beta status, version 0.9, and absence of visible large-scale production deployments prevent it from being production-hardened. State is Growing: active development (0.9.1291 versioning suggests frequent releases), documentation investment, and multi-backend expansion signal increasing momentum rather than maintenance-only stasis.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** YES. The README claims AgentEnv Framework is "a Python SDK and CLI for building, deploying and running agentic environments" that "speak the open `agentenv-framework-protocol`". The manifest confirms: (1) the project name is `agentenv-framework` v0.9.1291, published to PyPI, (2) it depends on `agentenv-framework-protocol>=0.1.0` as a separate package, (3) the CLI command `agent-env` is provided, (4) documentation domain www.agentenvframework.com/docs is referenced, (5) plugin contract/registry system with entry points is documented, (6) support for Docker containerization, multiple sandboxes (e2b, Modal, Sail), state providers, artifacts, and explorers is reflected in dependencies (e2b~=2.46.4, modal>=1.5.2, sail optional dep) and optional feature groups. The file structure includes packages/, src/, tst/ directories consistent with a multi-module SDK. This claim is structurally supported.
Подтверждено: Да

**Novelty checklist:** Protocol: YES - agentenv-framework-protocol is explicitly named as an open standard that containerized environments "speak", a new communication contract for agentic systems. Standard: PARTIAL - the protocol acts as a de facto standard but is tied to this ecosystem, not established as an industry standard yet. Architectural layer: YES - the framework introduces a standardized gateway+versioned-image deployment layer for agent environments, distinct from prior monolithic RL frameworks or raw agent SDKs. Market interaction: PARTIAL - establishes a plugin marketplace model (entry points for envs, task steps, artifacts, sandbox providers) which is a structural change to how RL environment components can be composed, but not fundamentally new to Python ecosystems. At least two "yes" answers (protocol + architectural layer) satisfy the novelty threshold.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, 3+ independent third-party environment plugins (beyond Scale AI's own) are published to PyPI, registered via entry points, and adopted by publicly documented RL/agent research projects or competitions.
**Если ошиблась:** Within 12 months, the project enters maintenance mode (6+ months without non-patch releases), the agentenv-framework-protocol is abandoned or absorbed into another standard (e.g., MCP), or major version 1.0 is not released, indicating the framework did not achieve the maturity/adoption needed to become a de facto ecosystem standard.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-08 - CANDIDATE: первая оценка

## Связи
- [[Local-First_Multi-Agent_Software_Platform 2026-09-17]]
- [[MCP_сервер_GitHub_v2 2026-06-07]]
- [[Execution_Safety_Layer_for_AI_Agents 2026-09-11]]
- [[AI_Agent_Authorization_Middleware 2026-08-15]]
