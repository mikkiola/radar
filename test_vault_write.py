import os
import tempfile

import vault_write


def _write_tmp(content):
    fd, path = tempfile.mkstemp(suffix=".md")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def _new_tmp_path():
    tmpdir = tempfile.mkdtemp()
    return os.path.join(tmpdir, "new_assessment.md")


def test_append_event_is_pure_no_file_io():
    frontmatter = {"evidence_log": []}
    result = vault_write.append_event(frontmatter, "state_transition", state_value="Growing", state_confidence="low")
    assert result is frontmatter
    assert not os.path.exists("/tmp/append_event_should_never_write_here.md")


def test_append_event_schema():
    frontmatter = {}
    vault_write.append_event(frontmatter, "state_transition", state_value="Growing", state_confidence="low")
    assert len(frontmatter["evidence_log"]) == 1
    event = frontmatter["evidence_log"][0]
    assert event["event_type"] == "state_transition"
    assert event["state_value"] == "Growing"
    assert event["state_confidence"] == "low"
    assert "date" in event


def test_append_event_accumulates():
    frontmatter = {}
    vault_write.append_event(frontmatter, "state_transition", state_value="Prototype", state_confidence="low")
    vault_write.append_event(frontmatter, "state_transition", state_value="Growing", state_confidence="high")
    assert len(frontmatter["evidence_log"]) == 2
    assert frontmatter["evidence_log"][0]["state_value"] == "Prototype"
    assert frontmatter["evidence_log"][1]["state_value"] == "Growing"


def test_write_verdict_entry_state_value_none_leaves_evidence_log_untouched():
    path = _write_tmp("---\nstatus: CANDIDATE_LOW_CONFIDENCE\nevidence_log: []\n---\n## История оценок\n")
    try:
        written = vault_write.write_verdict_entry(path, "VALIDATED_SHIFT", "- подтверждено")
        assert written is True
        frontmatter, _ = vault_write.read_frontmatter(path)
        assert frontmatter["evidence_log"] == []
        assert "state_value" not in frontmatter
        assert "state_confidence" not in frontmatter
    finally:
        os.remove(path)


def test_write_verdict_entry_new_file_state_value_low_confidence():
    path = _new_tmp_path()
    try:
        extra_frontmatter = {"maturity_score": 3, "novelty_score": 4, "evidence_log": []}
        body_template = "# Test\n\n## История оценок\n"
        written = vault_write.write_verdict_entry(
            path, "VALIDATED_SHIFT", "- первая оценка",
            extra_frontmatter=extra_frontmatter, body_template=body_template,
            state_value="Growing",
        )
        assert written is True
        frontmatter, _ = vault_write.read_frontmatter(path)
        assert frontmatter["state_value"] == "Growing"
        assert frontmatter["state_confidence"] == "low"
        assert len(frontmatter["evidence_log"]) == 1
        assert frontmatter["evidence_log"][0]["event_type"] == "state_transition"
    finally:
        os.remove(path)


def test_write_verdict_entry_existing_evidence_gives_high_confidence():
    content = (
        "---\n"
        "status: VALIDATED_SHIFT\n"
        "evidence_log:\n"
        "  - date: '2026-01-01'\n"
        "    event_type: state_transition\n"
        "    state_value: Prototype\n"
        "    state_confidence: low\n"
        "---\n"
        "## История оценок\n"
    )
    path = _write_tmp(content)
    try:
        written = vault_write.write_verdict_entry(
            path, "VALIDATED_SHIFT", "- переоценка", state_value="Growing",
        )
        assert written is True
        frontmatter, _ = vault_write.read_frontmatter(path)
        assert frontmatter["state_value"] == "Growing"
        assert frontmatter["state_confidence"] == "high"
        assert len(frontmatter["evidence_log"]) == 2
        assert frontmatter["evidence_log"][1]["state_value"] == "Growing"
    finally:
        os.remove(path)


def test_canonical_field_order_places_state_between_novelty_and_assertion():
    order = vault_write.CANONICAL_FIELD_ORDER
    assert order.index("novelty_score") < order.index("state_value") < order.index("assertion_vector")
    assert order.index("state_value") < order.index("state_confidence") < order.index("assertion_vector")
