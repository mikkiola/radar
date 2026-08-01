import re

from scorecard import check_scorecard, OK, NO_DATA, UNAVAILABLE

metrics = {"score_missing": 0, "score_timeout": 0}

GITHUB_URL_RE = re.compile(r"^https?://github\.com/([^/]+)/([^/]+?)/?$")

FORKS_STARS_MIN_RATIO = 0.03
WATCHERS_STARS_MIN_RATIO = 0.01

BOT_PATTERN_RE = re.compile(
    r"\[bot\]|dependabot|renovate|github-actions|semantic-release",
    re.IGNORECASE,
)

INCLUDE_TOPICS = [
    "ai", "agent", "agents", "mcp", "llm", "llmops",
    "automation", "workflow", "rag", "knowledge",
    "self-hosted", "infrastructure", "developer-tools",
    "openai", "anthropic", "langchain", "vector-database"
]

EXCLUDE_TOPICS = [
    "game", "games", "todo", "portfolio", "personal-website",
    "css", "ui-components", "icons", "wallpaper", "music",
    "frontend-checklist", "template"
]

EXCLUDE_WORDS = [
    "checklist", "wallpaper", "icon", "music", "player",
    "game", "portfolio", "template", "tutorial", "course",
    "beginner", "awesome-list"
]

def is_relevant(project):
    title = project.get("title", "").lower()
    description = project.get("description", "").lower()
    topics = [t.lower() for t in project.get("topics", [])]

    for word in EXCLUDE_WORDS:
        if word in title:
            return False

    for topic in topics:
        if topic in EXCLUDE_TOPICS:
            return False

    text = title + " " + description
    for keyword in INCLUDE_TOPICS:
        if keyword in text or keyword in topics:
            return True

    return False

def passes_traction_filter(project):
    stars = project.get("score") or 0
    forks = project.get("forks_count")
    watchers = project.get("watchers_count")
    recent_commits = project.get("recent_commits")

    if not stars or forks is None or watchers is None:
        return False

    if forks / stars < FORKS_STARS_MIN_RATIO:
        return False

    if watchers / stars < WATCHERS_STARS_MIN_RATIO:
        return False

    for commit_text in recent_commits or []:
        if BOT_PATTERN_RE.search(commit_text):
            return False

    return True

def passes_filter(project):
    match = GITHUB_URL_RE.match(project.get("url", "") or "")
    if not match:
        return is_relevant(project)

    owner, repo = match.group(1), match.group(2)
    result = check_scorecard(owner, repo)

    if result.status == OK:
        return result.passes()

    if result.status == NO_DATA:
        metrics["score_missing"] += 1
    elif result.status == UNAVAILABLE:
        metrics["score_timeout"] += 1

    return passes_traction_filter(project)
