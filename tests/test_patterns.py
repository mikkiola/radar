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
    # read_assessments() всегда передаёт extract_shift_summary() тело файла БЕЗ frontmatter
    # (frontmatter уже отделён read_frontmatter() до вызова) - фикстура отражает это.
    content = f"""# Assessment

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
    monkeypatch.setattr(update_assessments, "ASSESSMENTS_PATH", str(tmp_path))
    monkeypatch.setattr(update_assessments, "DAYS_THRESHOLD", 0)

    assessments = update_assessments.get_old_assessments()

    assert assessments[0]["filename"] == filename
    assert assessments[0]["days_old"] == (date.today() - date(2026, 6, 24)).days


def _write_frontmatter_assessment(path, status, title="Проект"):
    content = f"""---
status: {status}
maturity_score: 5
novelty_score: 5
assertion_vector: null
evidence_log: []
root_commit_sha: null
verdict_history: []
---
# {title}

**Дата:** 2026-07-01
**Репозиторий:** https://github.com/example/repo

## What Changes in the Ecosystem
Summary text.
"""
    path.write_text(content, encoding="utf-8")


def test_read_assessments_includes_only_validated_shift(tmp_path, monkeypatch):
    assessments_path = tmp_path / "01_Assessments"
    assessments_path.mkdir()
    _write_frontmatter_assessment(assessments_path / "Shift.md", "VALIDATED_SHIFT", title="Shift Project")
    _write_frontmatter_assessment(assessments_path / "Noise.md", "REJECTED_NOISE", title="Noise Project")
    _write_frontmatter_assessment(
        assessments_path / "LowConfidence.md", "CANDIDATE_LOW_CONFIDENCE", title="Low Confidence Project"
    )
    monkeypatch.setattr(patterns, "ASSESSMENTS_PATH", str(assessments_path))

    assessments = patterns.read_assessments()

    assert {a["filename"] for a in assessments} == {"Shift.md"}


def test_read_assessments_skips_files_without_frontmatter(tmp_path, monkeypatch):
    assessments_path = tmp_path / "01_Assessments"
    assessments_path.mkdir()
    (assessments_path / "Legacy.md").write_text(
        "# Legacy\n\n**Оценка:** СДВИГ\n\n## What Changes in the Ecosystem\nOld format.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(patterns, "ASSESSMENTS_PATH", str(assessments_path))

    assert patterns.read_assessments() == []


def test_extract_source_block_reads_all_three_fields():
    content = """# Assessment

**Дата:** 2026-07-28
**Источник:**
  файл: GitHub description
  локация: не указана
  цитата: "runs entirely on your local machine"

## What Changes in the Ecosystem
Something.
"""
    assert patterns.extract_source_block(content) == {
        "file": "GitHub description",
        "location": "",
        "quote": "runs entirely on your local machine",
    }


def test_extract_source_block_missing_block_returns_empty_strings():
    content = """# Assessment

**Дата:** 2026-07-28

## What Changes in the Ecosystem
Something.
"""
    assert patterns.extract_source_block(content) == {"file": "", "location": "", "quote": ""}


def test_extract_source_block_placeholder_values_treated_as_empty():
    content = """**Источник:**
  файл: не указан
  локация: не указана
  цитата: не указана

## What Changes in the Ecosystem
"""
    assert patterns.extract_source_block(content) == {"file": "", "location": "", "quote": ""}


def test_mark_assessment_as_pattern_member_appends_backlink(tmp_path, monkeypatch):
    assessments_path = tmp_path / "01_Assessments"
    assessments_path.mkdir()
    filename = "Проект 2026-07-01.md"
    content = """# Проект

**Дата:** 2026-07-01
**Модель:** claude-haiku-4-5-20251001
**Промпт версия:** v1.0

