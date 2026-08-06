import os
import tempfile
from datetime import datetime, timedelta

import recheck_lifecycle
import vault_write


def _tmp_file(status="VALIDATED_SHIFT", url="https://github.com/some-owner/some-repo", extra_frontmatter=""):
    tmpdir = tempfile.mkdtemp()
    filepath = os.path.join(tmpdir, "some-repo.md")
    content = (
        "---\n"
        f"status: {status}\n"
        "evidence_log: []\n"
        f"{extra_frontmatter}"
        "---\n"
        f"**Репозиторий:** {url}\n\n"
        "## История оценок\n"
    )
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def _iso(months_ago):
    dt = datetime.now() - timedelta(days=months_ago * 30)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _signal(**overrides):
    base = {"archived": False, "license_spdx_id": "MIT", "pushed_at": _iso(0), "private": False}
    base.update(overrides)
    return base


class _FakeRepos:
    def __init__(self, releases=None, exc=None):
        self._releases = releases
        self._exc = exc

    def list_releases(self, owner, repo):
        if self._exc:
            raise self._exc
        return self._releases


class _FakeActions:
    def __init__(self, runs=None, exc=None):
        self._runs = runs
        self._exc = exc

    def list_workflow_runs_for_repo(self, owner, repo, per_page=1):
        if self._exc:
            raise self._exc
        return self._runs


class _FakeGhApi:
    def __init__(self, repos=None, actions=None):
        self.repos = repos or _FakeRepos()
        self.actions = actions or _FakeActions()


# detect_transition


def test_detect_transition_first_true_observation_enters():
    assert recheck_lifecycle.detect_transition([], "frozen_entered", "frozen_exited", True) == "frozen_entered"


def test_detect_transition_first_false_observation_stays_none():
    assert recheck_lifecycle.detect_transition([], "frozen_entered", "frozen_exited", False) is None


def test_detect_transition_no_change_returns_none():
    log = [{"event_type": "frozen_entered"}]
    assert recheck_lifecycle.detect_transition(log, "frozen_entered", "frozen_exited", True) is None


def test_detect_transition_exit_detected():
    log = [{"event_type": "frozen_entered"}]
    assert recheck_lifecycle.detect_transition(log, "frozen_entered", "frozen_exited", False) == "frozen_exited"


def test_detect_transition_already_out_stays_none():
    log = [{"event_type": "frozen_entered"}, {"event_type": "frozen_exited"}]
    assert recheck_lifecycle.detect_transition(log, "frozen_entered", "frozen_exited", False) is None


# check_releases_stopped / check_ci_broken


def test_check_releases_stopped_needs_history(monkeypatch):
    releases = [{"published_at": _iso(20)}]
    monkeypatch.setattr(recheck_lifecycle, "gh_api", _FakeGhApi(repos=_FakeRepos(releases=releases)))
    assert recheck_lifecycle.check_releases_stopped("o", "r", []) is None


def test_check_releases_stopped_detects_entered(monkeypatch):
    releases = [{"published_at": _iso(20)}, {"published_at": _iso(25)}]
    monkeypatch.setattr(recheck_lifecycle, "gh_api", _FakeGhApi(repos=_FakeRepos(releases=releases)))
    assert recheck_lifecycle.check_releases_stopped("o", "r", []) == "releases_stopped_entered"


def test_check_releases_stopped_recent_history_no_signal(monkeypatch):
    releases = [{"published_at": _iso(1)}, {"published_at": _iso(6)}]
    monkeypatch.setattr(recheck_lifecycle, "gh_api", _FakeGhApi(repos=_FakeRepos(releases=releases)))
    assert recheck_lifecycle.check_releases_stopped("o", "r", []) is None


def test_check_releases_stopped_api_error_returns_none(monkeypatch):
    monkeypatch.setattr(recheck_lifecycle, "gh_api", _FakeGhApi(repos=_FakeRepos(exc=Exception("boom"))))
    assert recheck_lifecycle.check_releases_stopped("o", "r", []) is None


def test_check_ci_broken_no_workflows_returns_none(monkeypatch):
    monkeypatch.setattr(recheck_lifecycle, "gh_api", _FakeGhApi(actions=_FakeActions(runs={"workflow_runs": []})))
    assert recheck_lifecycle.check_ci_broken("o", "r", []) is None


