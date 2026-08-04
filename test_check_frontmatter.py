import os
import tempfile

import check_frontmatter


def _write_tmp(content):
    fd, path = tempfile.mkstemp(suffix=".md")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def test_file_without_frontmatter_is_error():
    path = _write_tmp("# Просто markdown без frontmatter\n")
    try:
        assert check_frontmatter.validate_file(path) is not None
    finally:
        os.remove(path)


def test_file_with_broken_yaml_is_error():
    path = _write_tmp("---\nstatus: [unclosed\n---\nТело\n")
    try:
        assert check_frontmatter.validate_file(path) is not None
    finally:
        os.remove(path)


def test_file_with_status_outside_enum_is_error():
    path = _write_tmp("---\nstatus: NOT_A_REAL_STATUS\n---\nТело\n")
    try:
        assert check_frontmatter.validate_file(path) is not None
    finally:
        os.remove(path)


def test_file_with_valid_status_is_none():
    path = _write_tmp("---\nstatus: VALIDATED_SHIFT\n---\nТело\n")
    try:
        assert check_frontmatter.validate_file(path) is None
    finally:
        os.remove(path)


def test_validate_paths_returns_only_invalid():
    valid = _write_tmp("---\nstatus: CANDIDATE\n---\nТело\n")
    invalid = _write_tmp("# Без frontmatter\n")
    try:
        errors = check_frontmatter.validate_paths([valid, invalid])
        assert list(errors.keys()) == [invalid]
    finally:
        os.remove(valid)
        os.remove(invalid)
