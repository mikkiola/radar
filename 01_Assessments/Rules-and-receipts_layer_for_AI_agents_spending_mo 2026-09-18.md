---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: AskGrokWallet is a new architectural layer combining contract-enforced
  agent spending policies, threshold-routed human approval, and independently verifiable
  receipts, enabling operators to grant agents autonomous financial capability while
  remaining auditable to third parties.
evidence_log:
- date: '2026-09-18'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 20e0f98c98b3e0c56b2e05b27f83a5cebe0ac016
license_spdx_id: MIT
license_baseline_origin: initial
verdict_history:
- date: '2026-09-18'
  verdict: CANDIDATE
---
# Rules-and-receipts layer for AI agents spending money

**Дата:** 2026-09-18
**Репозиторий:** https://github.com/richard7463/askgrokwallet
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "The rules-and-receipts layer for AI agents that spend money. Small things run · big things ask · everything leaves a receipt"

## What Changes in the Ecosystem
This introduces a verifiable trust boundary for agentic spending: agents can no longer exceed policies enforced at the contract level (not just configuration), operators gain auditability without third-party custody, and any third party can independently verify transaction outcomes via hash-chained receipts anchored to a public chain. The ecosystem shifts from "trust the agent framework + trust the operator" to "agent cannot exceed bounds + outcome is cryptographically verifiable."

## Reasoning
AskGrokWallet combines policy-as-contract-boundary (enforced reverts), threshold-based human approval routing, and standalone-verifiable signed receipts into a unified architectural layer. This is a novel composition solving a real gap in agentic commerce (agents already move money; operators lack enforceable bounds + third-party-verifiable records). Maturity is 3 because the system is live and tested end-to-end on testnet and deployed on mainnet, but explicitly marked "unaudited developer preview" with no production settlement demonstrated yet. State is Growing because it has live product, verified contracts, comprehensive test coverage, and active Runtime NYC 2026 submission momentum.

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** The README claims three load-bearing capabilities: (1) policy enforcement via contract vault reverts (not suggestions), (2) human-in-loop for specific action thresholds (allow/ask/deny compilation), and (3) verifiable receipts with signatures, hash-chained logs, and blockchain anchoring. The file tree confirms contracts/ with deployment addresses on Base mainnet and Sepolia, spec/ with 20 contract tests and standalone verifier (verify-receipt-v1.0.0), and examples/ supporting integration patterns. The TrustLeaseController (ERC-8196 policy + receipt anchors) and BoundlessVault (token custody) contracts are verified deployed. The spec/judge-check.mjs and spec/vectors/ support the verifier claims. The architecture matches the README: agent request → policy enforcement at contract level → signed receipt → anchored log. All three claims are structurally supported.
Подтверждено: Да

**Novelty checklist:** New protocol: Yes — the combination of policy-as-contract-boundary + human-in-loop-at-threshold + hash-chained signed receipts anchored to blockchain is a distinct protocol for agentic commerce governance. New standard: Partially — implements ERC-8196 (Trust Lease standard), claiming alignment but not inventing it. New architectural layer: Yes — sits between agent and wallet as a rules + receipts + verification layer that did not exist as a unified system before. New market interaction: Yes — the operator can now hand a third party a receipt they can verify without trusting the operator or the platform, solving a gap in agentic commerce trust models.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, a public agent framework (Grok, Cursor, Claude, or equivalent) integrates AskGrokWallet as standard governance, and at least one production financial transaction (≥$100 equivalent) settles through its guarded vault with a publicly verifiable receipt cited as audit evidence.
**Если ошиблась:** Within 12 months, no production settlements occur through the system, the verifier is broken by a disclosed vulnerability that is not patched within 30 days, or adoption remains zero (no external integrations, no forks for production use, no third-party receipt verification).

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-18 - CANDIDATE: первая оценка

## Связи
- [[Human Verification Embedded in Agent Loops 2026-08-04]]
- [[Cryptographic Trust as Native Agent Architecture 2026-08-04]]
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[Human-in-Loop_Agent_Verification_Loop 2026-07-29]]
