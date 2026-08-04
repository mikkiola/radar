import os
import re
import glob
import argparse
import difflib
import subprocess

import yaml

VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar/01_Assessments"))

VERDICT_TO_STATUS = {
    "СДВИГ": "VALIDATED_SHIFT",
    "ШУМ": "REJECTED_NOISE",
}

HISTORY_LINE_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) [-—] ([^:(]+)")
BOLD_VERDICT_RE = re.compile(r"\*\*(СДВИГ|ШУМ)\*\*")


def extract_top_verdict(content):
    """Значение верхнего поля **Оценка:** (СДВИГ/ШУМ) или None, если поле не найдено."""
    for line in content.splitlines():
        if line.startswith("**Оценка:**"):
            value = line.replace("**Оценка:**", "").strip()
            if value in VERDICT_TO_STATUS:
                return value
    return None


def extract_human_correction_flip(content, top_verdict):
    """Если в '## Правка человека' есть явный жирный вердикт, отличный от top_verdict -
    вернуть его. Иначе None (нет правки, либо правка совпадает с верхним полем)."""
    start = content.find("## Правка человека")
    if start == -1:
        return None
    end = content.find("\n## ", start + len("## Правка человека"))
    block = content[start:end] if end != -1 else content[start:]
    for match in BOLD_VERDICT_RE.finditer(block):
        candidate = match.group(1)
        if candidate != top_verdict:
            return candidate
    return None


def parse_verdict_history(content):
    """Разобрать '## История оценок' в список {date, verdict} для новой схемы.
    Строки с токеном вне {СДВИГ, ШУМ} пропускаются, но логируются - не останавливают backfill."""
    start = content.find("## История оценок")
    if start == -1:
        return [], []
    end = content.find("\n## ", start + len("## История оценок"))
    section = content[start:end] if end != -1 else content[start:]

    entries = []
    skipped = []
    for raw_line in section.splitlines():
        stripped = raw_line.strip()
        if not stripped.startswith("-"):
            continue
        match = HISTORY_LINE_RE.match(stripped)
        if not match:
            continue
        entry_date, token = match.group(1), match.group(2).strip()
        status = VERDICT_TO_STATUS.get(token)
        if status is None:
            skipped.append(stripped)
            continue
        entries.append({"date": entry_date, "verdict": status})
    return entries, skipped


def build_frontmatter(status, verdict_history):
    return {
        "status": status,
        "maturity_score": None,
        "novelty_score": None,
        "assertion_vector": None,
        "evidence_log": [],
        "root_commit_sha": None,
        "verdict_history": verdict_history,
    }


def backfill_file(filepath):
    """Вернуть отчёт по одному файлу: эффективный вердикт, статус, пропущенные строки
    истории, новое содержимое файла (с frontmatter) - не пишет на диск."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    filename = os.path.basename(filepath)

    if content.startswith("---\n"):
        return {"filename": filename, "skipped_already_migrated": True}

    top_verdict = extract_top_verdict(content)
    if top_verdict is None:
        return {"filename": filename, "error": "не найдено верхнее поле **Оценка:**"}

    flip = extract_human_correction_flip(content, top_verdict)
    effective_verdict = flip if flip is not None else top_verdict
    status = VERDICT_TO_STATUS[effective_verdict]

    verdict_history, skipped = parse_verdict_history(content)
    frontmatter = build_frontmatter(status, verdict_history)
    yaml_block = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False, default_flow_style=False)
    new_content = f"---\n{yaml_block}---\n{content}"

    return {
        "filename": filename,
        "top_verdict": top_verdict,
        "flip": flip,
        "status": status,
        "verdict_history_count": len(verdict_history),
        "skipped_history_lines": skipped,
        "old_content": content,
        "new_content": new_content,
    }


def print_report(report):
    filename = report["filename"]
    if report.get("skipped_already_migrated"):
        print(f"[backfill] ПРОПУЩЕН {filename}: уже мигрирован (файл начинается с frontmatter)")
        return
    if "error" in report:
        print(f"[backfill] ПРОПУЩЕН {filename}: {report['error']}")
        return
    flip_note = f" (ПРАВКА ЧЕЛОВЕКА: {report['top_verdict']} -> {report['flip']})" if report["flip"] else ""
    print(f"[backfill] {filename}: status={report['status']}{flip_note}, verdict_history={report['verdict_history_count']} записей")
    for skipped_line in report["skipped_history_lines"]:
        print(f"    ПРОПУЩЕНА строка истории (нераспознанный токен): {skipped_line!r}")


def print_diff(report):
    diff = difflib.unified_diff(
        report["old_content"].splitlines(keepends=True),
        report["new_content"].splitlines(keepends=True),
        fromfile=f"a/{report['filename']}",
        tofile=f"b/{report['filename']}",
    )
    print("".join(diff))


def verify_local_checkout_matches_origin(vault_path):
    """Перед --apply сверить список файлов локального чекаута VAULT_PATH с
    origin/vault - тот же класс риска, что и в инциденте с production cron
    (Правило 24 CONSTITUTION): локальный чекаут может отставать от origin.
    Возвращает текст ошибки при расхождении, иначе None."""
    repo_root = os.path.dirname(os.path.normpath(vault_path))

    fetch = subprocess.run(
        ["git", "-C", repo_root, "fetch", "origin", "vault"],
        capture_output=True, text=True,
    )
    if fetch.returncode != 0:
        return f"git fetch origin vault не удался: {fetch.stderr.strip()}"

    ls_tree = subprocess.run(
        ["git", "-C", repo_root, "ls-tree", "-r", "origin/vault", "--name-only", "--", "01_Assessments"],
        capture_output=True, text=True,
    )
    if ls_tree.returncode != 0:
        return f"git ls-tree origin/vault не удался: {ls_tree.stderr.strip()}"

    origin_files = {
        os.path.basename(line) for line in ls_tree.stdout.splitlines() if line.endswith(".md")
    }
    local_files = {
        os.path.basename(f) for f in glob.glob(os.path.join(vault_path, "*.md"))
    }

    if origin_files == local_files:
        return None

    parts = []
    missing_locally = origin_files - local_files
    extra_locally = local_files - origin_files
    if missing_locally:
        parts.append(f"есть в origin/vault, нет локально: {sorted(missing_locally)}")
    if extra_locally:
        parts.append(f"есть локально, нет в origin/vault: {sorted(extra_locally)}")
    return "локальный чекаут отстаёт от origin/vault (" + "; ".join(parts) + "), обновите перед --apply"


def main():
    parser = argparse.ArgumentParser(description="Одноразовая миграция 01_Assessments/ на YAML frontmatter (Вариант A, backfill)")
    parser.add_argument("--apply", action="store_true", help="Реально записать файлы (по умолчанию - только dry-run с отчётом)")
    parser.add_argument("--only", help="Через запятую - подмножество filename для pilot-прогона")
    parser.add_argument("--diff", action="store_true", help="Показать полный unified diff для каждого файла")
    args = parser.parse_args()

    if not os.path.exists(VAULT_PATH):
        print(f"[backfill] ОШИБКА: vault не найден: {VAULT_PATH}")
        return

    only = set(args.only.split(",")) if args.only else None
    files = sorted(glob.glob(os.path.join(VAULT_PATH, "*.md")))
    if only:
        files = [f for f in files if os.path.basename(f) in only]
        missing = only - {os.path.basename(f) for f in files}
        if missing:
            print(f"[backfill] ВНИМАНИЕ: не найдены файлы из --only: {missing}")

    print(f"[backfill] vault: {VAULT_PATH}")
    print(f"[backfill] режим: {'APPLY (реальная запись)' if args.apply else 'DRY-RUN (без записи)'}")
    print(f"[backfill] файлов к обработке: {len(files)}")
    print()

    if args.apply:
        mismatch = verify_local_checkout_matches_origin(VAULT_PATH)
        if mismatch:
            print(f"[backfill] ОШИБКА: {mismatch}")
            return

    errors = 0
    already_migrated = 0
    total_skipped_history = 0
    written = 0

    for filepath in files:
        report = backfill_file(filepath)
        print_report(report)
        if report.get("skipped_already_migrated"):
            already_migrated += 1
            continue
        if "error" in report:
            errors += 1
            continue
        total_skipped_history += len(report["skipped_history_lines"])
        if args.diff:
            print_diff(report)
        if args.apply:
            os.path.exists(filepath)  # инвариант CONSTITUTION - точечная правка только существующего файла
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report["new_content"])
            written += 1

    print()
    print(f"[backfill] итог: обработано={len(files)}, уже мигрировано (пропущено)={already_migrated}, ошибок={errors}, пропущенных строк истории={total_skipped_history}, {'записано=' + str(written) if args.apply else 'записей НЕ было (dry-run)'}")


if __name__ == "__main__":
    main()
