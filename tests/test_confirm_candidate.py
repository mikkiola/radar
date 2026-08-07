import os
import tempfile

import pytest

import confirm_candidate
import vault_write


def _tmp_vault_with_file(content):
    tmpdir = tempfile.mkdtemp()
    filepath = os.path.join(tmpdir, "some-repo.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return tmpdir, filepath


def _run(vault_path, repo, decision, monkeypatch):
    monkeypatch.setattr(confirm_candidate, "ASSESSMENTS_PATH", vault_path)
    monkeypatch.setenv("CONFIRM_REPO", repo)
    monkeypatch.setenv("CONFIRM_DECISION", decision)


def test_path_traversal_slash_rejected(monkeypatch):
    _run("01_Assessments", "../etc/passwd", "approve", monkeypatch)
    with pytest.raises(SystemExit) as exc:
        confirm_candidate.main()
    assert exc.value.code == 1


def test_path_traversal_dotdot_rejected(monkeypatch):
    _run("01_Assessments", "..", "approve", monkeypatch)
    with pytest.raises(SystemExit) as exc:
        confirm_candidate.main()
    assert exc.value.code == 1


def test_empty_repo_rejected(monkeypatch):
    _run("01_Assessments", "", "approve", monkeypatch)
    with pytest.raises(SystemExit) as exc:
        confirm_candidate.main()
    assert exc.value.code == 1


def test_invalid_decision_rejected(monkeypatch):
    tmpdir, filepath = _tmp_vault_with_file("---\nstatus: CANDIDATE_LOW_CONFIDENCE\n---\nТело\n")
    try:
        _run(tmpdir, "some-repo", "maybe", monkeypatch)
        with pytest.raises(SystemExit) as exc:
            confirm_candidate.main()
        assert exc.value.code == 1
    finally:
        os.remove(filepath)


def test_missing_file_rejected(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    _run(tmpdir, "no-such-repo", "approve", monkeypatch)
    with pytest.raises(SystemExit) as exc:
        confirm_candidate.main()
    assert exc.value.code == 1


def test_wrong_current_status_rejected(monkeypatch):
    tmpdir, filepath = _tmp_vault_with_file("---\nstatus: VALIDATED_SHIFT\n---\nТело\n")
    try:
        _run(tmpdir, "some-repo", "approve", monkeypatch)
        with pytest.raises(SystemExit) as exc:
            confirm_candidate.main()
        assert exc.value.code == 1
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert frontmatter["status"] == "VALIDATED_SHIFT"
    finally:
        os.remove(filepath)


def test_approve_happy_path(monkeypatch):
    tmpdir, filepath = _tmp_vault_with_file(
        "---\nstatus: CANDIDATE_LOW_CONFIDENCE\n---\n## История оценок\n"
    )
    try:
        _run(tmpdir, "some-repo", "approve", monkeypatch)
        confirm_candidate.main()
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert frontmatter["status"] == "VALIDATED_SHIFT"
        assert "state_value" not in frontmatter
    finally:
        os.remove(filepath)


def test_reject_happy_path(monkeypatch):
    tmpdir, filepath = _tmp_vault_with_file(
        "---\nstatus: CANDIDATE_LOW_CONFIDENCE\n---\n## История оценок\n"
    )
    try:
        _run(tmpdir, "some-repo", "reject", monkeypatch)
        confirm_candidate.main()
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert frontmatter["status"] == "REJECTED_NOISE"
    finally:
        os.remove(filepath)
