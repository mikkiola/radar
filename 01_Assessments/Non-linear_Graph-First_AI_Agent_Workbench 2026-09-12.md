---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: PiX establishes a new graph-structured conversation layer enabling
  non-linear, multi-path agent exploration where context automatically follows arbitrarily-created
  branches, dramatically reducing friction compared to traditional linear session
  management in AI workbenches.
evidence_log:
- date: '2026-09-12'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: 0d0a9f34ba50942099543145450b0c695e0369ce
license_spdx_id: null
license_baseline_origin: initial
verdict_history:
- date: '2026-09-12'
  verdict: CANDIDATE
---
# Non-linear Graph-First AI Agent Workbench

**Дата:** 2026-09-12
**Репозиторий:** https://github.com/huang-sh/PiX
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "PiX 的会话不是一条线，而是一张会生长的图：每一轮对话都是图上的一个节点，任何一个节点都可以随时长出新分支。"

## What Changes in the Ecosystem
PiX introduces a graph-structured conversation layer on top of existing agent protocols, enabling parallel exploration paths and non-destructive branching within a single session. Instead of linear chat history, users now navigate a growing tree where any message node can fork into independent branches, each maintaining its own context without requiring session restart or manual state reconstruction. This architectural shift transforms agent workbench interaction from sequential to exploratory, allowing simultaneous comparison and rollback within a single session graph.

## Reasoning
PiX implements a novel architectural abstraction—graph-first session organization with context-following branches—on top of the existing Pi agent platform. The project shows working prototypes (GUI tests, remote runtime tests pass), but lacks evidence of production deployment beyond author use; version 0.0.15 and test-driven validation indicate early-stage maturity. The state is Prototype because GitHub shows development activity but no indicators of external adoption or production hardening yet.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims: (1) non-linear session graphs with branching and context following the branch, (2) arbitrary fork/branch creation from any message node, (3) multi-panel chat display with up to 3 simultaneous branch views, (4) remote Node environment support (SSH/WSL), (5) built-in extensions (@injaneity/pi-computer-use, @ff-labs/pi-fff). Cross-check with manifest: package.json shows @earendil-works/pi-* dependencies (pi-ai, pi-coding-agent, pi-server v0.85.0), @vue-flow/core and @vue-flow/minimap for graph rendering, @xterm/xterm for terminal UI, node-pty for pseudo-terminal support. File tree includes server/, src/, test/ directories with test files for gui, terminal, wsl, ssh, indicating multi-panel and remote runtime capabilities are implemented. The manifest confirms the graph-based architecture (vue-flow) and remote environment setup scripts (install-wsl-server.mjs, wsl-server-test.mjs). Core UI claims (branching, context following) are structurally supported by @vue-flow dependencies and test coverage (test:gui, test:gui:wsl, test:gui:ssh). The claims are internally consistent with the available code structure.
Подтверждено: Да

**Novelty checklist:** New protocol? No—it uses existing Pi agent protocol. New standard? No—it wraps existing standards. New architectural layer? Yes—the graph-first session organization with arbitrary branching and context-following is a new architectural abstraction layer for agent conversation management that restructures how agent sessions are organized (tree/graph instead of linear timeline). New way of market interaction? No—it is a workbench tool, not a market mechanism. At least one 'yes' criterion met.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** In 12 months, PiX reaches version 1.0+, demonstrates multi-user collaborative branching sessions in production, and shows adoption by at least 3 independent AI teams or enterprises managing complex multi-path agent workflows through graph-based session branching.
**Если ошиблась:** In 12 months, PiX remains at version 0.x with limited external adoption, graph branching is reverted or deprecated due to usability issues, or the project enters maintenance mode with no active new feature development beyond bug fixes.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-12 - CANDIDATE: первая оценка

## Связи
- [[Collaborative_AI_агенты_в_shared_workspaces 2026-06-24]]
- [[AI_Software_Engineering_Workflow_for_Agents 2026-08-13]]
- [[Self-hosted_контроль_и_управление_агентами 2026-06-12]]
- [[Локальная_плоскость_контроля_агентских_DAG 2026-07-23]]
- [[Human-in-Loop_Agent_Verification_Loop 2026-07-29]]
