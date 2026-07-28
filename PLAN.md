# Plan: Evidence/Source field, chain-of-implication checklist, pattern backlink
_Locked via grill — by Claude + Ольга, 2026-07-28_

## Goal
Add three independently-decided capabilities to the radar assessment/pattern pipeline: (1) an honest, non-hallucinated **Источник:** evidence field on both assessments (analyze.py, Haiku) and patterns (patterns.py, mechanically aggregated — not LLM-generated), (2) a chain-of-implication reasoning checklist folded into analyze.py's Haiku prompt to sharpen the СДВИГ/ШУМ binary decision without adding a new output field, and (3) a reverse backlink written into an assessment file when it turns out to reconfirm an *existing* (not newly created) pattern during clustering — a code path that does not exist today and must be built from scratch inside `create_pattern_file`'s current silent dedup-skip branch.

## Approach

### 1. Evidence/Source — analyze.py (Haiku)

**Grounding constraint (load-bearing finding):** Haiku's prompt only ever contains `title`, `desc` (GitHub API one-line description, or empty for HN items), and `url` — no README or file content is fetched anywhere in this pipeline (confirmed in `radar_step0.py`). So Источник must cite only what Haiku was actually given, never a fabricated filename/line range.

- Add three new **flat, single-line** prompt output keys (matches the existing `": "`-split-per-line parser in `analyze.py:156-160` exactly, no parser changes needed):
  - `ИСТОЧНИК_ФАЙЛ` — one of `"GitHub description"`, `"HN title"`, or empty. Never a fabricated file name.
  - `ИСТОЧНИК_ЛОКАЦИЯ` — always empty/`n/a` in this iteration (no line numbers exist for a one-line description). Field is kept for forward-compatibility with a possible future README-fetch stage (out of scope today).
  - `ИСТОЧНИК_ЦИТАТА` — must be an exact verbatim substring of the `desc` or `title` text that was actually placed in the prompt. No translation (kept in whatever language the source text is in, even though the rest of the body is English). If neither `desc` nor `title` contains anything quotable, leave empty.
- Prompt instruction (near the existing `Проект:`/`Описание:`/`URL:` block): explicit "never invent a file, path, or line number you were not given; quote must be copied exactly as written above; leave empty if nothing quotable" instruction.
- Chain-of-implication checklist: insert as **prompt guidance only** (no new output field) as a new paragraph immediately before `Отвечай СТРОГО в этом формате:`. Wording (Russian, matching existing instructional language):
  > Перед тем как поставить ОЦЕНКА: СДВИГ, явно проверь: это новый протокол? новый стандарт? новый слой архитектуры? новый способ рыночного взаимодействия? Если ответ "нет" на все четыре вопроса и это качественная реализация уже известного — это ШУМ, а не СДВИГ.
  Status stays strictly binary (СДВИГ/ШУМ) — this is reasoning guidance that should sharpen АРГУМЕНТАЦИЯ, not a new category or field.
- `max_tokens`: 800 → 1000 (headroom for the 3 new short lines).
- Parsing (`analyze_and_save`): read the 3 new keys via `.get(..., "")` same as existing fields, no special-casing needed beyond defaulting to empty string.
- Template: insert a new **Источник:** block into the f-string content, placed in the header metadata block right after `**Промпт версия:**` and before `## What Changes in the Ecosystem`:
  ```
  **Источник:**
    файл: {source_file or "не указан"}
    локация: {source_location or "не указана"}
    цитата: {f'"{source_quote}"' if source_quote else "не указана"}
  ```
  Block is always rendered (never omitted) — placeholders fill in for graceful degradation. Pipeline never skips or fails a СДВИГ write because source is missing.

### 2. Evidence/Source — patterns.py (mechanical aggregation, not new LLM output)

- Sonnet's clustering prompt is unchanged — it still only sees `extract_shift_summary` (300-char summaries) and must not receive raw Источник text, per the existing "base ALL conclusions ONLY on the summaries provided" rule (avoids re-growing the prompt past the 2026-07-11 truncation-incident fix, and avoids hallucination risk).
- New function `extract_source_block(content)` (same file, next to `extract_shift_summary`): parses the **Источник:** block (файл/локация/цитата sub-lines) out of a raw assessment `.md` file's content via simple line-prefix matching (`.strip().startswith("файл:")` etc.), returns a dict with the three values (empty string if block/sub-line absent — assessments written before this change won't have the block at all, must degrade cleanly).
- `read_assessments()`: additionally capture `source` = `extract_source_block(content)` per assessment dict entry. Used only in `create_pattern_file`, never sent to Sonnet.
- `create_pattern_file()`: after building `links_str`, build a new `## Sources` section (English heading, consistent with `## Summary`/`## If Right` etc.) listing each linked assessment's source block, skipping assessments whose source block is entirely empty (pre-migration assessments):
  ```
  ## Sources
  - [[Assessment Name]] — файл: GitHub description, локация: не указана, цитата: "..."
  ```
  Sub-labels (файл/локация/цитата) stay Russian literals, matching the language contract used inside assessments. Section inserted between `## Summary` and `## Why It Matters Now`. If every linked assessment has an empty source block, the whole `## Sources` section is omitted from the pattern file (unlike the assessment-side block, which is always rendered — patterns are Sonnet-authored files where an empty aggregated section is visual noise, not a degraded required field).