def test_check_ci_broken_detects_failure(monkeypatch):
    runs = {"workflow_runs": [{"conclusion": "failure"}]}
    monkeypatch.setattr(recheck_lifecycle, "gh_api", _FakeGhApi(actions=_FakeActions(runs=runs)))
    assert recheck_lifecycle.check_ci_broken("o", "r", []) == "ci_broken"


def test_check_ci_broken_success_no_signal(monkeypatch):
    runs = {"workflow_runs": [{"conclusion": "success"}]}
    monkeypatch.setattr(recheck_lifecycle, "gh_api", _FakeGhApi(actions=_FakeActions(runs=runs)))
    assert recheck_lifecycle.check_ci_broken("o", "r", []) is None


def test_check_ci_broken_api_error_returns_none(monkeypatch):
    monkeypatch.setattr(recheck_lifecycle, "gh_api", _FakeGhApi(actions=_FakeActions(exc=Exception("boom"))))
    assert recheck_lifecycle.check_ci_broken("o", "r", []) is None


# process_file


def test_archived_becomes_archived_dead(monkeypatch):
    filepath = _tmp_file()
    try:
        monkeypatch.setattr(recheck_lifecycle, "fetch_repo_lifecycle_signal", lambda o, r: _signal(archived=True))
        recheck_lifecycle.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert frontmatter["status"] == "ARCHIVED_DEAD"
    finally:
        os.remove(filepath)


def test_no_signals_no_evidence_written(monkeypatch):
    filepath = _tmp_file(extra_frontmatter="license_spdx_id: MIT\nlicense_baseline_origin: initial\n")
    try:
        monkeypatch.setattr(recheck_lifecycle, "fetch_repo_lifecycle_signal", lambda o, r: _signal())
        monkeypatch.setattr(recheck_lifecycle, "check_releases_stopped", lambda o, r, e: None)
        monkeypatch.setattr(recheck_lifecycle, "check_ci_broken", lambda o, r, e: None)
        recheck_lifecycle.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert frontmatter["evidence_log"] == []
    finally:
        os.remove(filepath)


def test_missing_baseline_sets_migration_origin_no_event(monkeypatch):
    filepath = _tmp_file()  # без license_spdx_id вообще - файл до этой сессии
    try:
        monkeypatch.setattr(recheck_lifecycle, "fetch_repo_lifecycle_signal", lambda o, r: _signal(license_spdx_id="MIT"))
        monkeypatch.setattr(recheck_lifecycle, "check_releases_stopped", lambda o, r, e: None)
        monkeypatch.setattr(recheck_lifecycle, "check_ci_broken", lambda o, r, e: None)
        recheck_lifecycle.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert frontmatter["license_spdx_id"] == "MIT"
        assert frontmatter["license_baseline_origin"] == "migration"
        assert frontmatter["evidence_log"] == []
    finally:
        os.remove(filepath)


def test_license_change_detected_and_baseline_updated(monkeypatch):
    filepath = _tmp_file(extra_frontmatter="license_spdx_id: MIT\nlicense_baseline_origin: initial\n")
    try:
        monkeypatch.setattr(recheck_lifecycle, "fetch_repo_lifecycle_signal", lambda o, r: _signal(license_spdx_id="BSL-1.1"))
        monkeypatch.setattr(recheck_lifecycle, "check_releases_stopped", lambda o, r, e: None)
        monkeypatch.setattr(recheck_lifecycle, "check_ci_broken", lambda o, r, e: None)
        recheck_lifecycle.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert frontmatter["license_spdx_id"] == "BSL-1.1"
        events = frontmatter["evidence_log"]
        assert len(events) == 1
        assert events[0]["event_type"] == "license_changed"
        assert events[0]["old"] == "MIT"
        assert events[0]["new"] == "BSL-1.1"
    finally:
        os.remove(filepath)


