#!/usr/bin/env python3
"""
fetch_analysts.py - загрузка и структурирование данных внешних аналитиков (Layer 4)

Что делает:
1. Перебирает EXTERNAL_ANALYSTS
2. Для каждого вызывает соответствующий парсер
3. Извлекает структурированные claims через Claude Haiku
4. Сохраняет файл в 04_Analysts/
"""

import os
import re
import json
import argparse
import requests
import anthropic
from datetime import datetime, timedelta

EXTERNAL_ANALYSTS = [
    {
        "name": "Builder Radar",
        "url": "https://buttondown.com/Builder-Radar/archive",
        "parser": "parse_buttondown",
        "weight": 0.8,
        "cadence": "weekly",
    },
    # Future:
    # {"name": "Simon Willison", ..., "weight": 1.0, "cadence": "daily"},
    # {"name": "Latent Space",   ..., "weight": 0.9, "cadence": "weekly"},
    # {"name": "Ben Evans",      ..., "weight": 0.9, "cadence": "weekly"},
]

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def parse_buttondown(analyst):
    """Найти последний выпуск Builder Radar на Buttondown, вернуть dict с date/url/text."""
    archive_url = analyst["url"]
    headers = {"User-Agent": "Mozilla/5.0 (compatible; radar-bot/1.0)"}

    try:
        r = requests.get(archive_url, headers=headers, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"[fetch_analysts] ошибка загрузки архива {archive_url}: {e}")
        return None

    html = r.text

    # Ищем ссылки на выпуски
    links = re.findall(
        r'href="(https://buttondown\.com/Builder-Radar/archive/[^"/]+/?)"', html
    )
    if not links:
        print(f"[fetch_analysts] ссылки на выпуски не найдены в {archive_url}")
        return None

    # Дедупликация, берём первую (самую свежую)
    seen = set()
    unique_links = []
    for link in links:
        link = link.rstrip("/")
        if link not in seen:
            seen.add(link)
            unique_links.append(link)

    issue_url = unique_links[0]

    try:
        r2 = requests.get(issue_url, headers=headers, timeout=15)
        r2.raise_for_status()
    except Exception as e:
        print(f"[fetch_analysts] ошибка загрузки выпуска {issue_url}: {e}")
        return None

    issue_html = r2.text

    # Ищем дату в формате YYYY-MM-DD
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', issue_html)
    if date_match:
        issue_date = date_match.group(1)
    else:
        month_match = re.search(
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',
            issue_html,
        )
        if month_match:
            try:
                issue_date = datetime.strptime(month_match.group(0), "%B %d, %Y").strftime("%Y-%m-%d")
            except Exception:
                issue_date = datetime.now().strftime("%Y-%m-%d")
        else:
            issue_date = datetime.now().strftime("%Y-%m-%d")

    # Очищаем HTML от тегов и скриптов
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', issue_html, flags=re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&#\d+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = text[:8000]

    return {"date": issue_date, "url": issue_url, "text": text}


def extract_claims_via_haiku(text, issue_date):
    """Извлечь структурированные claims из текста аналитика через Claude Haiku."""
    verification_horizon = (
        datetime.strptime(issue_date, "%Y-%m-%d") + timedelta(days=180)
    ).strftime("%Y-%m-%d")

    prompt = f"""Extract claims from this analyst report.
For each claim return JSON:
{{
  "thesis": "one sentence",
  "confidence": "high/medium/low",
  "evidence": ["evidence 1", "evidence 2"],
  "verification_horizon": "{verification_horizon}"
}}
Respond in Russian language only.
Return only JSON array, no markdown.

Report text:
{text}"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = re.sub(r'^```\w*\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw)

    try:
        claims = json.loads(raw.strip())
        if not isinstance(claims, list):
            claims = []
    except json.JSONDecodeError:
        print(f"[fetch_analysts] не удалось разобрать JSON claims: {raw[:200]}")
        claims = []

    return claims


def build_analyst_file(analyst, issue_date, issue_url, claims):
    """Сформировать markdown-файл аналитика."""
    name = analyst["name"]
    weight = analyst["weight"]

    lines = [
        f"# {name} | {issue_date}",
        "",
        f"**Источник:** {issue_url}",
        f"**Дата выпуска:** {issue_date}",
        f"**Аналитик:** {name}",
        f"**Вес доверия:** {weight}",
        "",
        "## Claims",
        "",
    ]

    for i, claim in enumerate(claims, 1):
        thesis = claim.get("thesis", "")
        confidence = claim.get("confidence", "")
        evidence = claim.get("evidence", [])
        horizon = claim.get("verification_horizon", "")

        lines.append(f"### Claim {i}")
        lines.append(f"**Тезис:** {thesis}")
        lines.append(f"**Уверенность:** {confidence}")
        lines.append("**Доказательства:**")
        for ev in evidence:
            lines.append(f"- {ev}")
        lines.append(f"**Горизонт проверки:** {horizon}")
        lines.append("**Статус:** не проверен")
        lines.append("")

    lines.append("## External-only signals")
    lines.append("[паттерны которые видит аналитик но которых нет в нашем vault на эту дату]")
    lines.append("")
    lines.append("## Совпадения с нашими паттернами")
    lines.append("[заполняется автоматически в patterns.py]")
    lines.append("")

    return "\n".join(lines)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--vault",
        default=os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar")),
    )
    args = arg_parser.parse_args()

    vault_path = args.vault
    analysts_path = os.path.join(vault_path, "04_Analysts")
    os.makedirs(analysts_path, exist_ok=True)

    print(f"[fetch_analysts] vault: {vault_path}")

    parsers = {
        "parse_buttondown": parse_buttondown,
    }

    for analyst in EXTERNAL_ANALYSTS:
        name = analyst["name"]
        parser_name = analyst["parser"]
        print(f"[fetch_analysts] обрабатываю: {name}")

        parse_fn = parsers.get(parser_name)
        if not parse_fn:
            print(f"[fetch_analysts] неизвестный парсер: {parser_name}")
            continue

        result = parse_fn(analyst)
        if not result:
            print(f"[fetch_analysts] выпуск не найден для {name}, пропускаю")
            continue

        issue_date = result["date"]
        issue_url = result["url"]
        text = result["text"]

        safe_name = re.sub(r'[/\\:*?"<>| ]', "_", name)
        filename = f"{safe_name}_{issue_date}.md"
        filepath = os.path.join(analysts_path, filename)

        if os.path.exists(filepath):
            print(f"[fetch_analysts] уже существует: {filename}")
            continue

        print(f"[fetch_analysts] извлекаю claims через Haiku...")
        claims = extract_claims_via_haiku(text, issue_date)
        print(f"[fetch_analysts] claims: {len(claims)}")

        content = build_analyst_file(analyst, issue_date, issue_url, claims)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[fetch_analysts] сохранён: {filename}")

    print("[fetch_analysts] готово")


if __name__ == "__main__":
    main()
