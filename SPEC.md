# Radar 2.0 — Фаза 3: state-поле, evidence_log-контракт, HITL-подтверждение — Specification

## Overview

Decision B+ (принято 04.08.2026, вне репозитория): марковское допущение
используется только как дешёвая проверка согласованности вывода LLM во
времени — без полноценной HMM (Baum-Welch/Viterbi/эмиссии). Эта фаза
закладывает данные (`state_value`/`state_confidence` во frontmatter,
append-only `evidence_log`), но не считает transition matrix и не строит
Temporal Consistency Validator — это Фаза 3b, отдельная сессия, после
накопления истории.

Roadmap v7 (статус на 04.08.2026) содержит пять открытых пунктов Фазы 3.
Эта спека сознательно покрывает только три:

- **Decision B+**: `state_value`/`state_confidence` во frontmatter.
- **п.2 (частично)**: `append_event()` + контракт записи в `evidence_log`.
  Полный `recheck_lifecycle.py` (ghapi-проверки архивации/лицензии/релизов,
  cron) — вне скоупа.
- **п.5**: human-in-loop подтверждение `CANDIDATE_LOW_CONFIDENCE` через
  новый CI job `confirm_candidate`.

**п.1 (`status: CANDIDATE`, time-based карантин) вынесен из этой спеки
полностью** — решено в интервью 04.08.2026. Причина: п.1 по замыслу
Roadmap требует промоушен-механизма (`CANDIDATE → VALIDATED_SHIFT` через
N дней), а это часть `recheck_lifecycle.py` (п.2), которая в этой сессии
не реализуется. Присвоение `CANDIDATE` без промоушена заморозило бы
такие репозитории — `telegram_post.py`/`patterns.py` читают только
`status == VALIDATED_SHIFT` ([telegram_post.py:46](telegram_post.py#L46),
[patterns.py:281](patterns.py#L281)). `CANDIDATE`/`ARCHIVED_DEAD` остаются
зарезервированными в `VALID_STATUSES`, ни один код-путь их не присваивает
— как и до этой фазы.

## Goals

- [ ] `state_value`/`state_confidence` — новые поля frontmatter, плоские
  (не вложенные), полностью описательные — ни один существующий код-путь
  (`compute_status()`, `patterns.py`, `telegram_post.py`) их не читает.
- [ ] `append_event()` в `vault_write.py` — чистая функция контракта записи
  в `evidence_log`, вызываемая изнутри `write_verdict_entry()`.
- [ ] `confirm_candidate` — новый CI job, web-триггер, человеческое
  подтверждение/отклонение `CANDIDATE_LOW_CONFIDENCE`.
- [ ] `check_frontmatter.py` — валидация `state_value` против
  фиксированного набора значений, когда поле присутствует.

## Tech Stack

Без изменений от предыдущих фаз: Python 3, PyYAML, `anthropic`/`requests`
для LLM-вызовов, `pytest`. Новый CI job переиспользует существующий
паттерн защиты записи в vault (rebase → full-scan гейт → push,
[.gitlab-ci.yml:28-30](.gitlab-ci.yml#L28-L30)).

## Detailed Requirements

### 1. `state_value` / `state_confidence` — новые поля frontmatter

**Ось**: lifecycle/momentum репозитория (растёт/плато/угасает), НЕ
повторение `maturity_score` (снимок зрелости кода на момент оценки).
Промпт/tool schema обязаны явно разводить эти два понятия — иначе модель
просто продублирует одно через другое словами.

**Источник `state_value`**: новое LLM-суждение, часть уже существующего
вызова оценки (не отдельный API-запрос):

- `analyze.py` (первичная оценка) — `CLASSIFICATION_TOOL["input_schema"]`
  ([analyze.py:27-75](analyze.py#L27-L75)) получает новое обязательное
  поле `state_value` с `"enum": ["Prototype", "Growing", "Mature",
  "Maintenance", "Declining", "Archived", "Spam"]` и описанием,
  разводящим его с `maturity_score` (тренд, не снимок). Верификация
  против кода (Rule 28): вызов идёт через `call_haiku_classification()`
  ([analyze.py:298](analyze.py#L298)) с `tool_choice: {"type": "tool",
  "name": "submit_classification"}` — Haiku (не отдельный дорогой вызов,
  согласуется с Decision B+ "не внедрять HMM дорого"), новое обязательное
  поле гарантированно вернётся в `result`. **Явный шаг для реализации**:
  `analyze_and_save()` ([analyze.py:432-481](analyze.py#L432-L481))
  сейчас читает из `result` только именованные поля и вызывает
  `write_verdict_entry(filepath, status, narrative_line,
  extra_frontmatter=extra_frontmatter, body_template=body_template)` без
  нового параметра — при реализации Milestone 3 нужно добавить
  `state_value=result["state_value"]` в этот вызов (Milestone 1
  добавляет параметр в саму функцию, Milestone 3 должен явно соединить
  их на этом call site, иначе `state_value`/`evidence_log` останутся
  пустыми несмотря на новое поле в LLM-схеме).
- `update_assessments.py` (переоценка, Haiku, текстовый промпт) — новая
  строка в требуемом формате ответа: `STATE: Prototype/Growing/Mature/
  Maintenance/Declining/Archived/Spam`, парсится тем же `lines.get()`
  ([update_assessments.py:141-149](update_assessments.py#L141-L149)).
  **Если `STATE` отсутствует или не входит в набор — recheck всё равно
  пишется** (текущее поведение `status`/`verdict_history` не блокируется),
  просто `state_value` не передаётся в `write_verdict_entry()`
  (`state_value=None` → см. §2, `append_event()` не вызывается). Это
  отличается от текущей логики `ОЦЕНКА`/`ИЗМЕНЕНИЕ`
  ([update_assessments.py:151-153](update_assessments.py#L151-L153)), где
  невалидное значение прерывает весь recheck — здесь `STATE` не блокирует
  ничего, кроме самого себя.

**Источник `state_confidence`**: НЕ LLM self-report. Детерминированно,
внутри `write_verdict_entry()`/`append_event()`, из длины `evidence_log`
**до** текущей записи (см. §2):

- `low` — 0 предыдущих `state_transition`-событий в `evidence_log`.
- `high` — 1 и более предыдущих событий.

Два бакета (не три) — промежуточный порог не имеет поведенческого смысла,
пока `state_value`/`state_confidence` чисто описательны.

**Обратная совместимость**: 88 существующих файлов `01_Assessments/` не
трогаются, backfill-скрипт не пишется. `state_value`/`state_confidence`
появятся у файла только при следующем естественном recheck через
`update_assessments.py`. `check_frontmatter.py` не требует их
присутствия (см. §4) — старые файлы без этих полей остаются валидными.

### 2. `append_event()` — контракт записи в `evidence_log`

`vault_write.py`, новая функция:

```python
def append_event(frontmatter, event_type, **fields):
    """Чистая функция - мутирует и возвращает frontmatter, не трогает диск.
    Единственный сейчас определённый event_type - "state_transition"
    (date, event_type, state_value, state_confidence). Схема для будущих
    event_type (license_changed/archived/release, Фаза 3b) не
    зафиксирована - **fields оставляет это открытым без переписывания
    сигнатуры позже."""
    event = {"date": date.today().strftime("%Y-%m-%d"), "event_type": event_type, **fields}
    frontmatter["evidence_log"] = list(frontmatter.get("evidence_log") or []) + [event]
    return frontmatter
```

Никакого `state_value_prev` в записи — Фаза 3b, если понадобится transition
matrix, восстановит переходы последовательным чтением списка (текущая
запись vs предыдущая по индексу), не дублируя значение в каждой записи.

**`write_verdict_entry()` — новый параметр, единственная точка вызова
`append_event()`:**

```python
def write_verdict_entry(filepath, status, narrative_line, extra_frontmatter=None,
                         body_template=None, state_value=None):
    ...
    frontmatter["status"] = status
    ...
    if state_value is not None:
        prior_count = len(frontmatter.get("evidence_log") or [])
        state_confidence = "high" if prior_count >= 1 else "low"
        frontmatter["state_value"] = state_value
        frontmatter["state_confidence"] = state_confidence
        append_event(frontmatter, "state_transition",
                     state_value=state_value, state_confidence=state_confidence)
    write_frontmatter(filepath, frontmatter, body)
    ...
```

Один `write_frontmatter()` в конце — `status`+`verdict_history`+
`state_value`+`state_confidence`+`evidence_log` уходят на диск одним
вызовом, без риска Split-Brain между частичными записями.

**`state_value=None` (по умолчанию)** — `append_event()` не вызывается,
`evidence_log`/`state_value`/`state_confidence` не трогаются. Это путь
для `confirm_candidate.py` (§3, человеческое решение — не LLM-суждение о
state) и для любого будущего вызова `write_verdict_entry()`, не несущего
нового state-суждения.

`CANONICAL_FIELD_ORDER` в `vault_write.py` дополняется: `state_value`,
`state_confidence` — после `novelty_score`, перед `assertion_vector`.

### 3. `confirm_candidate` — CI job, HITL-подтверждение `CANDIDATE_LOW_CONFIDENCE`

Нет bot-сервера/webhook — Telegram-уведомление в `_send_candidate_low_
confidence_dm()` только исходящее. Подтверждение — через GitLab CI
web-триггер с переменными, по аналогии с `$PUBLISH_ONLY`/`$PATTERN_MODE`/
`$GRAPH_ONLY`.

**Новый файл `confirm_candidate.py`:**

```python
import os
import sys
import vault_write

VAULT_PATH = os.environ.get("VAULT_PATH", "01_Assessments")

def main():
    repo = os.environ.get("CONFIRM_REPO", "")
    decision = os.environ.get("CONFIRM_DECISION", "")

    if not repo or "/" in repo or ".." in repo:
        print(f"ОШИБКА: недопустимое значение CONFIRM_REPO: {repo!r}")
        sys.exit(1)
    if decision not in {"approve", "reject"}:
        print(f"ОШИБКА: CONFIRM_DECISION должен быть 'approve' или 'reject', получено: {decision!r}")
        sys.exit(1)

    filepath = os.path.join(VAULT_PATH, repo + ".md")
    if not os.path.exists(filepath):
        print(f"ОШИБКА: файл не найден: {filepath}")
        sys.exit(1)

    frontmatter, _ = vault_write.read_frontmatter(filepath)
    if frontmatter is None or frontmatter.get("status") != "CANDIDATE_LOW_CONFIDENCE":
        print(f"ОШИБКА: {filepath} не в статусе CANDIDATE_LOW_CONFIDENCE (текущий: {frontmatter.get('status') if frontmatter else None!r})")
        sys.exit(1)

    today_status = "VALIDATED_SHIFT" if decision == "approve" else "REJECTED_NOISE"
    narrative_line = f"- {today_status} подтверждено владельцем вручную (HITL, confirm_candidate)" \
        if decision == "approve" else \
        f"- отклонено владельцем вручную (HITL, confirm_candidate)"

    written = vault_write.write_verdict_entry(filepath, today_status, narrative_line)
    if not written:
        print(f"ОШИБКА записи: {filepath}")
        sys.exit(1)

    print(f"{repo}: CANDIDATE_LOW_CONFIDENCE -> {today_status}")

if __name__ == "__main__":
    main()
```

`state_value` не передаётся (человеческое решение — не новое LLM-суждение,
см. §2) — `evidence_log` этим вызовом не пополняется, только
`status`/`verdict_history`.

**Исход approve**: `status → VALIDATED_SHIFT`. Публикация — НЕ мгновенная
внутри этого job'а. `telegram_post.py` уже умеет `find_latest_shift()`
([telegram_post.py:64-78](telegram_post.py#L64-L78)) — берёт самый свежий
неопубликованный `VALIDATED_SHIFT` при каждом плановом прогоне `publish`.
Следующий плановый `publish` подхватит файл автоматически, без
дополнительного кода и без новых секретов в `confirm_candidate` job'е.

**Исход reject**: `status → REJECTED_NOISE` — первое реальное присвоение
этого статуса в коде (сейчас зарезервирован в `VALID_STATUSES`, никем не
присваивается). Файл остаётся в `01_Assessments/`, как архивная запись
отклонённой гипотезы; `patterns.py`/`telegram_post.py` игнорируют его, как
и любой не-`VALIDATED_SHIFT`.

**CI job** (`.gitlab-ci.yml`, следует тому же паттерну защиты, что и
остальные 5 job'ов, пишущих в vault — rebase → full-scan гейт → push):

```yaml
confirm_candidate:
  stage: run
  script:
    - pip install requests pyyaml --quiet
    - git config --global user.email "radar@gitlab.com"
    - git config --global user.name "Radar Bot"
    - git clone --branch vault https://gitlab-ci-token:${CI_JOB_TOKEN}@gitlab.com/lyolich777ka/radar.git vault_repo
    - VAULT_PATH="$(pwd)/vault_repo/01_Assessments" python3 confirm_candidate.py
    - cd vault_repo
    - git remote set-url origin https://lyolich777ka:${GITLAB_PUSH_TOKEN}@gitlab.com/lyolich777ka/radar.git
    - git add -A
    - git commit -m "HITL-подтверждение $CONFIRM_REPO: $CONFIRM_DECISION"
    - git pull --rebase origin vault
    - python3 ../check_frontmatter.py 01_Assessments || exit 1
    - git push origin vault
  rules:
    - if: '$CI_PIPELINE_SOURCE == "web" && $CONFIRM_REPO'
```

`rules:` триггерится по наличию `$CONFIRM_REPO`, не по отдельному
булеву флагу (`$CONFIRM_MODE == "true"`) — значение и так обязательно
для идентификации файла, второй флаг был бы избыточен. Без этого условия
любой `web`-запуск без остальных namespace-переменных запустил бы
`confirm_candidate` с пустым `$CONFIRM_REPO` вместе со всеми остальными
web-job'ами.

Секреты job'а: только `GITLAB_PUSH_TOKEN`/`CI_JOB_TOKEN` (git) —
`TELEGRAM_*`/`ANTHROPIC_API_KEY` не нужны, `write_verdict_entry()` шлёт
Telegram-уведомление только при `status == CANDIDATE_LOW_CONFIDENCE`
([vault_write.py:132-133](vault_write.py#L132-L133)), не при выходе из
этого статуса.

### 4. `check_frontmatter.py` — валидация `state_value`

```python
VALID_STATES = {
    "Prototype", "Growing", "Mature", "Maintenance",
    "Declining", "Archived", "Spam",
}
```

В `validate_file()`: если `state_value` присутствует (не `None`) —
должен входить в `VALID_STATES`, иначе — ошибка, тем же путём, что и
`status` ([check_frontmatter.py:27-31](check_frontmatter.py#L27-L31)).
Если поле отсутствует — не ошибка (обратная совместимость с 88 файлами
без `state_value`, см. §1).

## Non-Functional Requirements

1. `append_event()` не имеет побочных эффектов — чистая функция,
   мутирует и возвращает переданный `frontmatter`, не читает/пишет диск.
2. `state_value`/`state_confidence` не меняют поведение `compute_status()`,
   `patterns.py`, `telegram_post.py` — полностью описательные поля в этой
   фазе, поведенческий эффект только в Фазе 3b.
3. `confirm_candidate.py` не интерполирует пользовательский ввод в
   команды оболочки — `$CONFIRM_REPO`/`$CONFIRM_DECISION` используются
   только как значения Python-переменных после валидации, не как часть
   shell-команды.
4. `python3 -m py_compile confirm_candidate.py` перед коммитом.

## Security Considerations

- **Path traversal в `$CONFIRM_REPO`** — валидируется явно (запрет `/` и
  `..`), несмотря на то, что запускать `confirm_candidate` через GitLab
  Run Pipeline может только участник проекта с правами. Решено не
  полагаться только на права доступа — дешёвая проверка, права могут
  измениться, а невалидированный путь в `os.path.join()` — прямой риск
  чтения/записи вне `01_Assessments/`.
- Без новых секретов сверх уже существующих (`GITLAB_PUSH_TOKEN`,
  `CI_JOB_TOKEN`).
- `check_frontmatter.py` остаётся без побочных эффектов (без изменений от
  предыдущей ревизии) — новая валидация `state_value` того же вида
  (только чтение), не нарушает NFR предыдущей спеки.

## Test Plan

1. **Unit-тесты `append_event()`** — новые, в `test_vault_write.py`
   (или отдельный файл, на усмотрение реализации): чистота функции
   (не трогает файлы), корректная схема `state_transition`-события,
   накопление нескольких событий в `evidence_log`.
2. **Unit-тесты `write_verdict_entry()` с `state_value`** — три случая:
   `state_value=None` (текущее поведение не меняется, `evidence_log`
   нетронут), новый файл с `state_value` (confidence=`low`, 0 предыдущих
   событий), существующий файл с уже одним событием в `evidence_log`
   (confidence=`high`).
3. **Unit-тесты `confirm_candidate.py`** (`test_confirm_candidate.py`,
   локально, без реального web-прогона — решено в интервью 04.08.2026):
   path traversal (`/`, `..`) отклоняется, невалидный `CONFIRM_DECISION`
   отклоняется, отсутствующий файл — ошибка, файл с status не
   `CANDIDATE_LOW_CONFIDENCE` — ошибка, happy-path approve → `status ==
   VALIDATED_SHIFT`, happy-path reject → `status == REJECTED_NOISE`.
   Реальный web-триггер `confirm_candidate` в GitLab CI — решение
   владельца после мержа в master, вне этой сессии (мутирует реальные
   оценки, риск случайной публикации в канал при approve).
4. **`check_frontmatter.py` — новые кейсы в `test_check_frontmatter.py`**:
   `state_value` из `VALID_STATES` — валиден; произвольная строка —
   невалиден; отсутствие поля — валиден (обратная совместимость).
5. **Реальный LLM-вызов `analyze.py` на 1-2 известных репозиториях**
   (Rule 28, дополнение — тестирование реальным вызовом на реальных
   данных, а не только схема-валидацией): один явно зрелый/stable
   репозиторий, один явно свежий prototype — подтвердить, что
   `state_value` действительно различается между ними и не дублирует
   `maturity_score` словами. Выбор конкретных репозиториев — на этапе
   реализации.

   **Выполнено 04.08.2026** (напрямую через
   `fetch_repo_signal()`+`build_prompt()`+`call_haiku_classification()`,
   без записи в vault и без Telegram — скрипт вне репозитория). Три
   репозитория, включая decoupling-тест (два репозитория с ОДИНАКОВЫМ
   `maturity_score`, чтобы исключить гипотезу "state_value просто
   пересказывает maturity_score словами"):

   | Репозиторий | maturity_score | state_value | Комментарий |
   |---|---|---|---|
   | случайный репозиторий с GitHub Search, `created > 2026-07-01`, 0 звёзд (свежий prototype) | 1-2 | `Prototype` | ожидаемо |
   | `facebook/react` (эталон зрелого, активно развивающегося) | 5 | `Mature` | |
   | `angular/angular.js` (AngularJS 1.x, EOL/заменён Angular 2+, но полноценный production-grade код) | 5 | `Maintenance` | **decoupling подтверждён**: тот же `maturity_score`, что у React, но другой `state_value` — модель различает "зрелый и растущий" от "зрелый, но неактивный", а не дублирует одно через другое |

   Вывод: `state_value` — не переформулировка `maturity_score`, ось
   реально независима на практике, не только по замыслу схемы.
6. `python3 -m py_compile confirm_candidate.py` и затронутых файлов
   (`vault_write.py`, `analyze.py`, `update_assessments.py`,
   `check_frontmatter.py`).

## Milestones

1. [ ] `append_event()` + `state_value`-параметр `write_verdict_entry()`
   в `vault_write.py`, `CANONICAL_FIELD_ORDER` обновлён.
2. [ ] Unit-тесты `append_event()`/`write_verdict_entry()` (Test Plan §1-2).
3. [ ] `state_value` в `CLASSIFICATION_TOOL` (`analyze.py`) — enum +
   описание, разводящее с `maturity_score`.
4. [ ] `STATE:` в текстовом промпте `update_assessments.py`, парсинг,
   мягкая деградация при невалидном/отсутствующем значении.
5. [ ] `check_frontmatter.py` — `VALID_STATES` + валидация (Test Plan §4).
6. [ ] `confirm_candidate.py` + unit-тесты (Test Plan §3).
7. [ ] `confirm_candidate` job в `.gitlab-ci.yml`.
8. [x] Реальный LLM-вызов на 1-2 известных репозиториях, ручная проверка
   `state_value` vs `maturity_score` (Test Plan §5) — выполнено
   04.08.2026, decoupling подтверждён (`react` vs `angular.js`, см.
   таблицу в Test Plan §5).
9. [ ] Полный diff, явное подтверждение владельца перед commit/push
   (CONSTITUTION, без исключений).

## Open Questions / Decisions Needed

Все развилки этого интервью закрыты (04.08.2026):
- п.1 (`CANDIDATE` time-based карантин) — вынесен из скоупа полностью,
  отдельная сессия после того, как `recheck_lifecycle.py` (п.2, остаток)
  реализован — без промоушен-механизма присвоение `CANDIDATE` заморозило
  бы репозитории (см. Overview).
- `state`/`status` — не пересекаются: `status` управляет публикацией и
  квалификацией, `state_value`/`state_confidence` полностью описательны
  в этой фазе.
- `state_value` vs `maturity_score` — разные оси (тренд vs снимок),
  требует явного различения в промпте/schema, не просто новое поле рядом
  со старым.
- Реальный web-прогон `confirm_candidate` в CI — отложен на решение
  владельца после мержа (мутирует реальные данные, риск публикации).
