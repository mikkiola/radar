# Radar 2.0 — Фаза 3, п.2: `recheck_lifecycle.py` — ежемесячная переоценка `VALIDATED_SHIFT` — Specification

## Overview

Roadmap v4/v6 п.2, отдельная сессия — продолжение п.1 (`status: CANDIDATE`,
time-based карантин, реализовано в предыдущей сессии, коммиты `c15ebbc`/
`d047284`). Та спека прямо указывала на эту задачу как на будущую
отдельную сессию, переиспользующую `check_repo_alive()`.

**Задача другая, чем у п.1.** П.1 решает "дать время новой непроверенной
гипотезе, прежде чем зафиксировать её как `VALIDATED_SHIFT`". Эта сессия
решает другую задачу: уже опубликованный, подтверждённый `VALIDATED_SHIFT`
может устареть — репозиторий архивируется, меняет лицензию, замирает,
перестаёт релизиться, ломает CI. `recheck_lifecycle.py` — ежемесячный CI
job, перепроверяющий факты о репозитории для уже существующих
`VALIDATED_SHIFT`-записей, не переоценивающий сам вердикт заново.

**Единственный сигнал, меняющий `status`**: `repo.archived` → напрямую
`ARCHIVED_DEAD`, без карантина (в отличие от п.1 — там карантин нужен
именно потому, что вердикт ещё не подтверждён; здесь факт архивации
окончателен для уже подтверждённого вердикта, откладывать нечего).

