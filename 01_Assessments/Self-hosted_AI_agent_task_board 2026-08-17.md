---
status: VALIDATED_SHIFT
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: OverClick introduces a contract-based, MCP-native task board where
  human-written verification scripts replace subjective review, and agents autonomously
  claim work while reporting measurable cost (tokens, duration, model) as a native
  board primitive, enabling decoupled agent orchestration with embedded trust verification.
evidence_log:
- date: '2026-08-17'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
- date: '2026-09-01'
  event_type: ci_broken
root_commit_sha: ce28000c38a5ce9f495139dad8fd81eb03c74f73
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-08-17'
  verdict: CANDIDATE
- date: '2026-08-31'
  verdict: VALIDATED_SHIFT
---
# Self-hosted AI agent task board

**Дата:** 2026-08-17
**Репозиторий:** https://github.com/ustoppble/overclick
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "OverClick is a self-hosted task board for hybrid human + AI-agent teams. Humans decide and review; agents execute. The board is just an interface, a database, and an MCP server. Any MCP-capable coding agent (Claude Code, Codex, Gemini CLI, Overclock, ...) connects to it, claims cards, does the work on its own machine, and reports back with evidence and real telemetry: tokens per model, and time."

## What Changes in the Ecosystem
OverClick replaces unstructured task queues with a structured contract model where humans write tests before work begins and agents report measured telemetry (tokens, duration, model used). This embeds verification-as-architecture into agent orchestration, making cost and evidence native to the board, not bolted on. The MCP-native design creates a reusable protocol for any MCP-capable agent to interact with any OverClick board, decoupling agent implementation from task management infrastructure.

## Reasoning
OverClick introduces a structurally novel coordination primitive: contract-based task cards with embedded human verification loops and measured agent telemetry, native to MCP. The maturity is low (v0.1, self-described as "early and moving fast") with no evidence of production adoption beyond proof-of-concept, but the architectural novelty is high—it reframes agent-human collaboration around contracts and measurable outcomes rather than tickets.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims an MCP-native task board with specific capabilities: contract-based cards (What/Why/How), harness policies, token/time telemetry per card, RFC support, git-convention tracking, and optional cost tracking. The manifest shows package.json with a monorepo structure (packages/, apps/), explicit MCP SDK reference expected in dependencies, Docker support (Dockerfile, docker-compose.yml), and the file tree confirms modular architecture. The project version 0.1.9 and "Status: Early and moving fast" statement align with the codebase being early-stage. The core MCP surface (18 tools listed) is architectural, not demonstrated in manifest alone, but the presence of docs/mcp.md, Docker setup, and database migration scripts (db:migrate, db:seed, db:generate) structurally supports the claim of a functioning self-contained system. However, no evidence of production deployment, real telemetry capture mechanism, or multi-agent validation is visible in the manifest.
Подтверждено: Да

**Novelty checklist:** Is it a new protocol? Yes—the specific combination of MCP as agent-to-board communication with contract-based card semantics and embedded telemetry (tokens per model, duration) appears novel. Is it a new standard? Partially—it defines a new MCP surface standard (18 tools, atomic claims, typed errors) for agent task coordination, not yet adopted elsewhere. Is it a new architectural layer? Yes—it introduces a verification and validation layer between agent execution and human review, native to the board schema. Is it a new way of market interaction? Yes—it shifts from ticket-based (human-centric) to contract-based (agent-centric) execution models where agents report real cost/time/evidence and humans validate via pre-written scripts, not post-hoc review.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, a third-party MCP-capable agent (not authored by OverClick team) successfully claims and validates a multi-step card on a public or well-documented OverClick instance, with token/time telemetry properly captured and reported through the board UI.
**Если ошиблась:** Within 12 months, the project remains unmaintained or is archived, or the core claim that agents can autonomously claim and deliver cards over MCP with human validation is deprecated or replaced with a non-MCP approach.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-08-31 - VALIDATED_SHIFT: карантин пройден (14+ дней), репозиторий активен - promote_candidates
- 2026-08-17 - CANDIDATE: первая оценка

## Связи
- [[MCP как универсальный протокол агентной интеграции 2026-06-14]]
- [[Human Verification Embedded in Agent Loops 2026-08-04]]
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[Self-hosted суверенитет над агентной инфраструктурой 2026-06-14]]
- [[Оркестрация множества коммерческих агентов 2026-07-23]]
