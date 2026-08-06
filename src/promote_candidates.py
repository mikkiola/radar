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
    """Продвигает один CANDIDATE-файл, если карантин (QUARANTINE_DAYS) истёк:
    VALIDATED_SHIFT, если репозиторий жив, REJECTED_NOISE, если архивирован.
    Если check_repo_alive() не смог получить данные - файл остаётся CANDIDATE,
    обрабатывается заново на следующем прогоне (см. SPEC.md, §2)."""
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