### 3. Existing-pattern backlink — patterns.py

**Trigger (the only plausible hook — no such code path exists today):** `create_pattern_file`'s current dedup-skip branch (`patterns.py:432-436`), which today silently discards a cluster when its `assessment_files` overlap ≥50% with `covered_files` (assessments already claimed by an existing pattern). This is exactly the "assessment turned out to belong to an existing pattern" event.

Inside that skip branch, before `return None`:
1. Identify the dominant existing pattern file: for each existing pattern `.md` in `02_Patterns/`, count how many of `cluster["assessment_files"]` appear in its own `[[links]]`. Pick the pattern with the largest intersection count (tie → first match alphabetically by filename). The existing pattern `.md` file itself is **never modified** — this stays purely a read.
2. For each file in `new_files & covered_files` (i.e. the overlapping assessment files that belong to that dominant pattern):
   - Open the assessment file (`os.path.exists` guard first, per Rule 5/10).
   - **Idempotency guard:** if the file already contains a `**Часть паттерна:** [[<dominant pattern name>]]` line, skip — this is a one-time event per (assessment, pattern) pair, not something that re-fires on every future clustering run that happens to re-detect the same overlap.
   - Compute `N` = 1 + (count of `01_Assessments/*.md` files that already contain a `**Часть паттерна:** [[<dominant pattern name>]]` line — mechanical grep, no dependency on the pattern file's own link count, so N correctly increments 1st/2nd/3rd... across separate future runs even though the pattern file is never touched).
   - Append (not overwrite) a new line: `**Часть паттерна:** [[<dominant pattern name>]] (не новый сигнал — {N}-е подтверждение, {today})`.
   - Insertion point: directly after the last existing `**Часть паттерна:**` line in the file if any, else directly after the `**Промпт версия:**` line (end of the header metadata block, before the first `##` heading). Point-edit via string search + insert, never a full-file rewrite.
   - СДВИГ/ШУМ status of the assessment is untouched.
3. New pattern creation (the non-skip path) never gets this backlink — matches "не новый паттерн" in the spec; founding members are only ever listed via the pattern file's own forward `[[links]]`, as today.

## Key decisions & tradeoffs
- **Источник honesty over template completeness**: the format-starter's `README.md L120-L132` example is not achievable today (no file-fetch stage exists) — grounding the field in only what Haiku was actually given (GitHub description / HN title) was chosen over fabricating plausible-looking-but-fake citations. A real README-fetch stage is explicitly deferred as a separate future task, not bundled here.
- **Mechanical aggregation for pattern sources, not a new Sonnet prompt field** — protects the already-fixed truncation risk and respects the "summaries only" clustering rule; costs nothing in prompt tokens.
- **Chain-of-implication as prompt guidance, not a new output field** — protects Haiku's 800(→1000)-token ceiling, the single most truncation-sensitive point in the pipeline; status stays strictly binary.
- **Backlink N computed from assessment-side grep, not from the pattern file's own link count** — the latter would never grow since the pattern file is deliberately never touched, breaking "Nth confirmation" semantics across separate runs.
- **Backlink is a one-time (assessment, pattern) event** (idempotency guard on existing `**Часть паттерна:** [[X]]` presence) — prevents duplicate lines if the same overlap is re-detected on a retried/rerun pipeline within the same clustering cycle.

## Risks / open questions
- None outstanding from the grill. One deferred-not-decided item, explicitly out of scope for this pass: a real README/file-content fetch stage that would make Источник citations for analyze.py fully literal (file + real line numbers) rather than grounded-in-description. Flagged for a future task, not decided here.

## Out of scope (explicitly rejected today, not to be reopened)
- 5-level status model (СДВИГ/ПОДТВЕРЖДЕНИЕ/ЭКСПЕРИМЕНТ/РЕАЛИЗАЦИЯ/ШУМ) — no supporting data found in code; status stays binary.
- Relational DB, Artifact abstraction, traction metrics.
- A separate LLM pre-publish verification call.
- README/file-content fetch stage for real file+line citations (see Risks above).
- Any change to `update_assessments.py` (not named in the task; its own Haiku call and re-evaluation template are untouched).

## Implementation constraints (carried into Act 3 / build)
- `py_compile analyze.py patterns.py` after every change, before push.
- Never overwrite `01_Assessments/*.md` or `02_Patterns/*.md` files wholesale — point-edits only, `os.path.exists` guard before any write to a file that isn't being freshly created.
- Model IDs only from `MODEL_CONFIG` (`99_System/model_config.json`) — no hardcoding.
- `thinking={"type": "disabled"}` for Sonnet calls; no `temperature`/`top_p`/`top_k` anywhere.
- Body/`##`-headings of new/changed sections: English. `**Метка:**`-fields: Russian literals (including the файл/локация/цитата sub-labels, and quoted text kept in its original language, untranslated).
