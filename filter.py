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