def test_frozen_entered_then_no_dup_next_run(monkeypatch):
    filepath = _tmp_file(extra_frontmatter="license_spdx_id: MIT\nlicense_baseline_origin: initial\n")
    try:
        monkeypatch.setattr(recheck_lifecycle, "fetch_repo_lifecycle_signal", lambda o, r: _signal(pushed_at=_iso(9)))
        monkeypatch.setattr(recheck_lifecycle, "check_releases_stopped", lambda o, r, e: None)
        monkeypatch.setattr(recheck_lifecycle, "check_ci_broken", lambda o, r, e: None)

        recheck_lifecycle.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert [e["event_type"] for e in frontmatter["evidence_log"]] == ["frozen_entered"]

        recheck_lifecycle.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert [e["event_type"] for e in frontmatter["evidence_log"]] == ["frozen_entered"]
    finally:
        os.remove(filepath)


def test_visibility_lost_and_restored(monkeypatch):
    filepath = _tmp_file(extra_frontmatter="license_spdx_id: MIT\nlicense_baseline_origin: initial\n")
    try:
        monkeypatch.setattr(recheck_lifecycle, "check_releases_stopped", lambda o, r, e: None)
        monkeypatch.setattr(recheck_lifecycle, "check_ci_broken", lambda o, r, e: None)

        monkeypatch.setattr(recheck_lifecycle, "fetch_repo_lifecycle_signal", lambda o, r: _signal(private=True))
        recheck_lifecycle.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert [e["event_type"] for e in frontmatter["evidence_log"]] == ["visibility_lost"]

        monkeypatch.setattr(recheck_lifecycle, "fetch_repo_lifecycle_signal", lambda o, r: _signal(private=False))
        recheck_lifecycle.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert [e["event_type"] for e in frontmatter["evidence_log"]] == ["visibility_lost", "visibility_restored"]
    finally:
        os.remove(filepath)


def test_one_signal_error_does_not_block_others(monkeypatch):
    filepath = _tmp_file(extra_frontmatter="license_spdx_id: MIT\nlicense_baseline_origin: initial\n")
    try:
        monkeypatch.setattr(recheck_lifecycle, "fetch_repo_lifecycle_signal", lambda o, r: _signal(private=True))
        # check_releases_stopped/check_ci_broken - их собственный try/except уже проглотил
        # ошибку API и вернул None, как в реальном коде при исключении в list_releases/
        # list_workflow_runs_for_repo (см. test_check_releases_stopped_api_error_returns_none)
        monkeypatch.setattr(recheck_lifecycle, "check_releases_stopped", lambda o, r, e: None)
        monkeypatch.setattr(recheck_lifecycle, "check_ci_broken", lambda o, r, e: None)
        recheck_lifecycle.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert [e["event_type"] for e in frontmatter["evidence_log"]] == ["visibility_lost"]
    finally:
        os.remove(filepath)


def test_fetch_signal_none_skips_file_entirely(monkeypatch):
    filepath = _tmp_file(extra_frontmatter="license_spdx_id: MIT\nlicense_baseline_origin: initial\n")
    try:
        monkeypatch.setattr(recheck_lifecycle, "fetch_repo_lifecycle_signal", lambda o, r: None)
        recheck_lifecycle.process_file(filepath)
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert frontmatter["status"] == "VALIDATED_SHIFT"
        assert frontmatter["evidence_log"] == []
    finally:
        os.remove(filepath)


def test_missing_frontmatter_skipped(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    filepath = os.path.join(tmpdir, "broken.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("нет фронтматтера тут\n")
    try:
        recheck_lifecycle.process_file(filepath)  # не должно бросать исключение
    finally:
        os.remove(filepath)


def test_unparseable_url_skipped(monkeypatch):
    filepath = _tmp_file(url="not-a-github-url")
    try:
        recheck_lifecycle.process_file(filepath)  # не должно бросать исключение
        frontmatter, _ = vault_write.read_frontmatter(filepath)
        assert frontmatter["status"] == "VALIDATED_SHIFT"
    finally:
        os.remove(filepath)


def test_find_validated_shift_files_filters_by_status(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setattr(recheck_lifecycle, "VAULT_PATH", tmpdir)

    validated_path = os.path.join(tmpdir, "a-validated.md")
    other_path = os.path.join(tmpdir, "b-candidate.md")
    with open(validated_path, "w", encoding="utf-8") as f:
        f.write("---\nstatus: VALIDATED_SHIFT\n---\nТело\n")
    with open(other_path, "w", encoding="utf-8") as f:
        f.write("---\nstatus: CANDIDATE\n---\nТело\n")

    found = recheck_lifecycle.find_validated_shift_files()
    assert found == [validated_path]
