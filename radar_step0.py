from filter import is_relevant
import requests
import time
from datetime import datetime, timedelta

def fetch_hacker_news():
    print("\n📡 Hacker News...")
    url = "https://hn.algolia.com/api/v1/search"
    params = {"query": "open source AI agents MCP automation", "tags": "story", "hitsPerPage": 30}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        hits = r.json().get("hits", [])
        projects = []
        for h in hits:
            title = h.get("title", "")
            url_item = h.get("url", "")
            points = h.get("points", 0)
            if url_item and points > 10:
                projects.append({"title": title, "url": url_item, "score": points, "source": "HN"})
        print(f"   Найдено: {len(projects)}")
        return projects
    except Exception as e:
        print(f"   Ошибка: {e}")
        return []

def fetch_reddit():
    print("\n📡 Reddit...")
    subreddits = ["MachineLearning", "LocalLLaMA", "selfhosted"]
    projects = []
    headers = {"User-Agent": "opensource-radar/0.1"}
    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/search.json"
        params = {"q": "open source", "sort": "hot", "t": "week", "limit": 15, "restrict_sr": 1}
        try:
            r = requests.get(url, params=params, headers=headers, timeout=10)
            r.raise_for_status()
            posts = r.json().get("data", {}).get("children", [])
            for p in posts:
                d = p.get("data", {})
                title = d.get("title", "")
                link = d.get("url", "")
                score = d.get("score", 0)
                if score > 20 and ("github.com" in link or "gitlab.com" in link):
                    projects.append({"title": title, "url": link, "score": score, "source": f"Reddit/{sub}"})
            time.sleep(1)
        except Exception as e:
            print(f"   Ошибка {sub}: {e}")
    print(f"   Найдено: {len(projects)}")
    return projects

def fetch_github():
    print("\n📡 GitHub Search...")
    url = "https://api.github.com/search/repositories"
    cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    # Срез 1 — новые: молодые проекты, ранний сигнал
    new_queries = [
        f"topic:ai-agents created:>{cutoff}",
        f"topic:mcp-server created:>{cutoff}",
        f"topic:llm-tools created:>{cutoff}",
    ]

    # Срез 2 — звёздные: подтверждённые паттерны с тягой
    hot_queries = [
        "topic:ai-agents pushed:>2025-01-01 stars:>500",
        "topic:mcp-server pushed:>2025-01-01 stars:>500",
        "topic:llm-tools pushed:>2025-01-01 stars:>500",
    ]

    projects = []
    headers = {"Accept": "application/vnd.github.v3+json"}

    for q in new_queries:
        params = {
            "q": q + " is:public fork:false archived:false stars:10..500",
            "sort": "updated",
            "order": "desc",
            "per_page": 10,
        }
        try:
            r = requests.get(url, params=params, headers=headers, timeout=10)
            r.raise_for_status()
            items = r.json().get("items", [])
            for item in items:
                projects.append({
                    "title": item["full_name"],
                    "description": item.get("description", ""),
                    "url": item["html_url"],
                    "score": item["stargazers_count"],
                    "source": "GitHub/new",
                })
            time.sleep(1)
        except Exception as e:
            print(f"   Ошибка '{q}': {e}")

    for q in hot_queries:
        params = {
            "q": q + " is:public fork:false archived:false",
            "sort": "stars",
            "order": "desc",
            "per_page": 10,
        }
        try:
            r = requests.get(url, params=params, headers=headers, timeout=10)
            r.raise_for_status()
            items = r.json().get("items", [])
            for item in items:
                projects.append({
                    "title": item["full_name"],
                    "description": item.get("description", ""),
                    "url": item["html_url"],
                    "score": item["stargazers_count"],
                    "source": "GitHub/hot",
                })
            time.sleep(1)
        except Exception as e:
            print(f"   Ошибка '{q}': {e}")

    print(f"   Найдено: {len(projects)}")
    return projects

def fetch_awesome_lists():
    print("\n📡 Awesome Lists...")
    awesome_repos = [
        "punkpeye/awesome-mcp-servers",
        "e2b-dev/awesome-ai-agents",
        "Hannibal046/Awesome-LLM",
        "awesome-selfhosted/awesome-selfhosted",
    ]
    results = []
    for repo in awesome_repos:
        try:
            url = f"https://api.github.com/repos/{repo}"
            resp = requests.get(url, headers={"Accept": "application/vnd.github+json"}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                results.append({
                    "title": data.get("name", repo),
                    "description": data.get("description", ""),
                    "url": data.get("html_url", ""),
                    "score": data.get("stargazers_count", 0),
                    "topics": data.get("topics", []),
                    "source": "AwesomeList"
                })
        except Exception as e:
            print(f"   Ошибка {repo}: {e}")
    print(f"   Найдено: {len(results)}")
    return results

def deduplicate(projects):
    seen = set()
    unique = []
    for p in projects:
        url = p["url"].rstrip("/").lower()
        if url not in seen:
            seen.add(url)
            unique.append(p)
    return unique

def print_results(projects):
    print(f"\n{'='*60}")
    print(f"ИТОГО: {len(projects)} уникальных проектов")
    print(f"{'='*60}")
    projects.sort(key=lambda x: x.get("score", 0), reverse=True)
    for i, p in enumerate(projects[:30], 1):
        title = p["title"][:55]
        source = p["source"]
        score = p.get("score", 0)
        desc = p.get("description", "")[:60]
        print(f"\n{i:2}. [{source}] ★{score}")
        print(f"    {title}")
        if desc:
            print(f"    {desc}")
        print(f"    {p['url']}")

if __name__ == "__main__":
    print("🔍 Радар опенсорса — шаг 0 (без ключей)")
    print("Собираем проекты из открытых источников...")
    all_projects = []
    all_projects += fetch_hacker_news()
    all_projects += fetch_reddit()
    all_projects += fetch_github()
    all_projects += fetch_awesome_lists()
    unique = deduplicate(all_projects)
    filtered = [p for p in unique if is_relevant(p)]
    print(f"После фильтра: {len(filtered)} из {len(unique)}")
    print_results(filtered)
    print(f"\n✅ Готово.")