import os
import tempfile
from datetime import date, timedelta

import promote_candidates
import vault_write


def _tmp_file(days_ago, url="https://github.com/some-owner/some-repo", status="CANDIDATE"):
    tmpdir = tempfile.mkdtemp()
    filepath = os.path.join(tmpdir, "some-repo.md")
    candidate_date = (date.today() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    content = (
        "---\n"
        f"status: {status}\n"
        "verdict_history:\n"
        f"- date: '{candidate_date}'\n"
        "  verdict: CANDIDATE\n"
        "---\n"
        f"**Репозиторий:** {url}\n\n"
        "## История оценок\n"
    )
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return tmpdir, filepath


def test_too_young_skipped(monkeypatch):
    tmpdir, filepath = _tmp_file(days_ago=5)
    try:
        monkeypatch.setattr(promote_candidates, "check_repo_alive", lambda o, r: True)
        promote_candidates.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert frontmatter["status"] == "CANDIDATE"
    finally:
        os.remove(filepath)


def test_alive_promotes_to_validated_shift(monkeypatch):
    tmpdir, filepath = _tmp_file(days_ago=14)
    try:
        monkeypatch.setattr(promote_candidates, "check_repo_alive", lambda o, r: True)
        promote_candidates.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert frontmatter["status"] == "VALIDATED_SHIFT"
        assert "state_value" not in frontmatter
    finally:
        os.remove(filepath)


def test_archived_rejects_as_noise(monkeypatch):
    tmpdir, filepath = _tmp_file(days_ago=20)
    try:
        monkeypatch.setattr(promote_candidates, "check_repo_alive", lambda o, r: False)
        promote_candidates.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert frontmatter["status"] == "REJECTED_NOISE"
    finally:
        os.remove(filepath)


def test_unknown_alive_state_stays_candidate(monkeypatch):
    tmpdir, filepath = _tmp_file(days_ago=30)
    try:
        monkeypatch.setattr(promote_candidates, "check_repo_alive", lambda o, r: None)
        promote_candidates.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert frontmatter["status"] == "CANDIDATE"
    finally:
        os.remove(filepath)


def test_missing_verdict_history_skipped(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    filepath = os.path.join(tmpdir, "no-history.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("---\nstatus: CANDIDATE\n---\n**Репозиторий:** https://github.com/o/r\n\n## История оценок\n")
    try:
        monkeypatch.setattr(promote_candidates, "check_repo_alive", lambda o, r: True)
        promote_candidates.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert frontmatter["status"] == "CANDIDATE"
    finally:
        os.remove(filepath)


def test_find_candidate_files_filters_by_status(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setattr(promote_candidates, "ASSESSMENTS_PATH", tmpdir)

    candidate_path = os.path.join(tmpdir, "a-candidate.md")
    other_path = os.path.join(tmpdir, "b-validated.md")
    with open(candidate_path, "w", encoding="utf-8") as f:
        f.write("---\nstatus: CANDIDATE\n---\nТело\n")
    with open(other_path, "w", encoding="utf-8") as f:
        f.write("---\nstatus: VALIDATED_SHIFT\n---\nТело\n")

    found = promote_candidates.find_candidate_files()
    assert found == [candidate_path]