**Все остальные сигналы** (смена лицензии, "заморожен", видимость
репозитория, остановка релизов, поломка CI) — **evidence-only**: пополняют
`evidence_log`, не трогают `status`. Ни один из них не есть "репозиторий
мёртв", а сигнал риска для владельца, читающего файл в Obsidian —
композитные правила вывода (например "license BSL + visibility_lost +
frozen вместе → вероятный rugpull") сознательно не вводятся в этой сессии
(Decision B+, нет наблюдаемого случая, где такое правило реально
понадобилось) — `evidence_log` остаётся строго фактическим (измерение, не
вывод), тот же принцип, что уже применён в `check_repo_alive()` (три
исхода `True`/`False`/`None`, не готовый вердикт).

**`evidence_log` — event log, не measurement log.** Единственный до сих пор
существующий `event_type` (`"state_transition"`) — семантически событие
(LLM сменила суждение), не снимок состояния. Три из пяти новых сигналов —
условия, которые могут длиться месяцами и сниматься обратно (заморожен,
видимость, релизы остановлены, CI сломан) — записываются как **пары
переходов** (`X_entered`/`X_exited`), не как повторяющийся снимок каждый
месяц. Без этого `evidence_log` растёт на дублирующую запись каждый
прогон для любого долгоживущего `Maintenance`-репозитория — не шум, а
неверная модель данных для уже существующего событийного поля.

Бонус, прямо связанный с уже принятым в проекте решением: Фаза 3b
(transition matrix, отложена в BACKLOG до накопления истории `state_value`
через реальные recheck-циклы) получает готовую структуру данных истории
переходов бесплатно.

## Goals

- [x] `analyze.py`: `fetch_repo_lifecycle_signal(owner, repo)` — новая
  функция, один `gh_api.repos.get()`, возвращает
  `archived`/`license_spdx_id`/`pushed_at`/`private` или `None`.
  `check_repo_alive()` не меняется, не переиспользуется — отдельный вызов
  (см. §3).
- [x] `analyze.py`: `fetch_repo_signal()` — расширяется, `license_spdx_id`
  читается из уже существующего `repos.get()`-вызова (для
  `root_commit_sha`), без нового API-вызова на этапе первичной оценки.
- [x] `analyze.py`: `analyze_and_save()` — `extra_frontmatter` получает
  `license_spdx_id`/`license_baseline_origin: "initial"`.
- [x] `vault_write.py`: `append_evidence_only(filepath, events,
  extra_fields=None)` — evidence-only запись, не трогает
  `status`/`verdict_history`/тело файла. `write_verdict_entry()` не
  меняется.
- [x] `vault_write.py`: `CANONICAL_FIELD_ORDER` — добавить
  `license_spdx_id`/`license_baseline_origin`.
- [x] `recheck_lifecycle.py` — новый файл, полный флоу.
- [ ] `.gitlab-ci.yml`: новый job `recheck_lifecycle` + правки `rules` в
  `radar`/`promote_candidates` (исключение нового `$LIFECYCLE_ONLY`).
  `lint_vault` — без изменений (см. §11).
- [x] Unit-тесты (моки) + 1 реальный API-вызов на структуру ответа
  (`fetch_repo_lifecycle_signal` + `list_releases` +
  `list_workflow_runs_for_repo`) — 46 новых/расширенных тестов, полный
  прогон проекта 99/99. Реальный вызов на `facebook/react` подтвердил §11
  без расхождений (см. Test Plan §6).
- [ ] Полный diff, явное подтверждение владельца перед commit/push
  (CONSTITUTION, без исключений).
- [ ] Реальный приёмочный прогон в CI (Правило 31) — обязателен, т.к.
  меняется `.gitlab-ci.yml`, не только чтение YAML.

## Tech Stack

Без изменений: Python 3, `ghapi`, `pyyaml`, `pytest`. `license-expression`
(aboutcode-org) **НЕ подключается** в этой сессии — см. §4, явное решение,
не пропуск.

## Detailed Requirements

### 1. Периметр: какие файлы перепроверяются

Только `status == "VALIDATED_SHIFT"`. `CANDIDATE` уже обрабатывается
`promote_candidates.py` — дублировать логику `check_repo_alive()` в двух
job'ах не нужно. `REJECTED_NOISE`/`ARCHIVED_DEAD` — терминальные статусы,
без наблюдаемого триггера на пересмотр (полная FSM с un-archival отклонена
по тому же Decision B+, что уже применялся в п.1 к `check_repo_alive()`).

### 2. Архивация — единственный status-меняющий сигнал

```python
if signal["archived"]:
    narrative_line = f"- {today} - ARCHIVED_DEAD: репозиторий архивирован (recheck_lifecycle)"
    written = vault_write.write_verdict_entry(filepath, "ARCHIVED_DEAD", narrative_line)
    ...
    return  # остальные сигналы этого файла в этом прогоне не проверяются
```

`state_value` не передаётся (`None`) — детерминированный факт GitHub API,
не новое LLM-суждение, тот же принцип, что `promote_candidates.py` и
`confirm_candidate.py`. `evidence_log` этим вызовом не пополняется
(`write_verdict_entry()` пишет `state_transition` только при переданном
`state_value`).

### 3. `fetch_repo_lifecycle_signal()` — `analyze.py`

```python
def fetch_repo_lifecycle_signal(owner, repo):
    """Один gh_api.repos.get() вызов - archived/license_spdx_id/pushed_at/private
    разом, для recheck_lifecycle.py (ежемесячная переоценка VALIDATED_SHIFT).
    Не переиспользует check_repo_alive() и не изменяет её - разные вызывающие
    (promote_candidates.py против recheck_lifecycle.py), разный набор нужных
    полей; дублирование одного repos.get() дешевле риска трогать закрытую,
    протестированную (67/67) и уже работающую в проде часть Фазы 3 п.1
    (Decision B+, тот же принцип применён в §9 к read_repo_url()).
    None - не удалось получить данные (сетевая ошибка/rate limit/404) - НЕ
    факт о состоянии репозитория, вызывающий код обязан пропустить файл в
    этом прогоне целиком."""
    try:
        info = gh_api.repos.get(owner, repo)
        license_info = info.get("license") or {}
        return {
            "archived": info.get("archived", False),
            "license_spdx_id": license_info.get("spdx_id"),
            "pushed_at": info.get("pushed_at"),
            "private": info.get("private", False),
        }
    except Exception as e:
        print(f"   не удалось получить lifecycle-данные о репозитории {owner}/{repo}: {e}")
        return None
```

Рядом с `check_repo_alive()` (аналогичное размещение решению для неё в п.1
— реиспользует модульный `gh_api`, не создаёт второй `GhApi`-инстанс).

### 4. `license_spdx_id` — baseline, захватывается в `analyze.py`

`fetch_repo_signal()` расширяется: тот же `try`-блок, что уже делает
`meta = gh_api.repos.get(owner, repo)` для `root_commit_sha`
([analyze.py:150-156](analyze.py#L150-L156)), дополнительно читает
лицензию — **ноль новых API-вызовов**:

```python
    try:
        meta = gh_api.repos.get(owner, repo)
        default_branch = meta.get("default_branch") or "main"
        branch_info = gh_api.repos.get_branch(owner, repo, default_branch)
        signal["root_commit_sha"] = branch_info["commit"]["sha"]
        signal["license_spdx_id"] = (meta.get("license") or {}).get("spdx_id")
    except Exception as e:
        print(f"   HEAD SHA недоступен для {owner}/{repo}: {e}")
```

(`signal["license_spdx_id"] = None` добавляется в стартовый словарь
`signal` в начале `fetch_repo_signal()`, рядом с `"root_commit_sha": None`.)

`analyze_and_save()` — `extra_frontmatter`:

```python
        extra_frontmatter = {
            "maturity_score": maturity_score,
            "novelty_score": novelty_score,
            "assertion_vector": result.get("assertion_vector"),
            "evidence_log": [],
            "root_commit_sha": signal["root_commit_sha"],
            "license_spdx_id": signal["license_spdx_id"],
            "license_baseline_origin": "initial",
        }
```

**`license_baseline_origin`** — явное поле происхождения baseline, не
только текстовая пометка в этом документе. `root_commit_sha` уже `null`
для 88 backfilled-файлов — молчаливое ограничение, задокументированное
только текстом, не в самих данных. Не повторять этот паттерн для
`license_spdx_id`: `"license: MIT"` через полгода без пометки происхождения
читается как "лицензия была MIT с самого начала" — ложное ощущение полноты
данных. Два значения:
- `"initial"` — записано при первичной оценке (эта и все последующие
  сессии).
- `"migration"` — записано `recheck_lifecycle.py` задним числом при первом
  прогоне для файла без `license_spdx_id` в frontmatter (см. §7).

**Известное принятое ограничение** (зафиксировать явно, не как забытую
деталь): `recheck_lifecycle.py` не может обнаружить смену лицензии,
произошедшую ДО первого recheck-прогона файла — baseline для
`"migration"`-файлов ставится по текущему состоянию на момент миграции, не
по историческому состоянию на момент первой оценки. Полноценная
историческая реконструкция (проверка истории `LICENSE` через git/API)
отклонена — механизм ради разовой исторической дыры, которая не
повторится, нарушает Decision B+ и Правило 22 (build-vs-reuse).

### 5. `license-expression` — явно НЕ подключается в этой сессии

Контекст задачи изначально предполагал `license-expression` (aboutcode-org)
для сверки SPDX. Верификация против кода (Правило 28) показала: GitHub API
в `repo.license` возвращает **один уже распознанный `spdx_id`**
(например `"MIT"`), не составное SPDX-выражение вроде `"MIT OR Apache-2.0"`
— для сравнения двух готовых строк парсер выражений не нужен. Сравнение —
`current_spdx_id != baseline_spdx_id`, простое равенство строк, без новой
pip-зависимости.

`license-expression` остаётся правильным выбором на будущее при реальной
потребности (например прямое чтение `LICENSE`-файла репозитория вместо
API-поля, где составные выражения действительно могут встретиться) — не
отклонено навсегда, просто не нужно сейчас (Decision B+).

### 6. `append_evidence_only()` — `vault_write.py`

```python
def append_evidence_only(filepath, events, extra_fields=None):
    """Пишет evidence_log-события БЕЗ изменения status/verdict_history/тела
    файла - для recheck_lifecycle.py, где сигнал (license_changed/
    frozen_entered/...) не является новым вердиктом, файл остаётся в текущем
    status. Отдельно от write_verdict_entry(): та функция жёстко связывает
    evidence-запись с verdict_history-записью (верно для реальных вердиктов -
    analyze.py/update_assessments.py/promote_candidates.py/confirm_candidate.py,
    где каждый вызов и есть новый вердикт); здесь каждый вызов - НЕ вердикт.
    Расширять write_verdict_entry() условностью ("писать verdict_history,
    только если status реально изменился") означало бы вводить скрытую
    ветвящуюся логику в функцию с 4 существующими, сегодня работающими
    вызывающими - риск регрессии не оправдан отсутствием одной обёртки.
    Не вводит второй путь ИЗМЕНЕНИЯ status (extra_fields не предназначен для
    status - единственный вызывающий, recheck_lifecycle.py, туда status не
    передаёт) - второй путь ЗАПИСИ evidence_log при неизменном status.

    events - список dict-ов {"event_type": ..., **fields}, каждый передаётся
    в append_event() как есть. extra_fields - опциональный dict полей
    frontmatter для точечного обновления в той же записи на диск (например
    license_spdx_id при обновлении baseline) - один дисковый write на файл
    за прогон, не два независимых.

    Возвращает True при успешной записи, False при ошибке (файл без
    frontmatter) - тот же контракт, что write_verdict_entry()."""
    frontmatter, body = read_frontmatter(filepath)
    if frontmatter is None:
        print(f"[vault_write] ОШИБКА: {filepath} без frontmatter, append_evidence_only пропущен")
        return False

    if extra_fields:
        frontmatter.update(extra_fields)

    for event in events:
        fields = {k: v for k, v in event.items() if k != "event_type"}
        append_event(frontmatter, event["event_type"], **fields)

    write_frontmatter(filepath, frontmatter, body)
    return True
```

**Важное уточнение, чтобы не читалось как пересмотр более раннего решения
этой же сессии**: ранее в интервью был отклонён похожий по названию
вариант ("отдельная функция для evidence-only записи") в пользу расширения
`write_verdict_entry()` опциональным списком `events`. Это не противоречие
— тот вопрос был "как передать `events` в `append_event()` без второго
пути записи `status`" (там правильно выбрана единая точка входа для
status-меняющих вызовов). Здесь вопрос другой — "как не писать безусловный
`verdict_history`/`narrative_line`, когда `status` вообще не меняется".
`append_evidence_only()` не вводит второй путь изменения `status` — она
путь записи `evidence_log` **при неизменном** `status`. Внутри использует
тот же `append_event()`, тот же файл, тот же `frontmatter` — не
альтернативная реализация, обёртка с более узкой ответственностью.

`CANONICAL_FIELD_ORDER` в `vault_write.py` получает `license_spdx_id`,
`license_baseline_origin` (после `root_commit_sha`, до `verdict_history`).

### 7. `detect_transition()` — определение перехода состояния

```python
def detect_transition(evidence_log, entered_type, exited_type, condition_now):
    """Определяет, является ли condition_now переходом относительно
    последнего события этой пары в evidence_log. currently_in = последнее
    событие пары было entered_type (пары ещё не было -> currently_in=False,
    первое истинное наблюдение = вход). Возвращает entered_type/exited_type
    для append, или None, если состояние не изменилось с прошлого прогона -
    не порождает новую запись при неизменном факте (evidence_log - event log,
    не measurement log, см. Overview)."""
    relevant = [e for e in (evidence_log or []) if e.get("event_type") in (entered_type, exited_type)]
    currently_in = bool(relevant) and relevant[-1]["event_type"] == entered_type

    if condition_now and not currently_in:
        return entered_type
    if not condition_now and currently_in:
        return exited_type
    return None
```

Сравнение с предыдущим состоянием — часть ОПРЕДЕЛЕНИЯ события (детектор
перехода), не интерпретирующая логика поверх факта. `append_event()` не
меняется как функция, остаётся чистым append — меняется только то, что ей
передают: не сырое наблюдение "frozen=True", а уже детектированное событие
перехода. Решение "входим/выходим" принимается ДО вызова `append_event()`,
вызывающим кодом (`recheck_lifecycle.py`), не внутри неё.

### 8. Пороги и сигналы (пять типов, все кроме архивации — evidence-only)

| Сигнал | Порог | Пара событий | Условие оценки |
|---|---|---|---|
| `archived` | `repo.archived == True` | — (меняет `status`, см. §2) | всегда |
| license | `current_spdx_id != baseline` | `license_changed` (единичное, не пара) | baseline существует (см. §4/§7-migration) |
| frozen | `pushed_at` старше 6 месяцев | `frozen_entered`/`frozen_exited` | всегда |
| видимость | `repo.private == True` | `visibility_lost`/`visibility_restored` | всегда |
| релизы | последний релиз старше 12 мес. | `releases_stopped_entered`/`releases_resumed` | только если было ≥2 релизов когда-либо |
| CI | последний workflow run `conclusion != "success"` | `ci_broken`/`ci_restored` | только если есть хотя бы 1 workflow run |

**Видимость (`visibility_lost`/`visibility_restored`)** — нейтральное имя,
не `went_private`/`going_private` (эти названия сами по себе уже
интерпретация, "стал скрытным" читается как плохой знак). `private !=
rugpull`: легитимных причин уйти в приватность много и они частые —
коммерциализация, security audit перед раскрытием уязвимости, перенос в
закрытый monorepo, временная приватизация из-за утечки ключей, поглощение
компанией. В отличие от смены лицензии MIT→BSL (почти всегда означает одно
и то же), `public→private` говорит только "публичное наблюдение
прекращено" — не более. Факт записывается нейтрально, композитная
интерпретация (см. Overview) — не в этой сессии.

**Релизы без истории (0-1 когда-либо)** — сигнал не оценивается вообще, ни
разу: многие проекты в принципе не используют GitHub Releases, это не
признак упадка.

**CI без workflows вообще** (`list_workflow_runs_for_repo` возвращает
пустой список) — отсутствие данных, не `ci_broken`. Многие проекты либо не
используют GitHub Actions, либо CI ещё нет — тот же принцип Graceful
Degradation, что уже применён в `check_repo_alive()`.

`license_changed` — единичное событие, не пара (у лицензии нет
"вошли"/"вышли" — это смена значения). При обнаружении: событие
`license_changed` с `old`/`new`, baseline (`license_spdx_id` в
frontmatter) обновляется на новое значение той же записью через
`extra_fields`, чтобы то же значение не переспрашивалось как "изменение"
на следующий месяц.

### 9. Обработка ошибок API — гранулярность по сигналу, не по файлу

`fetch_repo_lifecycle_signal()` — один вызов, покрывает `archived`/
`license_spdx_id`/`pushed_at`/`private`. Ошибка → весь файл пропускается в
этом прогоне (эти данные нужны для гейта архивации и трёх из пяти
сигналов, без них нечего оценивать).

`list_releases()`/`list_workflow_runs_for_repo()` — отдельные `try/except`
вокруг каждого. Ошибка одного из них → **только этот конкретный сигнал**
не оценивается в этом прогоне, остальные (license/frozen/visibility и
второй из пары releases/CI) обрабатываются нормально — частичная
деградация на уровне сигнала, не всего файла.

### 10. `read_repo_url()` — дублирование, не рефакторинг

`recheck_lifecycle.py` копирует ту же 4-строчную функцию, что уже есть в
`promote_candidates.py`, вместо выноса в `vault_write.py`. Rule of three —
валидный принцип в общем случае, не применяется здесь: `promote_candidates.py`
не произвольный существующий код — это закрытая, протестированная (67/67),
реально прогнанная на `facebook/react`/`jquery/jquery-mobile` часть Фазы 3
п.1, сегодня утром закоммиченная (`c15ebbc`) и уже работающая на
существующем daily-schedule. Трогать её сейчас ради рефакторинга ДРУГОЙ
задачи вводит риск регрессии в уже сданном, не связанном с этим интервью
коде — даже декларативно поведение-нейтральная правка не подтверждена
повторным прогоном тестов конкретно для `promote_candidates.py`.

Асимметрия рисков (Правило 18): цена дублирования — 4 строки чистой
функции парсинга, не относящейся к классу часто меняющегося кода. Цена
рефакторинга — трогать уже закрытую часть Фазы 3 ради экономии этих 4
строк. Не отказ от rule of three навсегда — при третьем появлении ПОСЛЕ
этой сессии, или если `promote_candidates.py` в любом случае потребуется
трогать по другой причине, вынести в `vault_write.py` заодно.

### 11. `recheck_lifecycle.py` — полный флоу

```python
import os
from datetime import date, datetime

import vault_write
from analyze import parse_github_owner_repo, fetch_repo_lifecycle_signal, gh_api

VAULT_PATH = os.environ.get("VAULT_PATH", "01_Assessments")
FROZEN_MONTHS = 6
RELEASES_STOPPED_MONTHS = 12


def find_validated_shift_files():
    files = []
    if not os.path.exists(VAULT_PATH):
        return files
    for name in sorted(os.listdir(VAULT_PATH)):
        if not name.endswith(".md"):
            continue
        filepath = os.path.join(VAULT_PATH, name)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        if frontmatter and frontmatter.get("status") == "VALIDATED_SHIFT":
            files.append(filepath)
    return files


def read_repo_url(body):
    for line in body.splitlines():
        if line.startswith("**Репозиторий:**"):
            return line.split("**Репозиторий:**", 1)[1].strip()
    return None


def detect_transition(evidence_log, entered_type, exited_type, condition_now):
    relevant = [e for e in (evidence_log or []) if e.get("event_type") in (entered_type, exited_type)]
    currently_in = bool(relevant) and relevant[-1]["event_type"] == entered_type
    if condition_now and not currently_in:
        return entered_type
    if not condition_now and currently_in:
        return exited_type
    return None


def months_since(iso_timestamp):
    dt = datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    return (datetime.utcnow() - dt).days / 30


def check_releases_stopped(owner, repo, evidence_log):
    try:
        releases = gh_api.repos.list_releases(owner, repo)
    except Exception as e:
        print(f"   релизы недоступны для {owner}/{repo}: {e}")
        return None
    if len(releases) < 2:
        return None
    dates = sorted((r["published_at"] for r in releases if r.get("published_at")), reverse=True)
    if not dates:
        return None
    condition_now = months_since(dates[0]) > RELEASES_STOPPED_MONTHS
    return detect_transition(evidence_log, "releases_stopped_entered", "releases_resumed", condition_now)


def check_ci_broken(owner, repo, evidence_log):
    try:
        runs = gh_api.actions.list_workflow_runs_for_repo(owner, repo, per_page=1)
        run_list = runs.get("workflow_runs", [])
    except Exception as e:
        print(f"   CI-статус недоступен для {owner}/{repo}: {e}")
        return None
    if not run_list:
        return None
    condition_now = run_list[0].get("conclusion") != "success"
    return detect_transition(evidence_log, "ci_broken", "ci_restored", condition_now)


def process_file(filepath):
    frontmatter, body = vault_write.read_frontmatter(filepath)
    if frontmatter is None:
        print(f"   ОШИБКА: {filepath} без frontmatter, пропускаю")
        return

    url = read_repo_url(body)
    owner, repo = parse_github_owner_repo(url)
    if not owner or not repo:
        print(f"   ОШИБКА: не удалось разобрать owner/repo из {url!r} в {filepath}")
        return

    signal = fetch_repo_lifecycle_signal(owner, repo)
    if signal is None:
        print(f"   {filepath}: lifecycle-данные недоступны в этом прогоне, пропускаю")
        return

    today = date.today().strftime("%Y-%m-%d")

    if signal["archived"]:
        narrative_line = f"- {today} - ARCHIVED_DEAD: репозиторий архивирован (recheck_lifecycle)"
        written = vault_write.write_verdict_entry(filepath, "ARCHIVED_DEAD", narrative_line)
        print(f"   {filepath}: VALIDATED_SHIFT -> ARCHIVED_DEAD" if written else f"   ОШИБКА записи: {filepath}")
        return

    evidence_log = frontmatter.get("evidence_log") or []
    events = []
    extra_fields = None

    baseline_license = frontmatter.get("license_spdx_id")
    current_license = signal["license_spdx_id"]
    if baseline_license is None:
        extra_fields = {"license_spdx_id": current_license, "license_baseline_origin": "migration"}
    elif current_license != baseline_license:
        events.append({"event_type": "license_changed", "old": baseline_license, "new": current_license})
        extra_fields = {"license_spdx_id": current_license}

    if signal["pushed_at"] is not None:
        frozen_now = months_since(signal["pushed_at"]) > FROZEN_MONTHS
        frozen_event = detect_transition(evidence_log, "frozen_entered", "frozen_exited", frozen_now)
        if frozen_event:
            events.append({"event_type": frozen_event})

    visibility_event = detect_transition(evidence_log, "visibility_lost", "visibility_restored", signal["private"])
    if visibility_event:
        events.append({"event_type": visibility_event})

    releases_event = check_releases_stopped(owner, repo, evidence_log)
    if releases_event:
        events.append({"event_type": releases_event})

    ci_event = check_ci_broken(owner, repo, evidence_log)
    if ci_event:
        events.append({"event_type": ci_event})

    if events or extra_fields:
        written = vault_write.append_evidence_only(filepath, events, extra_fields=extra_fields)
        suffix = ", baseline обновлён" if extra_fields else ""
        print(f"   {filepath}: {len(events)} evidence-событий{suffix}" if written else f"   ОШИБКА записи evidence: {filepath}")


def main():
    files = find_validated_shift_files()
    print(f"Найдено VALIDATED_SHIFT-файлов: {len(files)}")
    for filepath in files:
        try:
            process_file(filepath)
        except Exception as e:
            print(f"   ОШИБКА при обработке {filepath}: {e}")
    print("Готово.")


if __name__ == "__main__":
    main()
```

`process_file()` вызывается под `try/except` в `main()` — тот же паттерн,
что `promote_candidates.py`: один повреждённый файл не прерывает батч.

**Подтверждено реальным вызовом на этапе реализации** (05.08.2026, см. Test
Plan §6): `gh_api.repos.list_releases(owner, repo)` возвращает
`fastcore.foundation.L` (ведёт себя как список — `len()`/индексация
работают), элементы — `AttrDict` с рабочим `.get("published_at")`.
`gh_api.actions.list_workflow_runs_for_repo(owner, repo, per_page=1)`
возвращает `AttrDict` с ключом `workflow_runs` (тоже `L` из `AttrDict`),
`.get("conclusion")` работает. `months_since()` формат
`%Y-%m-%dT%H:%M:%SZ` подтверждён реальным `pushed_at` от GitHub API
(`facebook/react`). Расхождений с §11 не найдено, правок в код не
потребовалось — при первоначальном написании этого раздела в интервью
предполагалось, что расхождение вероятно; по факту его не оказалось.

### 12. `.gitlab-ci.yml`

Новый job:

```yaml
recheck_lifecycle:
  stage: run
  script:
    - pip install requests pyyaml ghapi --quiet
    - git config --global user.email "radar@gitlab.com"
    - git config --global user.name "Radar Bot"
    - git clone --branch vault https://gitlab-ci-token:${CI_JOB_TOKEN}@gitlab.com/lyolich777ka/radar.git vault_repo
    - VAULT_PATH="$(pwd)/vault_repo/01_Assessments" python3 recheck_lifecycle.py
    - cd vault_repo
    - git remote set-url origin https://lyolich777ka:${GITLAB_PUSH_TOKEN}@gitlab.com/lyolich777ka/radar.git
    - git add -A
    - |
      if git diff --staged --quiet; then
        echo "Нет изменений lifecycle-сигналов"
      else
        git commit -m "Переоценка lifecycle: recheck_lifecycle $(date '+%Y-%m-%d')"
        git pull --rebase origin vault
        python3 ../check_frontmatter.py 01_Assessments || exit 1
        git push origin vault
      fi
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule" && $LIFECYCLE_ONLY == "true"'
    - if: '$CI_PIPELINE_SOURCE == "web" && $LIFECYCLE_ONLY == "true"'
```

**Первый ежемесячный GitLab Schedule в проекте** — новый Schedule (cron,
например `"0 0 1 * *"`, настраивается в GitLab UI, не в этом файле) с
переменной `$LIFECYCLE_ONLY == "true"`. Паттерн уже трижды использован в
проекте (`$PUBLISH_ONLY`/`$PROMOTE_ONLY`/`$CONFIRM_REPO`) —
предсказуемость важнее минимизации числа переменных, особенно в
соло-режиме, где владелец должен быстро узнавать знакомую схему конфига
через месяцы.

**Обязательное исключение в существующих job'ах** — без него они повторно
сработают на новом ежемесячном триггере наравне с `recheck_lifecycle`. Тот
же класс ошибки, что уже был найден и откачен (`revert 306f264`,
`.gitlab-ci.yml` этим же утром): постоянный web/schedule-триггер без
namespace-переменной расширяет поверхность срабатывания непредсказуемо.

`radar` — было:
```yaml
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule" && $PUBLISH_ONLY != "true" && $PATTERN_MODE != "weekly"'
    - if: '$CI_PIPELINE_SOURCE == "web" && $PUBLISH_ONLY != "true" && $PATTERN_MODE != "weekly"'
```
стало:
```yaml
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule" && $PUBLISH_ONLY != "true" && $PATTERN_MODE != "weekly" && $LIFECYCLE_ONLY != "true"'
    - if: '$CI_PIPELINE_SOURCE == "web" && $PUBLISH_ONLY != "true" && $PATTERN_MODE != "weekly" && $LIFECYCLE_ONLY != "true"'
```

`promote_candidates` — было:
```yaml
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
    - if: '$CI_PIPELINE_SOURCE == "web" && $PROMOTE_ONLY == "true"'
```
стало:
```yaml
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule" && $LIFECYCLE_ONLY != "true"'
    - if: '$CI_PIPELINE_SOURCE == "web" && $PROMOTE_ONLY == "true"'
```
(web-строка уже узкая — `$PROMOTE_ONLY == "true"` не совпадёт с
`$LIFECYCLE_ONLY == "true"`, изменений не требует.)

`lint_vault` — **без изменений**, решено в интервью после верификации
реального `rules:`-блока (Правило 28):
```yaml
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
    - if: '$CI_PIPELINE_SOURCE == "web"'
```
Уже сейчас безусловно срабатывает на ЛЮБОМ web/schedule-триггере, включая
существующие `$PROMOTE_ONLY`/`$CONFIRM_REPO`/`$PUBLISH_ONLY` — новый
`$LIFECYCLE_ONLY` не вносит новой асимметрии, просто ещё один случай того
же самого. `lint_vault` по роли — периодический детективный скан
инварианта frontmatter, намеренно не привязан к конкретному триггеру.

`publish`/`analysts`/`check_models`/`patterns`/`pages` — без изменений,
уже гейтятся другими именованными переменными
(`$PUBLISH_ONLY`/`$PATTERN_MODE`/`$GRAPH_ONLY`), которые не совпадут с
`$LIFECYCLE_ONLY == "true"`.

**Перед коммитом** — показать финальный список `rules:` для ВСЕХ
затронутых job'ов (не только `recheck_lifecycle`) в рамках полного
diff-review (Milestone, см. ниже) — отдельный шаг от построчной сверки
этого SPEC.md, ловит другой класс ошибок.

## Non-Functional Requirements

1. `fetch_repo_lifecycle_signal()` не имеет побочных эффектов кроме одного
   сетевого вызова — не пишет на диск, не мутирует vault.
2. Ошибка получения lifecycle-данных о репозитории (сеть/rate limit/404) не
   трактуется как "мёртв" — файл пропускается в этом прогоне целиком,
   обрабатывается заново на следующем плановом прогоне.
3. Ошибка `list_releases()`/`list_workflow_runs_for_repo()` — гранулярная
   деградация на уровне одного сигнала (§9), не всего файла.
4. `evidence_log` не получает дублирующую запись для неизменного условия
   между прогонами (`detect_transition()`, §7).
5. Несколько подходящих файлов обрабатываются за один прогон job'а, один
   git commit на весь батч — по паттерну `radar`/`promote_candidates`.
6. `python3 -m py_compile analyze.py vault_write.py recheck_lifecycle.py`
   перед коммитом.
7. Никакого em-dash/en-dash в python-строках.

## Security Considerations

- `recheck_lifecycle.py` не принимает внешний ввод, определяющий, какой
  файл обрабатывать — сам перечисляет `01_Assessments/` по
  `status == VALIDATED_SHIFT`. Поверхности path traversal через
  CI-переменные нет (тот же паттерн, что `promote_candidates.py`).
- Новых секретов сверх уже существующих (`GITHUB_READ_TOKEN`,
  `GITLAB_PUSH_TOKEN`, `CI_JOB_TOKEN`) не требуется.
- Новых pip-зависимостей нет — `license-expression` явно не подключается
  (§5).
- `fetch_repo_lifecycle_signal()` ошибку API трактует как "нет данных", не
  как "мёртв"/"жив"/"изменился" — Graceful Degradation, тот же принцип, что
  `check_repo_alive()`.

## Test Plan

1. **`fetch_repo_lifecycle_signal()` — mock-тесты**: `gh_api.repos.get`
   возвращает полный dict с `archived`/`license`/`pushed_at`/`private` →
   корректно извлечённые поля; `license` отсутствует в ответе → `None`, не
   исключение; вызов бросает исключение → `None`.
2. **`fetch_repo_signal()` расширение — mock-тест**: `license_spdx_id`
   извлекается из того же `meta`, что уже используется для
   `root_commit_sha`, без второго вызова `repos.get`.
3. **`detect_transition()` — unit-тесты**: пустой `evidence_log` +
   `condition_now=True` → `entered_type`; последнее событие `entered_type` +
   `condition_now=True` → `None` (не дублирует); последнее событие
   `entered_type` + `condition_now=False` → `exited_type`; последнее
   событие `exited_type` + `condition_now=False` → `None`.
4. **`append_evidence_only()` — mock/tmp-файл тесты**: `events` пишутся в
   `evidence_log`, `status`/`verdict_history`/тело файла не меняются;
   `extra_fields` мержится в frontmatter; файл без frontmatter → `False`.
5. **`process_file()` — mock-тесты** (`test_recheck_lifecycle.py`):
   - `archived=True` → `write_verdict_entry(..., "ARCHIVED_DEAD", ...)`
     вызван, остальные сигналы не проверяются.
   - `archived=False`, `license_spdx_id` без изменений, все условия ложны
     → `append_evidence_only` не вызывается вообще.
   - `license_spdx_id` без baseline (файл без поля) → `extra_fields` с
     `license_baseline_origin="migration"`, событие не пишется.
   - `license_spdx_id` изменился → событие `license_changed` с `old`/`new`,
     baseline обновлён.
   - `pushed_at` старше `FROZEN_MONTHS`, до этого не было `frozen_entered`
     → событие `frozen_entered`; повторный прогон с тем же условием →
     `None`, событие не дублируется.
   - `private=True` впервые → `visibility_lost`; `private=False` после
     `visibility_lost` → `visibility_restored`.
   - `list_releases` < 2 релизов → `releases_stopped`-сигнал не
     оценивается.
   - `list_workflow_runs_for_repo` пуст → `ci_broken`-сигнал не
     оценивается.
   - `fetch_repo_lifecycle_signal` → `None` → файл пропускается целиком,
     `append_evidence_only`/`write_verdict_entry` не вызываются.
   - `list_releases`/`list_workflow_runs_for_repo` бросает исключение →
     только этот сигнал пропущен, остальные события в батче пишутся.
6. **Реальный ghapi-вызов** (Правило 28, тот же принцип, что реальный
   LLM-вызов и реальный `check_repo_alive()` в предыдущих фазах): один
   реальный вызов `fetch_repo_lifecycle_signal("facebook", "react")` +
   `list_releases`/`list_workflow_runs_for_repo` на том же репозитории, без
   записи в vault. **Выполнено 05.08.2026** — структура ответа совпала с
   §11 без расхождений (см. §11, абзац "Подтверждено реальным вызовом").
7. `python3 -m py_compile analyze.py vault_write.py recheck_lifecycle.py`.
   **Выполнено.**

## Milestones

1. [x] `analyze.py`: `fetch_repo_lifecycle_signal()`.
2. [x] `analyze.py`: `fetch_repo_signal()` — расширение `license_spdx_id`;
   `analyze_and_save()` — `extra_frontmatter` расширение.
3. [x] `vault_write.py`: `append_evidence_only()`; `CANONICAL_FIELD_ORDER`
   расширение.
4. [x] Unit-тесты Milestone 1-3 (Test Plan §1-4).
5. [x] `recheck_lifecycle.py`: полный флоу (§11).
6. [x] Unit-тесты `recheck_lifecycle.py` (Test Plan §5) — 46
   новых/расширенных тестов, полный прогон проекта 99/99.
7. [x] Реальный ghapi-вызов, подтверждение структуры ответа (Test Plan §6)
   — совпало с §11, правок не потребовалось.
8. [ ] `.gitlab-ci.yml`: job `recheck_lifecycle` + правки `rules` в
   `radar`/`promote_candidates` (§12).
9. [ ] Показать финальный список `rules:` для всех затронутых job'ов
   владельцу до коммита `.gitlab-ci.yml`.
10. [ ] Полный diff, явное подтверждение владельца перед commit/push.
11. [ ] Новый GitLab Schedule (`$LIFECYCLE_ONLY=="true"`, ежемесячный cron)
    создан в UI, реальный приёмочный прогон в CI (Правило 31) — не только
    чтение YAML.

## Open Questions / Decisions Needed

Все развилки этого интервью закрыты (05.08.2026):
- Периметр — только `VALIDATED_SHIFT`.
- Архивация → `ARCHIVED_DEAD` напрямую, без карантина.
- Остальные четыре сигнала (лицензия/заморожен/видимость/релизы/CI) —
  evidence-only, `status` не трогают.
- `evidence_log` — event log (переходы), не measurement log; четыре из
  пяти сигналов — пары `entered`/`exited`, лицензия — единичное событие с
  обновлением baseline.
- `append_evidence_only()` — новая функция в `vault_write.py`,
  `write_verdict_entry()` не меняется (два разных вопроса: точка входа для
  status-меняющих записей vs условность записи при неизменном status — не
  пересмотр решения, отдельная развилка).
- `license_spdx_id`/`license_baseline_origin` — новые поля, захватываются
  в `analyze.py` в этой сессии, без нового API-вызова.
- `license-expression` не подключается — GitHub API возвращает атомарный
  `spdx_id`, не составное выражение.
- `fetch_repo_lifecycle_signal()` — новая функция, `check_repo_alive()` не
  трогается.
- `visibility_lost`/`visibility_restored` — нейтральное имя, не
  `went_private`; факт без интерпретации rugpull.
- `releases_stopped`/`ci_broken` — сигнал оценивается только при наличии
  истории (≥2 релизов / ≥1 workflow run когда-либо), иначе не оценивается
  вообще.
- `read_repo_url()` дублируется в `recheck_lifecycle.py`, не выносится в
  общий модуль — не трогать закрытый код Фазы 3 п.1 ради этой сессии.
- CI-каденция — новый GitLab Schedule, `$LIFECYCLE_ONLY=="true"`, по
  паттерну `$PUBLISH_ONLY`/`$PROMOTE_ONLY`/`$CONFIRM_REPO`.
- `radar`/`promote_candidates` — явное исключение `$LIFECYCLE_ONLY` в
  `rules`. `lint_vault` — без изменений (уже безусловен на любом
  web/schedule, верифицировано против реального файла).
- Telegram — тишина, как у `promote_candidates.py`/`confirm_candidate.py`.
- Test Plan — mock-тесты + один реальный ghapi-вызов на структуру ответа
  (не на переход, переходы редки/непредсказуемы по времени).

Открытых пунктов для этапа реализации не осталось, кроме точечной
верификации имён методов `ghapi` (§11, помечено явно как неподтверждённое
в этой сессии).
