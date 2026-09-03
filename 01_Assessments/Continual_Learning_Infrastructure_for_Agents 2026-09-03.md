---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Reef introduces a novel continual learning infrastructure layer
  that decouples agent serving from training via structured feedback loops and versioned
  artifacts, enabling agents to improve without redeployment; the architecture is
  sound but ecosystem adoption and production hardening are still emerging.
evidence_log:
- date: '2026-09-03'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 73d5d807112f3c4bd8fc713b17389d1480d4d339
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-09-03'
  verdict: CANDIDATE
---
# Continual Learning Infrastructure for Agents

**Дата:** 2026-09-03
**Репозиторий:** https://github.com/Human-Agent-Society/reef
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "Reef is infrastructure that serves an entire continual learning backend. Reef exposes standardized http endpoints so that you can download agents just like how you download `codex` or `opencode` using `curl`, and so that your agent can send its model requests to Reef's inference endpoint instead of the provider's. The only difference is that, Reef constantly evaluates your agent behavior and improves the served harness and model weights in the backend."

## What Changes in the Ecosystem
Reef shifts agent deployment from static snapshots to continuously-improving versioned artifacts backed by feedback-driven training loops. It introduces a persistent interaction recording and feedback matching layer that decouples agent serving from training orchestration. This creates a new ecosystem primitive: agents that improve in-place without redeployment, treating model weights and harness logic as managed, evolving state rather than immutable binaries.

## Reasoning
Reef is a novel architectural layer for continual agent learning with structured feedback-training loops and artifact versioning, but the project is still early-stage: limited production deployment evidence (SAO example is experimental), active development (CI badges, recent commits implied by version control), and the ecosystem around continual learning for agents is nascent. The novelty is genuine (new protocol layer + architectural abstraction), maturity is low (prototype-to-early-working state), and momentum is growing (recent launch, organizational backing, documented roadmap).

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims Reef is "continual learning infra" with standardized HTTP endpoints for downloading agents and a four-step loop (Serve, Observe, Grow, Commit). The manifest and file structure support this: pyproject.toml defines entry points (`reef` CLI, `reef-native`), dependencies for serving/training (aiohttp, huggingface_hub, ray, transformers), and optional dependency groups (slime for GPU training, wandb for experiment tracking). The file tree shows reef/ with service/, runtime/, train/, records.py, artifact/, recipe/, and surface/ modules—each matching the four-step architecture described in the README table. The SAO example deployment recipe is present in recipes/sao/. The inference endpoint implementation and harness evolution logic are referenced but not fully readable from the provided manifest, yet the structural skeleton supports the claimed capability.
Подтверждено: Да

**Novelty checklist:** New protocol? Partially—Reef adds a non-standard continual learning backend protocol (recipe-based, feedback-driven model/harness updates) on top of OpenAI-compatible chat endpoints, so yes, a new coordination layer protocol. New standard? No—it extends OpenAI/Anthropic standards but does not propose a new formal standard. New architectural layer? Yes—Reef introduces a dedicated continual learning persistence and evaluation layer (records, processors, evaluation, artifact versioning) between serving and training that did not exist as a unified system before. New way of market interaction? Partially—the agent-as-downloadable-artifact with background improvement model is novel in framing, though conceptually related to existing model versioning and federated learning ideas.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, a third-party agent framework or model provider (e.g., an existing open-source agent library or commercial LLM service) publicly announces integration with Reef for continual learning, demonstrating adoption beyond the authors' own SAO example.
**Если ошиблась:** Within 12 months, the project is archived or sees no commits for 6+ months, and no external projects adopt Reef's continual learning backend, indicating the architectural approach did not find traction in the agent ecosystem.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-03 - CANDIDATE: первая оценка

## Связи
- [[Local-First Agent Memory and Cognition Layers 2026-08-04]]
- [[Динамически расширяемая архитектура агентов 2026-06-14]]
- [[Self-hosted суверенитет над агентной инфраструктурой 2026-06-14]]
- [[Верификация и доверие к действиям агентов 2026-06-14]]
- [[MCP как слой интеграции сервисов 2026-06-14]]
