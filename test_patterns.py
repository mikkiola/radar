import os
from types import SimpleNamespace

import pytest

import patterns


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
