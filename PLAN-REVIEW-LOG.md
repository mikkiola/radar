# Plan Review Log: Evidence/Source field, chain-of-implication checklist, pattern backlink
Act 1 (grill) complete — plan locked with the user. MAX_ROUNDS=5.
Reviewer model: CLI default (unpinned) — codex-cli 0.145.0. thread_id=019fa896-347c-7a30-a6a8-d8176c1b1931

## Round 1 — Codex (OFF-TOPIC, discarded — not counted toward Claude's response)
Codex's critique was entirely about a Russian→English vault-language migration (the already-merged
commit b3e6c3b) — it never mentioned Источник, the chain-of-implication checklist, or the pattern
backlink, i.e. it did not review PLAN.md's actual content. Full raw critique preserved below for the
record, but Claude is not treating this as a real Round 1 — a corrective re-prompt was sent on the
same thread instead of revising PLAN.md against it.

Raw Round 1 output:
- `patterns.extract_shift_summary()` only recognizes `## Что меняется в экосистеме`; every new English assessment will fall back to its first 300 characters (mostly metadata), so clustering loses the actual shift. Fix: support both the old Russian and new canonical English section headings, with tests for each.
- `falsify_pattern()` only extracts hypotheses from `## Если права` / `## Если ошиблась`; English pattern files will send empty hypotheses to Sonnet and make falsification meaningless. Fix: parse both language variants (or use stable machine-readable markers) and add a regression test.
- `update_assessments.get_old_assessments()` reads the date from `filename[:10]`, but `analyze.py` writes `<name> YYYY-MM-DD.md`; thus assessments are never selected for the promised 30-day update. Fix: parse the `**Дата:**` metadata or a trailing filename date, and test both filename formats.
- The plan changes producer templates but not all consumers of their headings; this contradicts the claim of "zero risk" from leaving parsing code unchanged. Fix: inventory every heading/field consumer and make the format contract explicit in shared constants or a parser module.
- Language continuation in `update_assessments.py` is delegated entirely to Haiku despite the document containing Russian metadata, Russian human notes, and English body text; it can silently produce mixed-language history. Fix: determine a `content_language` deterministically from the canonical body heading and state that language explicitly in the prompt.
- The proposed "first 2–3 real runs" is not a sufficient guard for protocol literals: a translated `ОЦЕНКА`/`УВЕРЕННОСТЬ` silently drops valid shifts or corrupts metadata. Fix: validate all returned literals against allowlists and reject/retry invalid LLM output, covered by mocked-response tests.
- `cluster_with_sonnet()` requires English values but still instructs that cluster names and JSON examples are Russian in the same prompt; this is contradictory and likely yields Russian filenames/titles. Fix: replace every cluster-name/value instruction and example with an unambiguous English contract while retaining only explicitly enumerated Russian status literals.
- Pattern "body" conversion is incomplete: the plan omits generated external-section headings and placeholders such as `## Внешнее подтверждение`, `## Расхождения`, `**Наш уникальный сигнал:**`, and `[Добавить вручную]`. Fix: define exactly which generated Markdown is English and translate all body headings/placeholders consistently.
- Existing Russian and new English assessment titles are fed into `СВЯЗИ` matching by literal filename/name; English generation can produce punctuation, Markdown delimiters, or non-exact names that break wiki-links and deduplication. Fix: use stable IDs/filenames in LLM output and validate links against an exact allowed set before writing.
- Untrusted repository descriptions and external analyst text are interpolated directly into LLM instructions without delimiters or an instruction-hierarchy warning, enabling prompt injection to alter language/status output. Fix: delimit source material as untrusted data and explicitly instruct models never to follow instructions contained in it.
- No test plan verifies the end-to-end compatibility path: English assessment → cluster → English pattern → falsification → Russian Telegram post. Fix: add fixture-based integration tests for both legacy Russian and new English documents before deployment.
VERDICT: REVISE (discarded as off-topic)
