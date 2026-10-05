---
status: CANDIDATE
maturity_score: 3
novelty_score: 4
state_value: Growing
state_confidence: low
assertion_vector: .dai establishes a new plain-text memory format standard that inverts
  control from vendor-locked services to user-owned files, achieving competitive retrieval
  performance while enabling any model, language, or tool to access unified agent
  memory through an open specification.
evidence_log:
- date: '2026-10-05'
  event_type: state_transition
  state_value: Growing
  state_confidence: low
root_commit_sha: 2b0ecfd4e9614159fef7df9a0696489739b811ce
license_spdx_id: Apache-2.0
license_baseline_origin: initial
verdict_history:
- date: '2026-10-05'
  verdict: CANDIDATE
---
# Open plain-text AI memory format

**Дата:** 2026-10-05
**Репозиторий:** https://github.com/Kerneta/daidocs
**Уверенность:** в карантине
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v2.0
**Источник:**
  файл: README
  локация: не указана
  цитата: "An open plain-text format for AI memory. Your assistant's memory becomes files on your disk that you can open, grep and keep."

## What Changes in the Ecosystem
The project shifts AI memory from vendor-controlled databases to user-owned plain-text files, breaking the lock-in pattern where memory is accessible only through proprietary APIs. It establishes a new interchange format that allows any language, model, or tool (including grep and git) to access the same memory store, creating interoperability where previously none existed. The MCP server integration standardizes how memory is surfaced to agents, making memory a composable infrastructure component rather than a monolithic service.

## Reasoning
Daidocs introduces a genuinely novel format and architectural inversion (memory as files, not services) with credible benchmarks showing competitive performance (83% on LongMemEval-S, second place). However, it is in early adoption phase - launched Sep 2026, version 4.4.36 suggests recent iteration but the ecosystem of readers/writers in multiple languages is still nascent. The MCP server integration is solid and the specification is rigorous, but production adoption signals are mixed (active Discord community but limited evidence of enterprise use).

## Maturity x Novelty
**Maturity:** 3/5
**Novelty:** 4/5

## Self-Check (CoVe)
**Cross-validation (README vs manifest/files):** README claims ".dai" is an open plain-text format for AI memory, language/model-independent, readable by grep and any LLM. Manifest confirms: package.json lists bin entries for daidocs CLI, mcp_server.mjs for MCP integration, and file tree includes spec/DAIDOCS-STANDARD.md, docs/RESULTS.md with benchmark evidence, lib/ with implementation code, and prompts/ directory. Root files include MANIFEST.sha256 for provenance verification. The architecture claimed (plain-text YAML+JSON+text structure, MCP server, multi-model support) is structurally supported by the presence of MCP SDK dependency, the reference engine CLI tools, and documented standard specification.
Подтверждено: Да

**Novelty checklist:** Is this a new protocol? Partially yes - .dai is a novel plain-text interchange protocol for AI memory that differs from existing SaaS memory services. Is this a new standard? Yes - the spec/DAIDOCS-STANDARD.md defines a new file format standard for AI-readable memory. Is this a new architectural layer? Yes - it introduces a file-based memory abstraction layer between agents and traditional SaaS-locked memory systems. Is this a new way of market interaction? Yes - it inverts the model from vendor-locked memory-as-a-service to user-owned memory-as-a-format, allowing any model/tool to read the same store.
Проходит: Да

## Falsifiable Hypothesis
**Если права:** Within 12 months, the .dai format is adopted as a native memory store by at least two major code assistant platforms (beyond Claude/Cursor), demonstrating that the format becomes a de facto standard for agent-readable memory interchange.
**Если ошиблась:** Within 12 months, the project shows declining commit frequency, reduced Discord activity, or the benchmark leadership is lost to competing memory systems that achieve similar or better performance with simpler integration, indicating the format's market traction plateaus.

## Оценка Claude

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- 2026-10-05 - CANDIDATE: первая оценка

## Связи
- [[Persistent_Cognition_Sidecar_Architecture 2026-08-02]]
- [[Персистентная_локальная_память_для_кодирующих_аген 2026-06-28]]
- [[Local-First_Project_Memory_for_AI_Agents 2026-09-06]]
- [[Continual_Learning_Infrastructure_for_Agents 2026-09-03]]
