import os
import sys

import vault_write

VAULT_ROOT = os.environ.get("VAULT_ROOT", os.path.expanduser("~/radar/radar"))
ASSESSMENTS_PATH = os.path.join(VAULT_ROOT, "01_Assessments")


def main():
    repo = os.environ.get("CONFIRM_REPO", "")
    decision = os.environ.get("CONFIRM_DECISION", "")

    if not repo or "/" in repo or ".." in repo:
        print(f"ОШИБКА: недопустимое значение CONFIRM_REPO: {repo!r}")
        sys.exit(1)
    if decision not in {"approve", "reject"}:
        print(f"ОШИБКА: CONFIRM_DECISION должен быть 'approve' или 'reject', получено: {decision!r}")
        sys.exit(1)

    filepath = os.path.join(ASSESSMENTS_PATH, repo + ".md")
    if not os.path.exists(filepath):
        print(f"ОШИБКА: файл не найден: {filepath}")
        sys.exit(1)

    frontmatter, _ = vault_write.read_frontmatter(filepath)
    current_status = frontmatter.get("status") if frontmatter else None
    if frontmatter is None or current_status != "CANDIDATE_LOW_CONFIDENCE":
        print(f"ОШИБКА: {filepath} не в статусе CANDIDATE_LOW_CONFIDENCE (текущий: {current_status!r})")
        sys.exit(1)

    if decision == "approve":
        new_status = "VALIDATED_SHIFT"
        narrative_line = f"- {new_status} подтверждено владельцем вручную (HITL, confirm_candidate)"
    else:
        new_status = "REJECTED_NOISE"
        narrative_line = "- отклонено владельцем вручную (HITL, confirm_candidate)"

    written = vault_write.write_verdict_entry(filepath, new_status, narrative_line)
    if not written:
        print(f"ОШИБКА записи: {filepath}")
        sys.exit(1)

    print(f"{repo}: CANDIDATE_LOW_CONFIDENCE -> {new_status}")


if __name__ == "__main__":
    main()
