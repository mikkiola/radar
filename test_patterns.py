import os
from datetime import date
from types import SimpleNamespace

import pytest

import patterns
import update_assessments


def test_valid_json_passes_through_unchanged():
    assert patterns.parse_llm_json('{"clusters": [], "orphans": []}') == {
        "clusters": [], "orphans": []
    }


def test_truncated_mid_second_cluster_is_repaired():
    result = patterns.parse_llm_json(
        '{"clusters": [{"name": "Первый"}, {"name": "Второй"'
    )

    assert result == {"clusters": [{"name": "Первый"}]}
    assert result.repair_used is True


@pytest.mark.parametrize(
    "raw",
    [
        '{"clusters": [{"name": "Первый"',
        '{"clusters": [{"name":',
    ],
)
def test_no_complete_cluster_cannot_be_repaired(raw):
    with pytest.raises(patterns.UnrecoverableJSONError):
        patterns.parse_llm_json(raw)


def test_malformed_json_after_complete_cluster_recovers_prefix():
    result = patterns.parse_llm_json('{"clusters": [{"name": "Первый"},]}')

    assert result == {"clusters": [{"name": "Первый"}]}
    assert result.repair_used is True


def test_markdown_code_fence_is_removed():
    assert patterns.parse_llm_json('```json\n{"clusters": []}\n```') == {"clusters": []}


def test_brackets_and_escaped_quotes_inside_strings_do_not_confuse_repair():
    result = patterns.parse_llm_json(
        r'{"clusters": [{"description": "Скобки { } [ ] и \"кавычки\""}, {"name": "обрезан"'
    )

    assert result == {
        "clusters": [{"description": 'Скобки { } [ ] и "кавычки"'}]
    }


def test_nested_arrays_and_objects_repair_correctly():
    result = patterns.parse_llm_json(
        '{"clusters": [{"name": "Первый", "assessment_files": ["a.md"], '
        '"evidence": [{"source": "repo"}]}, {"name": "Второй"'
    )

    assert result == {
        "clusters": [{
            "name": "Первый",
            "assessment_files": ["a.md"],
            "evidence": [{"source": "repo"}],
        }]
    }


def test_truncation_inside_open_string_repairs_previous_cluster():
    result = patterns.parse_llm_json(
        '{"clusters": [{"name": "Первый"}, {"name": "Незакрытая строка'
    )

    assert result == {"clusters": [{"name": "Первый"}]}


def test_non_dict_top_level_is_unrecoverable():
    with pytest.raises(patterns.UnrecoverableJSONError):
        patterns.parse_llm_json('[]')


@pytest.mark.parametrize(
    ("heading", "summary"),
    [
        ("## Что меняется в экосистеме", "Русская суть сдвига."),
        ("## What Changes in the Ecosystem", "English shift summary."),
    ],
)
def test_extract_shift_summary_recognizes_both_heading_variants(heading, summary):
    content = f"""# Assessment

**Оценка:** СДВИГ

{heading}
{summary}

## Reasoning
Ignored.
"""

    assert patterns.extract_shift_summary(content) == summary


@pytest.mark.parametrize(
    ("right_heading", "wrong_heading", "right", "wrong"),
    [
        ("## Если права", "## Если ошиблась", "Рост", "Спад"),
        ("## If Right", "## If Wrong", "Growth", "Decline"),
    ],
)
def test_extract_pattern_hypotheses_recognizes_both_heading_variants(
    right_heading, wrong_heading, right, wrong
):
    content = f"""{right_heading}
{right}

{wrong_heading}
{wrong}
"""

    assert patterns.extract_pattern_hypotheses(content) == (right, wrong)


def test_get_old_assessments_parses_trailing_filename_date(tmp_path, monkeypatch):
    filename = "Some Title 2026-06-24.md"
    (tmp_path / filename).write_text("# Assessment", encoding="utf-8")
    monkeypatch.setattr(update_assessments, "VAULT_PATH", str(tmp_path))
    monkeypatch.setattr(update_assessments, "DAYS_THRESHOLD", 0)

    assessments = update_assessments.get_old_assessments()

    assert assessments[0]["filename"] == filename
    assert assessments[0]["days_old"] == (date.today() - date(2026, 6, 24)).days


def test_falsify_missing_reasoning_does_not_modify_pattern(tmp_path, monkeypatch):
    patterns_path = tmp_path / "02_Patterns"
    archive_path = tmp_path / "03_Archive"
    patterns_path.mkdir()
    archive_path.mkdir()
    pattern_path = patterns_path / "Паттерн.md"
    pattern_content = """# Паттерн

**Создан:** 2026-01-01 (автоматически, patterns.py)
**Статус:** АКТИВНЫЙ

## Если права
Рост

## Если ошиблась
Спад
"""
    pattern_path.write_text(pattern_content, encoding="utf-8")

    response = SimpleNamespace(
        content=[SimpleNamespace(text='{"verdict": "ОПРОВЕРГНУТ"}')],
        stop_reason="end_turn",
    )
    monkeypatch.setattr(
        patterns,
        "client",
        SimpleNamespace(messages=SimpleNamespace(create=lambda **kwargs: response)),
    )
    monkeypatch.setattr(patterns, "ARCHIVE_PATH", str(archive_path))
    monkeypatch.setattr(patterns, "send_telegram", lambda text: None)

    with pytest.raises(patterns.UnrecoverableJSONError):
        patterns.falsify_pattern(
            str(pattern_path),
            pattern_content,
            [{"title": "Новый сигнал", "date": "2026-02-01", "content": "Сдвиг"}],
        )

    assert pattern_path.read_text(encoding="utf-8") == pattern_content
    assert not os.listdir(archive_path)
