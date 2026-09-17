---
status: CANDIDATE
maturity_score: 2
novelty_score: 4
state_value: Prototype
state_confidence: low
assertion_vector: RWAlly is a novel on-chain protocol that atomically separates agent
  judgment (proposal) from execution authority (member vote), with immutable contracts
  and verifiable governance records; it is deployed but not launched, with procedural
  deployment errors and no path to full operation until open gates pass.
evidence_log:
- date: '2026-09-17'
  event_type: state_transition
  state_value: Prototype
  state_confidence: low
root_commit_sha: 73944203c3e37287e2423eda6e25eedf2973e775
license_spdx_id: NOASSERTION
license_baseline_origin: initial
verdict_history:
- date: '2026-09-17'
  verdict: CANDIDATE
---
# AI-governed on-chain index vault protocol

**Дата:** 2026-09-16
**Репозиторий:** https://github.com/SlumperSan/agent-governed-vaults
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "Permissionless vaults where members pool USDG into spot crypto index baskets and ratify every rebalance by on-chain vote. Proposal rights follow stake, not operatorship: an AI operator proposes as a member, and operatorship confers no authority to vote, execute, pause, reprice, or move member funds"

## What Changes in the Ecosystem
The ecosystem gains a primitive for verifiable, operator-neutral governance of agent-proposed index baskets: members vote on proposals, operator confers zero execution authority, and the immutable contract record ties every rebalance to a specific proposal and vote outcome. This decouples agent judgment (proposal) from execution authority (member consensus) in a way that was not available before. It also creates a new market interaction model: on-chain index funds where the basket composition is a timestamped record of member ratification, not an off-chain decision published post-hoc.

## Reasoning
RWAlly introduces a novel governance primitive: agent-proposed but member-ratified rebalancing with strict immutability (no upgrades, pauses, or admin keys) and verifiable on-chain records. However, maturity is low because (1) deployment itself has known procedural errors (first vaults created by EOA instead of Safe), (2) launch verdict is explicitly NO-GO with multiple gates open (soak drills, canary re-run both marked STALE), (3) only two vaults hold real funds with very small amounts ($20 USDG and ~0.002 WETH), and (4) the audit was private and not independently verifiable. The protocol is real and deployed, but under explicit launch hold and with minimal real-world validation.

## Maturity x Novelty
**Maturity:** 2/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims: immutable contracts (no proxy/pause/upgrade/admin), agent-proposed rebalances ratified by on-chain vote, USDG settlement on Robinhood Chain (4663), deployed with real funds in two vaults. Manifest shows Solidity contracts (forge build, forge test) in contracts/ directory, deployment configs at contracts/config/deployments/, evidence docs, and supporting backend (indexer, canary, API, agent-SDK). File tree confirms VaultFactory, VaultCore, Governance, ChainlinkOracle, and adapters exist. Deployment addresses are committed in robinhood-mainnet.json. However, README explicitly states "launch verdict: NO-GO" and "deployment record said they must not be" - the first vaults were created by deployer EOA instead of Safe, violating intended procedure. The README is transparent about deployment bugs but does not hide them. The architectural claim (immutable, vote-ratified rebalance, agent-as-member not operator) is structurally supported by contract names and governance docs cited.
Подтверждено: Да

**Novelty checklist:** Is this a new protocol? YES - commit-reveal governance with agent-as-proposer-not-operator, member-ratified rebalance, and strict immutability is a novel on-chain governance primitive for index funds. Is this a new standard? PARTIALLY - it could become a standard for decentralized fund governance, but it is currently one implementation. Is this a new architectural layer? YES - it introduces a layer where agent proposals are separated from execution authority, and all rebalancing authority is held by vote-locked members, not operators. Is this a new way of market interaction? YES - pooled index exposure with on-chain governance and verifiable record of proposal-vote-execution is a new market primitive (not a CEX, not a traditional fund structure, not a simple yield farm).
Проходит: Да

## Falsifiable Hypothesis
**Если права:** In 12 months, the launch verdict gate 3 (soak drills) and gate 6 (canary re-run) are re-executed, pass, and gate 1 (external review attestation) stands, allowing official launch permission; vaults reach $1M+ TVL on mainnet with stable governance execution across multiple proposals.
**Если ошиблась:** In 12 months, the project has not exited NO-GO status, vaults on Robinhood mainnet remain dormant or shrink below $5K TVL, or a critical issue surfaces during the open gates that forces architectural redesign; the project remains a proof-of-concept without production adoption.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-09-16 - CANDIDATE: первая оценка

## Связи
- [[Cryptographic Trust as Native Agent Architecture 2026-08-04]]
- [[Верификация как встроенная архитектура доверия 2026-07-23]]
- [[Открытые протоколы координации агентов 2026-06-25]]
- [[Human Verification Embedded in Agent Loops 2026-08-04]]
