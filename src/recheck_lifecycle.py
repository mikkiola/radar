import os
from datetime import date, datetime

import vault_write
from analyze import parse_github_owner_repo, fetch_repo_lifecycle_signal, gh_api

VAULT_ROOT = os.environ.get("VAULT_ROOT", os.path.expanduser("~/radar/radar"))
ASSESSMENTS_PATH = os.path.join(VAULT_ROOT, "01_Assessments")
FROZEN_MONTHS = 6
RELEASES_STOPPED_MONTHS = 12


def find_validated_shift_files():
    files = []
    if not os.path.exists(ASSESSMENTS_PATH):
        return files
    for name in sorted(os.listdir(ASSESSMENTS_PATH)):
        if not name.endswith(".md"):
            continue
        filepath = os.path.join(ASSESSMENTS_PATH, name)
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
    """Определяет, является ли condition_now переходом относительно
    последнего события этой пары в evidence_log. currently_in = последнее
    событие пары было entered_type (пары ещё не было -> currently_in=False,
    первое истинное наблюдение = вход). Возвращает entered_type/exited_type
    для append, или None, если состояние не изменилось с прошлого прогона -
    не порождает новую запись при неизменном факте (evidence_log - event log,
    не measurement log)."""
    relevant = [e for e in (evidence_log or []) if e.get("event_type") in (entered_type, exited_type)]
    currently_in = bool(relevant) and relevant[-1]["event_type"] == entered_type

    if condition_now and not currently_in:
        return entered_type
    if not condition_now and currently_in:
        return exited_type
    return None


def months_since(iso_timestamp):
    dt = datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    return (datetime.now() - dt).days / 30


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
    """Перепроверяет один VALIDATED_SHIFT-файл на сигналы риска устаревания
    вывода. archived - единственный сигнал, меняющий status (сразу
    ARCHIVED_DEAD, без карантина, см. SPEC.md §2). Остальные - evidence-only,
    пополняют evidence_log через append_evidence_only(), status не трогают."""
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
        if written:
            print(f"   {filepath}: {len(events)} evidence-событий{suffix}")
        else:
            print(f"   ОШИБКА записи evidence: {filepath}")


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
