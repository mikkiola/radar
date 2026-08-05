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
