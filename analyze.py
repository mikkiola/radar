import requests
import os
from datetime import date

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
VAULT_PATH = os.path.expanduser("~/radar/01_Assessments")

def analyze_and_save(projects):
    today = date.today().strftime("%Y-%m-%d")
    
    for p in projects[:5]:
        title = p.get("title", "")
        desc = p.get("description", "")
        url = p.get("url", "")
        
        prompt = f"""You are a measurement instrument for the AI and agent market ecosystem.
Respond in Russian language only.

Assess whether this opensource project represents a SHIFT or NOISE.

СДВИГ = изменение в том как организуется знание, ценность или инфраструктура в экосистеме — до того как это стало очевидным.
ШУМ = интересный инструмент, обновление продукта или популярная тема которая не меняет структуру экосистемы.

Проект: {title}
Описание: {desc}
URL: {url}

Отвечай СТРОГО в этом формате:
ОЦЕНКА: СДВИГ или ШУМ
УВЕРЕННОСТЬ: высокая или средняя или низкая
ЧТО_МЕНЯЕТСЯ: [2-3 предложения — что конкретно меняется в структуре экосистемы]
АРГУМЕНТАЦИЯ: [1-2 предложения почему такая оценка]
ЕСЛИ_ПРАВА: [одно конкретное наблюдаемое событие через 12 месяцев которое подтвердит оценку]
ЕСЛИ_ОШИБЛАСЬ: [одно конкретное наблюдаемое событие через 12 месяцев которое опровергнет оценку]"""

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 600,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"   Ошибка API для {title}: {response.status_code}")
                continue
                
            text = response.json()["content"][0]["text"]
            
            lines = {}
            for line in text.strip().split("\n"):
                if ": " in line:
                    key, val = line.split(": ", 1)
                    lines[key.strip()] = val.strip()
            
            ocenka = lines.get("ОЦЕНКА", "ШУМ")
            uverennost = lines.get("УВЕРЕННОСТЬ", "низкая")
            chto = lines.get("ЧТО_МЕНЯЕТСЯ", "")
            arg = lines.get("АРГУМЕНТАЦИЯ", "")
            esli_prava = lines.get("ЕСЛИ_ПРАВА", "")
            esli_oshiblas = lines.get("ЕСЛИ_ОШИБЛАСЬ", "")
            
            safe_title = title.replace("/", "-").replace(" ", "_")[:50]
            filename = f"{today} {safe_title}.md"
            filepath = os.path.join(VAULT_PATH, filename)
            
            content = f"""# Оценка: {title}

**Дата:** {today}
**Репозиторий:** {url}
**Оценка:** {ocenka}
**Уверенность:** {uverennost}

## Что меняется в экосистеме
{chto}

## Аргументация
{arg}

## Фальсифицируемая гипотеза
**Если права:** {esli_prava}
**Если ошиблась:** {esli_oshiblas}

## История оценок
- {today} — {ocenka}: первая оценка

## Связи
"""
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"   {ocenka} ({uverennost}) — {title}")
            
        except Exception as e:
            print(f"   Ошибка {title}: {e}")

if __name__ == "__main__":
    test_projects = [
        {"title": "github/github-mcp-server", "description": "GitHub's official MCP Server", "url": "https://github.com/github/github-mcp-server"},
        {"title": "browser-use/browser-use", "description": "Make websites accessible for AI agents", "url": "https://github.com/browser-use/browser-use"},
        {"title": "n8n-io/n8n", "description": "Fair-code workflow automation platform with native AI capabilities", "url": "https://github.com/n8n-io/n8n"},
    ]
    print("Тестируем обновлённый промпт...")
    analyze_and_save(test_projects)
    print("\nГотово. Проверь 01_Assessments в Obsidian.")
