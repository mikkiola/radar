import requests
import os
import glob
import json
from datetime import date

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar/01_Assessments"))
PATTERNS_PATH = os.environ.get("PATTERNS_PATH", os.path.expanduser("~/radar/radar/02_Patterns"))
MODEL_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "99_System", "model_config.json")
PROMPT_VERSION = "v1.0"


def load_model_config():
    with open(MODEL_CONFIG_PATH) as f:
        return json.load(f)


MODEL_CONFIG = load_model_config()


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


def get_assessed_urls():
    """Возвращает множество URL из уже существующих файлов оценок."""
    assessed = set()
    if not os.path.exists(VAULT_PATH):
        return assessed
    for f in glob.glob(os.path.join(VAULT_PATH, "*.md")):
        try:
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("**Репозиторий:**"):
                        url = line.split("**Репозиторий:**", 1)[1].strip()
                        if url:
                            assessed.add(url)
                        break
        except Exception:
            pass
    return assessed


def read_owner_opinion(filepath):
    """Читает блок Мнение Ольги из файла оценки. Возвращает текст или None."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        start_marker = "## Мнение Ольги"
        end_marker = "## История оценок"

        start = content.find(start_marker)
        end = content.find(end_marker)

        if start == -1 or end == -1:
            return None

        block = content[start + len(start_marker):end].strip()

        # Если блок содержит только комментарий-подсказку - пропускаем
        if not block or block.startswith("<!--"):
            return None

        return block
    except Exception:
        return None


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
    assessed_urls = get_assessed_urls()
    new_shifts = []

    for p in projects[:10]:
        title = p.get("title", "")
        desc = p.get("description", "")
        url = p.get("url", "")

        if url in assessed_urls:
            print(f"   Пропускаем (URL уже в vault): {title[:40]}")
            continue

        prompt = f"""You are a measurement instrument for the AI and agent market ecosystem.
Respond in English.

Assess whether this opensource project represents a SHIFT or NOISE.

СДВИГ = изменение в том как организуется знание, ценность или инфраструктура в экосистеме - до того как это стало очевидным.
ШУМ = интересный инструмент, обновление продукта или популярная тема которая не меняет структуру экосистемы.

Проект: {title}
Описание: {desc}
URL: {url}

Доступные паттерны в графе (для блока СВЯЗИ):
{patterns_list}

Недавние оценки в графе (для блока СВЯЗИ):
{assessments_list}

Перед тем как поставить ОЦЕНКА: СДВИГ, явно проверь: это новый протокол? новый стандарт? новый слой архитектуры? новый способ рыночного взаимодействия? Если ответ "нет" на все четыре вопроса и это качественная реализация уже известного - это ШУМ, а не СДВИГ.

Требование к источнику: ИСТОЧНИК_ЦИТАТА должна быть точной подстрокой из текста "Описание" или "Проект" выше - никогда не придумывай файл, путь или номер строк, которых тебе не давали. Если в "Описание" и "Проект" нет ничего, что стоит процитировать, оставь ИСТОЧНИК_ФАЙЛ и ИСТОЧНИК_ЦИТАТА пустыми.

