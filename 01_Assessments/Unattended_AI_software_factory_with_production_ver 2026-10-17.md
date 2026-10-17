---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: Cromford encodes a new verification-first orchestration layer for
  unattended LLM code delivery, where each stage gate is deterministic until a genuine
  reading-comprehension question is reached, and no artifact proceeds without proof
  that prior stage claims are true—a structural pattern for trusted autonomous loop
  execution that did not exist in open-source agent infrastructure before.
evidence_log:
- date: '2026-10-17'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 5f91e826ef6e0e31e3ee060230c678e2b2463416
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-10-17'
  verdict: CANDIDATE
---
# Unattended AI software factory with production verification

**Дата:** 2026-10-17
**Репозиторий:** https://github.com/cromford-ai/cromford
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: не указана

## What Changes in the Ecosystem
Cromford introduces a formalized verification-first orchestration layer that changes how unattended LLM agents interact with production systems: each stage (triage, plan, build, review, merge, deploy, QA) has independent gates and budgets, and no artifact proceeds without explicit proof that prior claims were true. This shifts the ecosystem from "can a model write code" to "can a loop nobody is watching be trusted with production"—requiring deterministic pre-LLM checks, adversarial review, deployment confirmation, and post-merge verification as non-optional architectural primitives. Cost tracking and multi-vendor failover become structural components, not add-ons.

## Reasoning
Cromford is a working implementation of unattended code-to-production automation with production-like characteristics (evidence: comprehensive test suites, multi-stage gates, documented self-hosting path, cost tracking, multi-vendor failover). However, it is not yet widely adopted beyond the authors and early users (no public deployment counts, limited GitHub stars relative to sophistication, self-hosting still requires manual resource creation). The novelty is genuine: the verification contract (every stage refuses work unless prior stage's claims are proven true) and the adversarial review loop with deployment verification are new architectural primitives for LLM agent orchestration. Momentum is growing: active test suite maintenance, detailed docs, explicit multi-machine scaling plans indicate active development addressing real use-case friction.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims Cromford is a complete unattended pipeline from ticket to production (triage → plan → build → review → preview QA → merge → deploy-verify → post-merge QA). The file tree confirms this: bin/ contains stage-specific runners (run-triage.sh, run-build.sh, review-prs.sh, merge-conductor.sh, deploy-train.sh, postmerge-qa.sh); tests/ includes load-bearing suites for design integrity (fleet-projects-not-hardcoded-test.sh, cron-fleet-parity-test.sh, agent-call-provider-order-test.sh); docs/ includes stage specifications (RUN-BUILD-GRAPH.md, DB-COORDINATION-SPEC.md); configuration is data-driven (fleet.conf, catalog/, env-templates/). The README's claim about multi-vendor lane failover (claude → grok → openrouter → fireworks), cost tracking (cost.csv, agent-call.sh), and adversarial review is structurally supported by bin/agent-call.sh, bin/cost-rows-push.sh, and bin/rule-miner.sh in the manifest. MCP integration is present (mcp/). The architecture described matches the file organization.
Подтверждено: Да

**Novelty checklist:** New protocol? No—uses existing GitHub/Fly/Cloudflare APIs. New standard? Arguably yes—the per-stage deterministic gate + LLM + verification loop (triage/plan/review/deploy-verify/post-merge QA) as a formalized protocol for unattended code delivery is not a pre-existing standard in open-source; this encodes structural assumptions about when to refuse work and how to verify outcomes. New architectural layer? Yes—the verification contract (stage outputs validated by subsequent stages, deployment confirmation mandatory before post-merge QA, cost tracking as first-class pipeline state) is a new orchestration layer between CI/CD and LLM agents. New way of market interaction? Arguably yes—the multi-vendor lane failover with price tracking and tier-based automerge creates a new market signal (which vendor to use, when to degrade gracefully, cost visibility) that did not exist before in open-source agent infrastructure.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, Cromford's self-hosting docs enable 3+ public independent deployments (forks with production activity) that report successful unattended PR merges with cost tracking and deploy verification, demonstrating the pattern scales beyond the original authors.
**Если ошиблась:** Within 12 months, no independent public deployments report success, the project stalls on self-hosting friction (manual resource creation remains the blocker), and commit frequency drops to <2/month, indicating the pattern is harder to generalize than the architecture suggests or adoption barriers are higher than documented.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-17 - CANDIDATE: первая оценка

## Связи
- [[Human Verification Embedded in Agent Loops 2026-08-04]]
- [[Execution_Safety_Layer_for_AI_Agents 2026-09-11]]
- [[Верификационный_шлюз_для_агентских_действий_Claude 2026-06-14]]
- [[Local-First_Multi-Agent_Software_Platform 2026-09-17]]
