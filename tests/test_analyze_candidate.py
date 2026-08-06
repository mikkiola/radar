import analyze


class _FakeRepos:
    def __init__(self, response=None, exc=None):
        self._response = response
        self._exc = exc

    def get(self, owner, repo):
        if self._exc:
            raise self._exc
        return self._response


class _FakeGhApi:
    def __init__(self, response=None, exc=None):
        self.repos = _FakeRepos(response, exc)


def test_gate_validated_shift_becomes_candidate():
    assert analyze.apply_quarantine_gate("VALIDATED_SHIFT") == "CANDIDATE"


def test_gate_candidate_low_confidence_unchanged():
    assert analyze.apply_quarantine_gate("CANDIDATE_LOW_CONFIDENCE") == "CANDIDATE_LOW_CONFIDENCE"


def test_confidence_label_candidate():
    assert analyze.confidence_label("CANDIDATE") == "в карантине"


def test_confidence_label_candidate_low_confidence():
    assert analyze.confidence_label("CANDIDATE_LOW_CONFIDENCE") == "низкая"


def test_check_repo_alive_archived_returns_false(monkeypatch):
    monkeypatch.setattr(analyze, "gh_api", _FakeGhApi(response={"archived": True}))
    assert analyze.check_repo_alive("owner", "repo") is False


def test_check_repo_alive_not_archived_returns_true(monkeypatch):
    monkeypatch.setattr(analyze, "gh_api", _FakeGhApi(response={"archived": False}))
    assert analyze.check_repo_alive("owner", "repo") is True


def test_check_repo_alive_api_error_returns_none(monkeypatch):
    monkeypatch.setattr(analyze, "gh_api", _FakeGhApi(exc=Exception("rate limited")))
    assert analyze.check_repo_alive("owner", "repo") is None


def test_fetch_repo_lifecycle_signal_extracts_all_fields(monkeypatch):
    response = {
        "archived": False,
        "license": {"spdx_id": "MIT"},
        "pushed_at": "2026-01-01T00:00:00Z",
        "private": False,
    }
    monkeypatch.setattr(analyze, "gh_api", _FakeGhApi(response=response))
    signal = analyze.fetch_repo_lifecycle_signal("owner", "repo")
    assert signal == {
        "archived": False,
        "license_spdx_id": "MIT",
        "pushed_at": "2026-01-01T00:00:00Z",
        "private": False,
    }


def test_fetch_repo_lifecycle_signal_missing_license_is_none(monkeypatch):
    response = {"archived": False, "pushed_at": "2026-01-01T00:00:00Z", "private": False}
    monkeypatch.setattr(analyze, "gh_api", _FakeGhApi(response=response))
    signal = analyze.fetch_repo_lifecycle_signal("owner", "repo")
    assert signal["license_spdx_id"] is None


def test_fetch_repo_lifecycle_signal_archived_true(monkeypatch):
    response = {"archived": True, "license": None, "pushed_at": "2026-01-01T00:00:00Z", "private": False}
    monkeypatch.setattr(analyze, "gh_api", _FakeGhApi(response=response))
    signal = analyze.fetch_repo_lifecycle_signal("owner", "repo")
    assert signal["archived"] is True


def test_fetch_repo_lifecycle_signal_api_error_returns_none(monkeypatch):
    monkeypatch.setattr(analyze, "gh_api", _FakeGhApi(exc=Exception("rate limited")))
    assert analyze.fetch_repo_lifecycle_signal("owner", "repo") is None
