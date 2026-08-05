# Radar 2.0 — Фаза 3, п.1: `status: CANDIDATE` — time-based карантин — Specification

## Overview

Roadmap v8 (04-05.08.2026) выносит п.1 Фазы 3 в отдельную сессию: `status:
CANDIDATE` — карантин, основанный на времени, а не на суждении LLM. Не
путать с `CANDIDATE_LOW_CONFIDENCE` (эпистемический карантин, уже
реализован — LLM сама не уверена в выводе в момент оценки). `CANDIDATE`
решает другую задачу: репозиторию нужно ВРЕМЯ, чтобы показать, доживёт ли
гипотеза о нём, прежде чем Radar зафиксирует вывод как `VALIDATED_SHIFT`.

**Условие присвоения** (решено владельцем до интервью): `evidence_log`
пуст на момент оценки. Верификация против кода (Rule 28) показала, что на
единственном call site, где это решение принимается (`compute_status()`,
`analyze.py:445` — первичная оценка нового репозитория), `evidence_log`
**всегда** пуст (`extra_frontmatter["evidence_log"] = []` для нового файла,
[analyze.py:481](analyze.py#L481)) — условие тождественно истинно на этом
пути. `update_assessments.py` физически не может смайнтить свежий
`VALIDATED_SHIFT`: несовпадение нового вердикта с текущим `status` уже
сегодня уходит в `CANDIDATE_LOW_CONFIDENCE`
([update_assessments.py:180](update_assessments.py#L180)), не в
`VALIDATED_SHIFT`. Решено в интервью: **эта сессия трогает только
`analyze.py`, `update_assessments.py` не меняется**.

**N дней карантина = 14** (стартовое значение, подлежит фальсификации на
реальных прогонах).

**Выход из карантина**: `check_repo_alive(owner, repo) -> bool | None`,
новая функция в `analyze.py` (реиспользует существующие `gh_api` и
`parse_github_owner_repo()` оттуда же, не создаёт второй `GhApi`-инстанс).
Решено в интервью: проверяется **только** `repo.archived` —
`repo.pushed_at` не используется как критерий "недостаточно свежий"
(зрелые `Maintenance`-репозитории месяцами не пушат, оставаясь валидными;
требовать push за 14-дневное окно было бы confounder'ом, не причиной
ненадёжности). Спроектирована для переиспользования будущим
`recheck_lifecycle.py` (Roadmap п.2, отдельная сессия) — просто добавляет
ещё один шаг, не требует переписывания.

## Goals

- [x] `analyze.py`: новый файл с подтверждённым вердиктом уходит в
  `CANDIDATE`, не в `VALIDATED_SHIFT`, напрямую — `compute_status()` не
  меняется, гейт — отдельная проверка сразу после вызова.
- [x] `analyze.py`: `check_repo_alive(owner, repo)` — три исхода (жив /
  мёртв / не удалось определить), не бинарная логика.
- [x] `promote_candidates.py` — новый скрипт, ежедневный CI job:
  находит `status == CANDIDATE` старше 14 дней, решает
  promote (`VALIDATED_SHIFT`) / reject (`REJECTED_NOISE`) / skip (оставить
  `CANDIDATE`, данные недостоверны в этом прогоне).
- [x] `.gitlab-ci.yml`: job `promote_candidates`, schedule + `$PROMOTE_ONLY`
  web-триггер, по паттерну остальных vault-пишущих job'ов (rebase →
  full-scan гейт → push).

## Tech Stack

Без изменений: Python 3, `ghapi`, `pyyaml`, `pytest`. Никаких новых
зависимостей — `ghapi` уже используется в `radar` job'е.

## Detailed Requirements

### 1. Гейт `CANDIDATE` в `analyze.py`

`compute_status()` ([analyze.py:170-178](analyze.py#L170-L178)) **не
меняется** — остаётся чистой функцией вердикта по существу
(`VALIDATED_SHIFT` / `CANDIDATE_LOW_CONFIDENCE` / `None`). Решено в
интервью: смешивать "вердикт оценки" и "готовность к публикации" в одном
возвращаемом значении — тот же класс путаницы, что уже был между
`CANDIDATE` и `CANDIDATE_LOW_CONFIDENCE` до их явного разведения в
предыдущей фазе.

Явный гейт сразу после вызова, в `analyze_and_save()`. Реализовано как
отдельная маленькая функция `apply_quarantine_gate(verdict)` рядом с
`compute_status()`, а не инлайн-код на call site — иначе логику
"VALIDATED_SHIFT -> CANDIDATE" нельзя протестировать без полного мока
всего пайплайна `analyze_and_save()` (LLM-вызов, GitHub API, файловая
система). Не нарушает решение интервью "compute_status() не меняется" —
это по-прежнему отдельная функция, вызываемая сразу после, просто
именованная, а не инлайн:

```python
def apply_quarantine_gate(verdict):
    return "CANDIDATE" if verdict == "VALIDATED_SHIFT" else verdict
```

Call site:

```python
verdict = compute_status(novelty_score, cross_validation_confirmed, novelty_checklist_passes)
if verdict is None:
    print(f"   ШУМ (novelty={novelty_score}) - {result.get('name_en', title)[:40]} - пропускаем")
    continue
status = apply_quarantine_gate(verdict)
```

`status` (не `verdict`) используется дальше по функции без изменений —
в `filename`, `body_template`, `extra_frontmatter`, `write_verdict_entry()`.

**Метка `confidence` в теле файла** (было: `"высокая" if status ==
"VALIDATED_SHIFT" else "низкая"`). `VALIDATED_SHIFT` больше не встречается
на этом call site — ветка мертва. Решено в интервью: развести `CANDIDATE`
и `CANDIDATE_LOW_CONFIDENCE` текстом, чтобы владелец, читая файл в
Obsidian, сразу видел причину низкой уверенности без обращения к `status`
в frontmatter. Реализовано как отдельная функция `confidence_label(status)`
(тот же мотив тестируемости, что и `apply_quarantine_gate`):

```python
def confidence_label(status):
    return "в карантине" if status == "CANDIDATE" else "низкая"
```

Call site: `confidence = confidence_label(status)`.

`state_value`/`state_confidence`/`evidence_log` пишутся штатно через
`write_verdict_entry(..., state_value=state_value)` независимо от статуса
(Фаза 3, Decision B+) — эта ось не пересекается с `CANDIDATE`-карантином.

### 2. `check_repo_alive()` — определение "жив ли репозиторий"

Новая функция в `analyze.py` (рядом с `parse_github_owner_repo()`,
реиспользует модульный `gh_api`):

```python
def check_repo_alive(owner, repo):
    """True/False - определённый результат (repo.archived). None - не
    удалось получить данные (сетевая ошибка/rate limit/404) - это НЕ факт
    о состоянии репозитория, вызывающий код обязан пропустить файл в этом
    прогоне, а не трактовать как мёртв или жив."""
    try:
        info = gh_api.repos.get(owner, repo)
        return not info.get("archived", False)
    except Exception as e:
        print(f"   не удалось получить данные о репозитории {owner}/{repo}: {e}")
        return None
```

Доступ к полю ответа API (`info.get(...)`) внутри `try`, не после него — по
тому же паттерну, что и `fetch_repo_signal()` (весь разбор ответа GitHub
API внутри `try`, не снаружи). Найдено на этапе diff-review: изначальный
черновик держал `info.get(...)` вне `try`, что оставляло необработанным
гипотетический случай, когда `gh_api.repos.get()` возвращает успешный
ответ, но `.get()` на нём бросает исключение.

Решено в интервью (отклонена полная FSM с `repo_state`/`unknown_since`/
`LOST` — нарушает Decision B+, вводит состояния без наблюдаемого
триггера): три исхода через `True`/`False`/`None`, не больше. Ошибка API
— это отсутствие данных, а не сигнал "мёртв". Формулировка в логах:
"не удалось получить данные о репозитории", не "недоступен"/"мёртв" —
эти слова описывали бы факт, которого у нас нет. Риск накопления
`CANDIDATE`-файлов из-за повторяющихся ошибок API признан и вынесен в
BACKLOG — не решается в этой сессии, нет наблюдаемого случая, что это
реально происходит.

`repo.pushed_at` не используется в этой функции (см. Overview).

### 3. `promote_candidates.py` — новый файл

```python
import os
from datetime import date

import vault_write
from analyze import parse_github_owner_repo, check_repo_alive

VAULT_PATH = os.environ.get("VAULT_PATH", "01_Assessments")
QUARANTINE_DAYS = 14


def find_candidate_files():
    files = []
    if not os.path.exists(VAULT_PATH):
        return files
    for name in sorted(os.listdir(VAULT_PATH)):
        if not name.endswith(".md"):
            continue
        filepath = os.path.join(VAULT_PATH, name)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        if frontmatter and frontmatter.get("status") == "CANDIDATE":
            files.append(filepath)
    return files


def read_repo_url(body):
    for line in body.splitlines():
        if line.startswith("**Репозиторий:**"):
            return line.split("**Репозиторий:**", 1)[1].strip()
    return None


def process_file(filepath):
    frontmatter, body = vault_write.read_frontmatter(filepath)
    if frontmatter is None:
        print(f"   ОШИБКА: {filepath} без frontmatter, пропускаю")
        return

    history = frontmatter.get("verdict_history") or []
    if not history:
        print(f"   ОШИБКА: {filepath} status=CANDIDATE без verdict_history, пропускаю")
        return

    candidate_date = date.fromisoformat(history[-1]["date"])
    days_in_candidate = (date.today() - candidate_date).days
    if days_in_candidate < QUARANTINE_DAYS:
        return

    url = read_repo_url(body)
    owner, repo = parse_github_owner_repo(url)
    if not owner or not repo:
        print(f"   ОШИБКА: не удалось разобрать owner/repo из {url!r} в {filepath}")
        return

    alive = check_repo_alive(owner, repo)
    today = date.today().strftime("%Y-%m-%d")

    if alive is None:
        print(f"   {filepath}: данные о репозитории недоступны в этом прогоне, остаётся CANDIDATE")
        return
    elif alive:
        narrative_line = f"- {today} - VALIDATED_SHIFT: карантин пройден ({QUARANTINE_DAYS}+ дней), репозиторий активен - promote_candidates"
        written = vault_write.write_verdict_entry(filepath, "VALIDATED_SHIFT", narrative_line)
    else:
        narrative_line = f"- {today} - REJECTED_NOISE: карантин истёк, репозиторий архивирован - promote_candidates"
        written = vault_write.write_verdict_entry(filepath, "REJECTED_NOISE", narrative_line)

    if not written:
        print(f"   ОШИБКА записи: {filepath}")
        return
    print(f"   {filepath}: CANDIDATE -> {'VALIDATED_SHIFT' if alive else 'REJECTED_NOISE'}")


def main():
    files = find_candidate_files()
    print(f"Найдено CANDIDATE-файлов: {len(files)}")
    for filepath in files:
        try:
            process_file(filepath)
        except Exception as e:
            print(f"   ОШИБКА при обработке {filepath}: {e}")
    print("Готово.")


if __name__ == "__main__":
    main()
```

`process_file()` вызывается под `try/except` в `main()` — найдено на этапе
diff-review: без этого один повреждённый/неожиданный файл (например, файл
без `verdict_history` с ошибкой в другом месте, не покрытой явной
проверкой) прервал бы весь прогон и оставил необработанными остальные
`CANDIDATE`-файлы в этом батче. По тому же паттерну, что
`analyze_and_save()` (try/except вокруг классификации на каждый проект) и
`update_assessment()` (try/except вокруг всей функции, вызываемой в цикле
`__main__`).

**Источник даты**: `verdict_history[-1]["date"]`, без нового поля во
frontmatter. Инвариант `write_verdict_entry()`
([vault_write.py:141-144](vault_write.py#L141-L144)): `status` всегда
равен `verdict_history[-1]["verdict"]` — раз файл отобран по
`status == "CANDIDATE"`, последняя запись истории обязана быть именно
записью о присвоении `CANDIDATE`. Решено в интервью: не вводить
`candidate_since` ради одного job'а.

`state_value=None` (по умолчанию) в обоих вызовах `write_verdict_entry()`
— решение здесь человеческое/детерминированное (архивирован или нет), не
новое LLM-суждение, `evidence_log` этим вызовом не пополняется — тот же
принцип, что и в `confirm_candidate.py` (Фаза 3, §2 предыдущей спеки).

**Telegram**: решено в интервью — тишина при promotion, как при
`confirm_candidate.py` approve. Публикация всё равно не мгновенная —
`telegram_post.py` подхватит свежий `VALIDATED_SHIFT` на следующем
плановом `publish` через `find_latest_shift()`
([telegram_post.py:64-78](telegram_post.py#L64-L78)). Никаких новых
секретов сверх `GITHUB_READ_TOKEN` (уже используется `analyze.py`) и
`GITLAB_PUSH_TOKEN`/`CI_JOB_TOKEN` (git).

`patterns.py`/`telegram_post.py` уже фильтруют строго
`status == "VALIDATED_SHIFT"` ([patterns.py:281](patterns.py#L281),
[telegram_post.py:46](telegram_post.py#L46)) — `CANDIDATE` автоматически
не публикуется и не участвует в паттернах, без дополнительного кода.

### 4. `check_frontmatter.py` — без изменений

`"CANDIDATE"` уже в `VALID_STATUSES` (зарезервировано заранее, до этой
фазы). Новых полей во frontmatter не вводится — дата читается из уже
существующего `verdict_history`. Подтверждено в интервью: этот файл в
текущей сессии не меняется.

### 5. `.gitlab-ci.yml` — новый job `promote_candidates`

```yaml
promote_candidates:
  stage: run
  script:
    - pip install requests pyyaml ghapi --quiet
    - git config --global user.email "radar@gitlab.com"
    - git config --global user.name "Radar Bot"
    - git clone --branch vault https://gitlab-ci-token:${CI_JOB_TOKEN}@gitlab.com/lyolich777ka/radar.git vault_repo
    - VAULT_PATH="$(pwd)/vault_repo/01_Assessments" python3 promote_candidates.py
    - cd vault_repo
    - git remote set-url origin https://lyolich777ka:${GITLAB_PUSH_TOKEN}@gitlab.com/lyolich777ka/radar.git
    - git add -A
    - |
      if git diff --staged --quiet; then
        echo "Нет CANDIDATE-файлов для обработки"
      else
        git commit -m "Карантин: promote_candidates $(date '+%Y-%m-%d')"
        git pull --rebase origin vault
        python3 ../check_frontmatter.py 01_Assessments || exit 1
        git push origin vault
      fi
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
    - if: '$CI_PIPELINE_SOURCE == "web" && $PROMOTE_ONLY == "true"'
```

`promote_candidates.py` импортирует `analyze.py`, а тот безусловно
импортирует `requests`/`ghapi` и читает (не проверяет)
`ANTHROPIC_API_KEY`/грузит `MODEL_CONFIG` из
`99_System/model_config.json` (файл существует в master-ветке, путь
строится от `__file__`, не от `VAULT_PATH` — [analyze.py:18](analyze.py#L18)) —
безопасно импортировать без реального ключа. Верифицировано (Rule 28):
`analyze.py` не импортирует пакет `anthropic` напрямую, вызывает Anthropic
API через `requests` — поэтому `anthropic` в `pip install` job'а не
нужен.

Существующий daily-schedule (тот же, что триггерит `radar`/`lint_vault`)
покрывает `promote_candidates` без правки расписания в GitLab UI —
job фильтруется только через `rules`, отдельного нового schedule не
создаётся.

**Web-триггер**: решено в интервью — `$PROMOTE_ONLY == "true"`, по
паттерну `$PUBLISH_ONLY`/`$CONFIRM_REPO`/`$PATTERN_MODE`. Без отдельной
переменной голый `$CI_PIPELINE_SOURCE == "web"` запускал бы
`promote_candidates` при любом ручном запуске любого другого job'а.
Назначение — только инженерная проверка/отладка, штатная эксплуатация
исключительно через schedule.

## Non-Functional Requirements

1. `check_repo_alive()` не имеет побочных эффектов кроме одного сетевого
   вызова `gh_api.repos.get()` — не пишет на диск, не мутирует vault.
2. `promote_candidates.py` не трогает файлы вне `status == CANDIDATE` и не
   продвигает файлы моложе `QUARANTINE_DAYS` — оба условия проверяются до
   любой записи.
3. Несколько подходящих `CANDIDATE`-файлов обрабатываются за один прогон
   job'а, один git commit на весь батч — по паттерну `radar`/`patterns`
   job'ов, не по одному коммиту на файл.
4. Ошибка получения данных о репозитории (сеть/rate limit/404) не
   трактуется как "мёртв" — файл остаётся `CANDIDATE`, обрабатывается
   заново на следующем плановом прогоне.
5. `python3 -m py_compile analyze.py promote_candidates.py` перед
   коммитом.
6. Никакого em-dash/en-dash в python-строках.

## Security Considerations

- `promote_candidates.py` не принимает внешний ввод, определяющий, какой
  файл обрабатывать (в отличие от `confirm_candidate.py`'s
  `$CONFIRM_REPO`) — сам перечисляет `01_Assessments/` по
  `status == CANDIDATE`. Поверхности path traversal через CI-переменные
  здесь нет.
- Новых секретов сверх уже существующих (`GITHUB_READ_TOKEN`,
  `GITLAB_PUSH_TOKEN`, `CI_JOB_TOKEN`) не требуется.
- `check_repo_alive()` ошибку API трактует как "нет данных", не как
  "мёртв"/"жив" — намеренное решение, чтобы неполные данные не приводили
  к неверному REJECTED_NOISE/VALIDATED_SHIFT (Graceful Degradation).

## Test Plan

1. **Гейт в `analyze.py`** (`test_analyze.py` или отдельный файл):
   `compute_status()` возвращает `"VALIDATED_SHIFT"` → итоговый `status`
   становится `"CANDIDATE"`; возвращает `"CANDIDATE_LOW_CONFIDENCE"` →
   остаётся без изменений; возвращает `None` → файл по-прежнему не
   создаётся (текущее поведение не сломано).
2. **Метка `confidence`**: `status == "CANDIDATE"` → `"в карантине"`;
   `status == "CANDIDATE_LOW_CONFIDENCE"` → `"низкая"`.
3. **`check_repo_alive()` — mock-тесты**: `gh_api.repos.get` возвращает
   `{"archived": True}` → `False`; `{"archived": False}` → `True`;
   выбрасывает исключение → `None`.
4. **`promote_candidates.py` — mock-тесты** (`test_promote_candidates.py`):
   - `days_in_candidate < 14` → пропуск, `write_verdict_entry` не
     вызывается.
   - `days_in_candidate >= 14`, `check_repo_alive` → `True` → пишется
     `VALIDATED_SHIFT`, `state_value=None`.
   - `days_in_candidate >= 14`, `check_repo_alive` → `False` → пишется
     `REJECTED_NOISE`.
   - `days_in_candidate >= 14`, `check_repo_alive` → `None` → пропуск,
     файл остаётся `CANDIDATE`, ничего не пишется.
   - файл без `verdict_history` (не должен встречаться при корректной
     записи, но защита есть) → ошибка в лог, пропуск.
5. **Реальный ghapi-вызов `check_repo_alive()`** (Rule 28, тот же принцип,
   что реальный LLM-вызов в предыдущей фазе): один заведомо архивированный
   репозиторий (`archived: true`), один заведомо активный — подтвердить
   `False`/`True` соответственно на реальном GitHub API, не только на
   моках.

   **Выполнено 05.08.2026** (прямой вызов `analyze.check_repo_alive()`,
   без записи в vault):

   | Репозиторий | archived (реальный GitHub API) | `check_repo_alive()` |
   |---|---|---|
   | `facebook/react` (активный, эталон из Test Plan предыдущей фазы) | `False` | `True` |
   | `jquery/jquery-mobile` (архивирован, `full_name` → `jquery-archive/jquery-mobile`) | `True` | `False` |

   Оба результата совпали с ожидаемыми.
6. `python3 -m py_compile analyze.py promote_candidates.py`.

## Milestones

1. [x] `analyze.py`: гейт `VALIDATED_SHIFT -> CANDIDATE` после
   `compute_status()`, обновлённая метка `confidence`.
2. [x] `analyze.py`: `check_repo_alive(owner, repo)`.
3. [x] Unit-тесты Milestone 1-2 (Test Plan §1-3).
4. [x] `promote_candidates.py`: полный флоу (поиск CANDIDATE, проверка
   14 дней через `verdict_history[-1]`, `check_repo_alive`,
   promote/reject/skip).
5. [x] Unit-тесты `promote_candidates.py` (Test Plan §4).
6. [x] `.gitlab-ci.yml`: job `promote_candidates` (schedule +
   `$PROMOTE_ONLY` web-триггер).
7. [x] Реальный ghapi-вызов на 2 известных репозиториях (Test Plan §5).
8. [ ] Полный diff, явное подтверждение владельца перед commit/push
   (CONSTITUTION, без исключений).

## Open Questions / Decisions Needed

Все развилки этого интервью закрыты (05.08.2026):
- Гейт живёт как отдельная проверка после `compute_status()`, не внутри
  неё — `compute_status()` не меняется.
- `update_assessments.py` не трогается — не может смайнтить свежий
  `VALIDATED_SHIFT` уже сегодня.
- `check_repo_alive()` смотрит только на `archived`, `pushed_at` не
  используется как критерий свежести.
- Не прошёл карантин через 14 дней → сразу `REJECTED_NOISE`, без
  повторных циклов ожидания.
- Ошибка API при проверке → пропуск прогона, файл остаётся `CANDIDATE`,
  не трактуется как "мёртв".
- Дата присвоения `CANDIDATE` берётся из `verdict_history[-1]`, нового
  поля во frontmatter нет.
- Promotion — без Telegram-уведомления, тишина как при
  `confirm_candidate.py` approve.
- `promote_candidates` — отдельный CI job, реиспользует существующий
  daily-schedule через `rules`, web-триггер только через `$PROMOTE_ONLY`.

Открытых пунктов для этапа реализации не осталось.
