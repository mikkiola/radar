import os
import sys

import vault_write

VALID_STATUSES = {
    "VALIDATED_SHIFT",
    "CANDIDATE_LOW_CONFIDENCE",
    "REJECTED_NOISE",
    "CANDIDATE",
    "ARCHIVED_DEAD",
}


def validate_file(filepath):
    """Проверить один файл на валидный frontmatter. Возвращает текст ошибки
    или None, если файл валиден. Единственное место, формулирующее, что
    значит «валидный frontmatter» - используется и inline-гейтом radar job,
    и lint_vault job."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    frontmatter, _ = vault_write.parse_frontmatter(content)
    if frontmatter is None:
        return "frontmatter отсутствует или YAML-блок битый"

    status = frontmatter.get("status")
    if status is None:
        return "поле status отсутствует"
    if status not in VALID_STATUSES:
        return f"status '{status}' не входит в {sorted(VALID_STATUSES)}"

    return None


def validate_paths(paths):
    """Прогнать validate_file по списку путей. Возвращает {filepath: error}
    только для файлов с ошибкой."""
    errors = {}
    for path in paths:
        error = validate_file(path)
        if error is not None:
            errors[path] = error
    return errors


def _expand_paths(args):
    paths = []
    for arg in args:
        if os.path.isdir(arg):
            paths.extend(
                os.path.join(arg, name)
                for name in sorted(os.listdir(arg))
                if name.endswith(".md")
            )
        else:
            paths.append(arg)
    return paths


def main():
    if len(sys.argv) < 2:
        print("Использование: python3 check_frontmatter.py <file_or_dir> [<file_or_dir> ...]")
        sys.exit(1)

    paths = _expand_paths(sys.argv[1:])
    errors = validate_paths(paths)

    for filepath, error in errors.items():
        print(f"{filepath}: {error}")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