Отвечай СТРОГО в этом формате:
НАЗВАНИЕ: [short English name, 3-5 words, describing the project essence]
ОЦЕНКА: СДВИГ или ШУМ
УВЕРЕННОСТЬ: высокая или средняя или низкая
ЧТО_МЕНЯЕТСЯ: [2-3 English sentences - what specifically changes in the ecosystem structure]
АРГУМЕНТАЦИЯ: [1-2 English sentences explaining the assessment]
ЕСЛИ_ПРАВА: [one specific observable event in 12 months that confirms the assessment, in English]
ЕСЛИ_ОШИБЛАСЬ: [one specific observable event in 12 months that refutes the assessment, in English]
СВЯЗИ: [перечисли через запятую от 3 до 5 наиболее связанных паттернов и оценок из списков выше. Предпочитай заполнить 3-5 связей. Оставляй пустым только если действительно нет ни одной осмысленной связи]
ИСТОЧНИК_ФАЙЛ: [GitHub description, или HN title, или пусто если нечего процитировать]
ИСТОЧНИК_ЛОКАЦИЯ: [обычно пусто - у короткого описания нет номеров строк]
ИСТОЧНИК_ЦИТАТА: [точная подстрока из "Описание" или "Проект" выше, на языке оригинала, без перевода; пусто если нечего процитировать]"""

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY.strip(),
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": MODEL_CONFIG["haiku"],
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )

            if response.status_code != 200:
                print(f"   Ошибка API для {title}: {response.status_code} - {response.text[:100]}")
                continue

            text = response.json()["content"][0]["text"]

            lines = {}
            for line in text.strip().split("\n"):
                if ": " in line:
                    key, val = line.split(": ", 1)
                    lines[key.strip()] = val.strip()

            ru_name = lines.get("НАЗВАНИЕ", title[:50])
            ocenka = lines.get("ОЦЕНКА", "ШУМ")
            uverennost = lines.get("УВЕРЕННОСТЬ", "низкая")
            chto = lines.get("ЧТО_МЕНЯЕТСЯ", "")
            arg = lines.get("АРГУМЕНТАЦИЯ", "")
            esli_prava = lines.get("ЕСЛИ_ПРАВА", "")
            esli_oshiblas = lines.get("ЕСЛИ_ОШИБЛАСЬ", "")
            svyazi_raw = lines.get("СВЯЗИ", "")
            istochnik_fayl = lines.get("ИСТОЧНИК_ФАЙЛ", "").strip()
            istochnik_lokatsiya = lines.get("ИСТОЧНИК_ЛОКАЦИЯ", "").strip()
            istochnik_tsitata = lines.get("ИСТОЧНИК_ЦИТАТА", "").strip()

            if uverennost not in {"высокая", "средняя", "низкая"}:
                print(f"   Неожиданное значение УВЕРЕННОСТЬ: {uverennost!r}, использую 'низкая'")
                uverennost = "низкая"

            if ocenka != "СДВИГ":
                print(f"   {ocenka} ({uverennost}) - {ru_name[:40]} - пропускаем")
                continue

            svyazi_block = ""
            if svyazi_raw and svyazi_raw.strip():
                items = [s.strip() for s in svyazi_raw.split(",") if s.strip()]
                for item in items:
                    if item in patterns:
                        svyazi_block += f"- [[{item}]]\n"
                        continue
                    matched_assessment = next((a for a in assessments if item in a), None)
                    if matched_assessment:
                        svyazi_block += f"- [[{matched_assessment.replace('.md', '')}]]\n"

            safe_ru = ru_name.replace(" ", "_").replace("/", "-")[:50]
            filename = f"{safe_ru} {today}.md"
            filepath = os.path.join(VAULT_PATH, filename)

            if os.path.exists(filepath):
                print(f"   Пропускаем (файл существует): {filename}")
                continue

            content = f"""# {ru_name}

**Дата:** {today}
**Репозиторий:** {url}
**Оценка:** {ocenka}
**Уверенность:** {uverennost}
**Модель:** {MODEL_CONFIG["haiku"]}
**Промпт версия:** {PROMPT_VERSION}
**Источник:**
  файл: {istochnik_fayl if istochnik_fayl else "не указан"}
  локация: {istochnik_lokatsiya if istochnik_lokatsiya else "не указана"}
  цитата: {f'"{istochnik_tsitata}"' if istochnik_tsitata else "не указана"}

## What Changes in the Ecosystem
{chto}

## Reasoning
{arg}

## Falsifiable Hypothesis
**Если права:** {esli_prava}
**Если ошиблась:** {esli_oshiblas}

## Оценка Claude
- {today} - {ocenka}: первая оценка автоматически

## Правка человека
<!-- Не согласна с Claude? Добавь строку: - [дата] - [твоя оценка]: [почему] -->

## Мнение Ольги
<!-- Свободная рефлексия: контекст, ощущение, аналогии. Читается Claude при следующей переоценке. -->

## История оценок
- {today} - {ocenka}: первая оценка

## Связи
{svyazi_block}"""

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"   СДВИГ ({uverennost}) - {ru_name}")
            new_shifts.append(ru_name)

        except Exception as e:
            print(f"   Ошибка {title}: {e}")

    # Уведомление в личку при новых СДВИГ оценках
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    owner_id = os.environ.get("TELEGRAM_OWNER_ID")
    if new_shifts and bot_token and owner_id:
        msg = "Новые СДВИГ оценки:\n" + "\n".join(f"- {name}" for name in new_shifts)
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
