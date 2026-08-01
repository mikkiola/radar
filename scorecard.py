import requests

SCORECARD_MIN_SCORE = 4
SCORECARD_API_URL = "https://api.securityscorecards.dev/projects/github.com/{owner}/{repo}"

OK = "OK"
NO_DATA = "NO_DATA"
UNAVAILABLE = "UNAVAILABLE"


class ScorecardResult:
    def __init__(self, status, score=None):
        self.status = status
        self.score = score

    def passes(self):
        return self.status == OK and self.score >= SCORECARD_MIN_SCORE

    def __repr__(self):
        return f"ScorecardResult(status={self.status!r}, score={self.score!r})"


def check_scorecard(owner, repo):
    url = SCORECARD_API_URL.format(owner=owner, repo=repo)
    try:
        r = requests.get(url, timeout=10)
    except requests.exceptions.RequestException:
        return ScorecardResult(UNAVAILABLE)

    if r.status_code == 404:
        return ScorecardResult(NO_DATA)

    if r.status_code >= 500:
        return ScorecardResult(UNAVAILABLE)

    if r.status_code != 200:
        return ScorecardResult(UNAVAILABLE)

    score = r.json().get("score")
    if score is None:
        return ScorecardResult(NO_DATA)

    return ScorecardResult(OK, score)
