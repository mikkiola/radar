---
status: VALIDATED_SHIFT
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: Vantage is a novel evidence-based work tracking architecture that
  enforces proof-of-completion for AI agent tasks through local-first, protocol-agnostic
  verification, distinct from prior log-centric or claim-based agent monitoring approaches.
evidence_log:
- date: '2026-10-15'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: 52ce9143f40ef8b5b73af7a743f9b5686aece80e
license_spdx_id: null
license_baseline_origin: initial
verdict_history:
- date: '2026-10-15'
  verdict: CANDIDATE
- date: '2026-10-29'
  verdict: VALIDATED_SHIFT
---
# Evidence-Based AI Work Tracker

**Дата:** 2026-10-15
**Репозиторий:** https://github.com/ymatrix1/vantage
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README.md
  локация: не указана
  цитата: "Vantage tracks **work items**, not sessions. Each item moves along one evidence-based track, the **A2V track** from the [A2V: Asked to Verified](docs/METHOD.md) method: Asked → Built → Proven → Reviewed → Shipped → Verified. A card moves only on evidence: a git diff, a test or data check that ran after the last edit, a PR approval, a deploy, a clean monitoring window. What an agent *says* never moves a card."

## What Changes in the Ecosystem
Vantage introduces a new verification layer in the AI agent ecosystem that decouples work tracking from agent claims, requiring evidence (git diffs, test results, PR approvals) for stage progression. This shifts the trust model from agent-reported completion to externally observable facts, creating a new category of work orchestration infrastructure for agent-assisted development. The local-first architecture and daemon-based design enable persistent, transparent work state independent of agent session lifecycle.

## Reasoning
Vantage introduces a novel A2V (Asked-to-Verified) methodology as an architectural layer for agent work tracking, moving beyond agent claims to evidence-based stage transitions. The Phase 1 implementation covers Claude Code and git with local-first persistence, but explicitly states it "has not been used day to day for a week yet" and lacks Reviewed/Shipped/Verified stages, placing it in early prototype territory with significant forward novelty.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** Yes. The README claims: (1) work item tracking across agents with an A2V six-stage pipeline (Asked→Built→Proven→Reviewed→Shipped→Verified), (2) evidence-only stage advancement (git diff, test checks, PR approval, deploy, monitoring), (3) Claude Code hook integration, (4) local SQLite store at ~/.vantage. The manifest confirms a TypeScript monorepo with @vantage/ui, @vantage/cli packages and Node.js 22.5+ requirement for node:sqlite. The file tree shows packages/cli, plugin/vantage for Claude Code integration, docs/METHOD.md and docs/install-for-agents.md, and .claude/ for configuration—all structural support for the claimed A2V pipeline, hook capture, and local-first design.
Подтверждено: Да

**Novelty checklist:** New protocol: Yes—the A2V (Asked to Verified) evidence-based work pipeline is a new protocol not previously standardized for AI agent output verification. New standard: Partially—it proposes a new de-facto standard for measuring agent work completion beyond agent logs, but not formally standardized yet. New architectural layer: Yes—the local-first spool→SQLite→daemon→web-ui verification layer between agents and work item visibility is a new architectural primitive absent in prior agent frameworks. New way of market interaction: No—it does not change how buyers/sellers or platforms transact.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, Vantage completes Phase 2–3 (Reviewed, Shipped, Verified sources), publishes to npm, and reports daily active users tracking work across Claude Code, with measurable adoption beyond the author in at least two public GitHub repositories.
**Если ошиблась:** Within 12 months, the project remains in Phase 1, has no npm release, no day-to-day usage beyond the author for more than a week, and the repository shows no commits from external contributors or forks with substantive changes.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-29 - VALIDATED_SHIFT: карантин пройден (14+ дней), репозиторий активен - promote_candidates
- 2026-10-15 - CANDIDATE: первая оценка

## Связи
- [[Верификационный_шлюз_для_агентских_действий_Claude 2026-06-14]]
- [[Execution_Safety_Layer_for_AI_Agents 2026-09-11]]
- [[Persistent_Cognition_Sidecar_Architecture 2026-08-02]]