## What Changes in the Ecosystem
Suff.
"""
    (assessments_path / filename).write_text(content, encoding="utf-8")
    monkeypatch.setattr(patterns, "ASSESSMENTS_PATH", str(assessments_path))

    result = patterns.mark_assessment_as_pattern_member(filename, "Some Pattern")

    updated = (assessments_path / filename).read_text(encoding="utf-8")
    assert result is True
    assert "**Часть паттерна:** [[Some Pattern]] (не новый сигнал - 1-е подтверждение," in updated
    # inserted right after the header metadata block, before the first heading
    assert updated.index("**Часть паттерна:**") < updated.index("## What Changes")
    assert updated.index("**Промпт версия:**") < updated.index("**Часть паттерна:**")


def test_mark_assessment_as_pattern_member_is_idempotent(tmp_path, monkeypatch):
    assessments_path = tmp_path / "01_Assessments"
    assessments_path.mkdir()
    filename = "Проект 2026-07-01.md"
    content = "**Промпт версия:** v1.0\n\n## What Changes in the Ecosystem\n"
    (assessments_path / filename).write_text(content, encoding="utf-8")
    monkeypatch.setattr(patterns, "ASSESSMENTS_PATH", str(assessments_path))

    first = patterns.mark_assessment_as_pattern_member(filename, "Some Pattern")
    second = patterns.mark_assessment_as_pattern_member(filename, "Some Pattern")

    assert first is True
    assert second is False
    updated = (assessments_path / filename).read_text(encoding="utf-8")
    assert updated.count("**Часть паттерна:** [[Some Pattern]]") == 1


def test_mark_assessment_as_pattern_member_n_grows_across_assessments(tmp_path, monkeypatch):
    assessments_path = tmp_path / "01_Assessments"
    assessments_path.mkdir()
    base_content = "**Промпт версия:** v1.0\n\n## What Changes in the Ecosystem\n"
    (assessments_path / "A.md").write_text(base_content, encoding="utf-8")
    (assessments_path / "B.md").write_text(base_content, encoding="utf-8")
    monkeypatch.setattr(patterns, "ASSESSMENTS_PATH", str(assessments_path))

    patterns.mark_assessment_as_pattern_member("A.md", "Some Pattern")
    patterns.mark_assessment_as_pattern_member("B.md", "Some Pattern")

    a_content = (assessments_path / "A.md").read_text(encoding="utf-8")
    b_content = (assessments_path / "B.md").read_text(encoding="utf-8")
    assert "1-е подтверждение" in a_content
    assert "2-е подтверждение" in b_content


def test_mark_assessment_as_pattern_member_missing_file_returns_false(tmp_path, monkeypatch):
    assessments_path = tmp_path / "01_Assessments"
    assessments_path.mkdir()
    monkeypatch.setattr(patterns, "ASSESSMENTS_PATH", str(assessments_path))

    assert patterns.mark_assessment_as_pattern_member("missing.md", "Some Pattern") is False


def test_find_dominant_pattern_picks_largest_intersection(tmp_path, monkeypatch):
    patterns_path = tmp_path / "02_Patterns"
    patterns_path.mkdir()
    (patterns_path / "Small.md").write_text("## Links\n- [[A]]\n", encoding="utf-8")
    (patterns_path / "Big.md").write_text("## Links\n- [[A]]\n- [[B]]\n- [[C]]\n", encoding="utf-8")
    monkeypatch.setattr(patterns, "PATTERNS_PATH", str(patterns_path))

    assert patterns.find_dominant_pattern({"A.md", "B.md", "C.md"}) == "Big"


def test_find_dominant_pattern_tie_breaks_alphabetically(tmp_path, monkeypatch):
    patterns_path = tmp_path / "02_Patterns"
    patterns_path.mkdir()
    # Both patterns intersect on exactly the same 2 files - a genuine tie.
    (patterns_path / "Zeta.md").write_text("## Links\n- [[A]]\n- [[B]]\n", encoding="utf-8")
    (patterns_path / "Alpha.md").write_text("## Links\n- [[A]]\n- [[B]]\n", encoding="utf-8")
    monkeypatch.setattr(patterns, "PATTERNS_PATH", str(patterns_path))

    assert patterns.find_dominant_pattern({"A.md", "B.md"}) == "Alpha"


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
