import requests
import os
import glob
from datetime import date

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar/01_Assessments"))
PATTERNS_PATH = os.environ.get("PATTERNS_PATH", os.path.expanduser("~/radar/radar/02_Patterns"))


def get_existing_patterns():
    if not os.path.exists(PATTERNS_PATH):
        return []
    files = glob.glob(os.path.join(PATTERNS_PATH, "*.md"))
    return [os.path.splitext(os.path.basename(f))[0] for f in files]


def get_existing_assessments():
    if not os.path.exists(VAULT_PATH):
        return []
    files = glob.glob(os.path.join(VAULT_PATH, "*.md"))
    return [os.path.splitext(os.path.basename(f))[0] for f in files]


def analyze_and_save(projects):
    if not ANTHROPIC_API_KEY:
        print("ОШИБКА: ANTHROPIC_API_KEY не задан")
        return

    today = date.today().strftime("%Y-%m-%d")
    patterns = get_existing_patterns()
    assessments = get_existing_assessments()

    patterns_list = "\n".join(f"- {p}" for p in patterns) if patterns else "- паттернов пока нет"
    assessments_list = "\n".join(f"- {a}" for a in assessments[-20:]) if assessments else "- оценок пока нет"

    os.makedirs(VAULT_PATH, exist_ok=True)
    new_shifts = []

    for p in projects[:10]:
        title = p.get("title", "")
        desc = p.get("description", "")
        url = p.get("url", "")

        safe_title_tmp = title.replace("/", "-").replace(" ", "_")[:50]
        filepath_tmp = os.path.join(VAULT_PATH, f"{today} {safe_title_tmp}.md")

        if os.path.exists(filepath_tmp):
            print(f"   Пропускаем (уже существует): {safe_title_tmp}")
            continue

        prompt = f"""You are a measurement instrument for the AI and agent market ecosystem.
Respond in Russian language only.

Assess whether this opensource project represents a SHIFT or NOISE.

СДВИГ = изменение в том как организуется знание, ценность или инфраструктура в экосистеме — до того как это стало очевидным.
ШУМ = интересный инструмент, обновление продукта или популярная тема которая не меняет структуру экосистемы.

Проект: {title}
Описание: {desc}
URL: {url}

Доступные паттерны в графе (для блока СВЯЗИ):
{patterns_list}

Недавние оценки в графе (для блока СВЯЗИ):
{assessments_list}

Отвечай СТРОГО в этом формате:
НАЗВАНИЕ: [короткое русское название 3-5 слов — суть проекта, например "Браузерный агент для ИИ" или "Self-hosted автоматизация с ИИ"]
ОЦЕНКА: СДВИГ или ШУМ
УВЕРЕННОСТЬ: высокая или средняя или низкая
ЧТО_МЕНЯЕТСЯ: [2-3 предложения — что конкретно меняется в структуре экосистемы]
АРГУМЕНТАЦИЯ: [1-2 предложения почему такая оценка]
ЕСЛИ_ПРАВА: [одно конкретное наблюдаемое событие через 12 месяцев которое подтвердит оценку]
ЕСЛИ_ОШИБЛАСЬ: [одно конкретное наблюдаемое событие через 12 месяцев которое опровергнет оценку]
СВЯЗИ: [перечисли через запятую названия паттернов и оценок из списков выше которые связаны с этим проектом. Если ничего не подходит — оставь пустым]"""

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY.strip(),
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 800,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )

            if response.status_code != 200:
                print(f"   Ошибка API для {title}: {response.status_code} — {response.text[:100]}")
                continue

            text = response.json()["content"][0]["text"]

            lines = {}
            for line in text.strip().split("\n"):
                if ": " in line:
                    key, val = line.split(": ", 1)
                    lines[key.strip()] = val.strip()

            ru_name = lines.get("НАЗВАНИЕ", safe_title_tmp)
            ocenka = lines.get("ОЦЕНКА", "ШУМ")
            uverennost = lines.get("УВЕРЕННОСТЬ", "низкая")
            chto = lines.get("ЧТО_МЕНЯЕТСЯ", "")
            arg = lines.get("АРГУМЕНТАЦИЯ", "")
            esli_prava = lines.get("ЕСЛИ_ПРАВА", "")
            esli_oshiblas = lines.get("ЕСЛИ_ОШИБЛАСЬ", "")
            svyazi_raw = lines.get("СВЯЗИ", "")

            svyazi_block = ""
            if svyazi_raw and svyazi_raw.strip():
                items = [s.strip() for s in svyazi_raw.split(",") if s.strip()]
                for item in items:
                    if item in patterns or any(item in a for a in assessments):
                        svyazi_block += f"- [[{item}]]\n"

            safe_ru = ru_name.replace(" ", "_").replace("/", "-")[:50]
            filename = f"{safe_ru} {today}.md"
            filepath = os.path.join(VAULT_PATH, filename)

            if os.path.exists(filepath):
                print(f"   Пропускаем (уже существует): {filename}")
                continue

            content = f"""# {ru_name}

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

## Оценка Claude
- {today} — {ocenka}: первая оценка автоматически

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] — [твоя оценка]: [почему] -->

## История оценок
- {today} — {ocenka}: первая оценка

## Связи
{svyazi_block}"""

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"   {ocenka} ({uverennost}) — {ru_name}")

            if ocenka == "СДВИГ":
                new_shifts.append(ru_name)

        except Exception as e:
            print(f"   Ошибка {title}: {e}")

    # Уведомление в личку при новых СДВИГ оценках
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    owner_id = os.environ.get("TELEGRAM_OWNER_ID")
    if new_shifts and bot_token and owner_id:
        msg = "🔴 Новые СДВИГ оценки:\n" + "\n".join(f"• {name}" for name in new_shifts)
        try:
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": owner_id, "text": msg},
                timeout=10
            )
            print(f"Уведомление отправлено: {len(new_shifts)} СДВИГ")
        except Exception as e:
            print(f"Ошибка отправки уведомления: {e}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from radar_step0 import fetch_hacker_news, fetch_github, fetch_awesome_lists, deduplicate
    from filter import is_relevant

    print("Собираем проекты...")
    all_projects = []
    all_projects += fetch_hacker_news()
    all_projects += fetch_github()
    all_projects += fetch_awesome_lists()

    unique = deduplicate(all_projects)
    filtered = [p for p in unique if is_relevant(p)]
    print(f"После фильтра: {len(filtered)} проектов")

    print("Анализируем через Claude...")
    analyze_and_save(filtered)
    print("\nГотово.")