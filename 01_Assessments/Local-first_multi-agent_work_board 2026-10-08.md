---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Pullboard is a novel local-first verification-gate architecture
  for multi-agent software delivery that enforces mandatory cross-agent review before
  merge, using git-native specs and SQLite state, without SaaS. It exhibits working
  code with self-dogfooding proof but limited third-party adoption evidence, placing
  it at the growing-but-early boundary between prototype validation and production
  maturity.
evidence_log:
- date: '2026-10-08'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: ae9d2057212f705b72d844488c0475097dcb5c84
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-10-08'
  verdict: CANDIDATE
---
# Local-first multi-agent work board

**Дата:** 2026-10-08
**Репозиторий:** https://github.com/pullboard-dev/pullboard
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "Nothing ships until a second agent verifies it."

## What Changes in the Ecosystem
Pullboard introduces a mandatory second-agent verification layer as a structural primitive in multi-agent software delivery—rejection and rework cycles are now auditable, committed artifacts with frozen criteria at claim time. It replaces centralized coordination (one model or human bottleneck) with peer verification across agent models and families, and shifts spec/verification from chat transcripts into durable, enforceable git artifacts. This removes the requirement for external CI platforms or SaaS for agent team governance.

## Reasoning
Pullboard combines existing git and SQLite technologies into a novel multi-agent coordination and verification architecture. It is working software with documented live usage (79 verified items, 42 rejected verdicts recorded on 7 Oct 2026 in self-dogfooding), but adoption signals are limited to early adopter/author workflows; no third-party deployments evident. The project demonstrates maturity markers (test suite, CI/CD badge, security.md, contributing guidelines) but lacks widespread production evidence. Novelty is strong: mandatory cross-agent verification as a git-native primitive is distinct from existing agent frameworks and CI approaches.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims: (1) local-first board living in git repo as SQLite file in .git, (2) SPEC.md workflow with one-line requirements, (3) multi-lane worktrees per agent, (4) second-agent verification before merge, (5) git hooks enforcing PRACTICE.md rules, (6) no hosted dependencies or account needed. Manifest confirms: package.json shows CLI tool (bin/pullboard.js), exports module (src/index.js), includes skills/ directory (Claude integration), docs/ with workflow diagrams, test suite, and git hooks setup. File tree contains SPEC.md, PRACTICE.md, AGENTS.md, pullboard.json config, comprehensive bin/ and src/ structure. Architecture claims are structurally supported—the project provides executable tooling for spec management, agent lane isolation, and verification gates as described.
Подтверждено: Да

**Novelty checklist:** New protocol? Partially—defines a verification-before-merge workflow and spec-driven agent coordination protocol not standard in existing CI/CD or agent frameworks. New standard? No—uses existing git, SQLite, and shell conventions. New architectural layer? Yes—introduces a local verification/gate layer specifically designed to sit between multi-agent builders and merges, with mandatory second-agent sign-off as a native primitive. New way of market interaction? Yes—enables teams to run coding agents with local-first governance (no platform lock-in) and distributed verification without hosted SaaS infrastructure. Three of four criteria met strongly.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, at least one public repository (not the author's) demonstrates Pullboard-managed agent work with >20 items verified by multiple coding agents, logged in pullboard ledger and visible in a shared board.
**Если ошиблась:** Within 12 months, the project is archived, or there is no evidence of any third-party usage, or the gap between README promises (e.g., "works with Claude Code, Codex and any agent you can run from a shell") and actual tested integrations narrows to only one tested agent type, contradicting the multi-agent premise.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-08 - CANDIDATE: первая оценка

## Связи
- [[Human Verification Embedded in Agent Loops 2026-08-04]]
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[Local-First Agent Memory and Cognition Layers 2026-08-04]]
- [[Оркестрация множества коммерческих агентов 2026-07-23]]
- [[Единая_панель_управления_для_кодирующих_агентов 2026-07-19]]
