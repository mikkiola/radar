#!/usr/bin/env python3
import os
import sys
import glob
import argparse
import requests
from anthropic import Anthropic

VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar/01_Assessments"))
PUBLISHED_LOG = os.environ.get("PUBLISHED_LOG", os.path.expanduser("~/radar/radar/99_System/published_posts.log"))
GRAPH_URL = "https://lyolich777ka.gitlab.io/opensource-radar/"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

def check_vault_path():
    if not os.path.exists(VAULT_PATH):
        print(f"ОШИБКА: vault не найден: {VAULT_PATH}")
        sys.exit(1)
    print(f"Vault найден: {VAULT_PATH}")

def load_assessment(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def is_shift_assessment(content):
    for line in content.splitlines():
        if line.startswith("**Оценка:**"):
            return "СДВИГ" in line
    return False

def get_human_correction(content):
    lines = content.splitlines()
    in_block = False
    corrections = []
    for line in lines:
        if line.strip() == "## Правка человека":
            in_block = True
            continue
        if in_block:
            if line.startswith("## "):
                break
            stripped = line.strip()
            if stripped and not stripped.startswith("<!--"):
                corrections.append(stripped)
    return "\n".join(corrections) if corrections else None

def find_latest_shift(exclude_published=True):
    check_vault_path()
    published = load_published_log() if exclude_published else set()
    pattern = os.path.join(VAULT_PATH, "*.md")
    files = sorted(glob.glob(pattern), reverse=True)
    for filepath in files:
        filename = os.path.basename(filepath)
        if filename in published:
            print(f"Пропускаю (уже опубликован): {filename}")
            continue
        content = load_assessment(filepath)
        if is_shift_assessment(content):
            print(f"Найдена оценка СДВИГ: {filename}")
            return filepath, content
    return None, None

def load_published_log():
    if not os.path.exists(PUBLISHED_LOG):
        return set()
    with open(PUBLISHED_LOG, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def mark_as_published(filename):
    os.makedirs(os.path.dirname(PUBLISHED_LOG), exist_ok=True)
    with open(PUBLISHED_LOG, "a", encoding="utf-8") as f:
        f.write(filename + "\n")
    print(f"Отмечен как опубликованный: {filename}")

SYSTEM_PROMPT = """Ты аналитик технологических сдвигов.

Твоя задача - описывать не продукт и не список функций, а то изменение в индустрии, которое произошло благодаря появлению проекта.

Пиши для технических руководителей, основателей компаний, инвесторов и инженеров одновременно.

СТРУКТУРА ОТВЕТА (строго соблюдать):

ОБЩИЙ ОБЪЁМ:
Весь пост без ссылок - максимум 650 знаков.
Если получается длиннее - сокращай абзац, а не финальную мысль.

[Название проекта] - [короткое определение через роль в экосистеме, не через функции]
[ссылка на репозиторий]

[1 абзац, максимум 3 коротких предложения, до 450 знаков]:
1. Что было до и что изменилось после.
2. Какой новый паттерн или распределение ценности он создал.

Меняет подход: [0-10]/10 - [3-5 слов]
Открывает возможности: [0-10]/10 - [3-5 слов]
Создаёт ценность: [0-10]/10 - [3-5 слов]
Приживётся на рынке: [0-10]/10 - [3-5 слов]

[Одна короткая финальная фраза, до 120 знаков]

Субъективная оценка на дату публикации.

ЗАПРЕЩЕНО:
- пересказ документации
- списки возможностей
- маркетинговые формулировки
- фразы: "позволяет", "предоставляет", "даёт возможность"
- markdown форматирование: никаких *, _, **, []()
- тяжёлые абстракции без простого объяснения: "инфраструктурный слой", "runtime", "персистентный", "архитектурная метафора"

ПЕРВАЯ ФРАЗА:
- должна описывать наблюдаемый факт
- запрещено начинать с метафор и абстракций
- запрещены формулировки: "архитектурный примитив", "новая парадигма", "трансформация экосистемы", "генеративная архитектура" и подобные
- читатель должен понять что произошло после первого предложения

СТИЛЬ:
- сначала факт, потом вывод
- конкретика важнее красивой формулировки
- если предложение нельзя пересказать другу за 10 секунд - переписать проще

ГЛАВНЫЙ ВОПРОС АНАЛИЗА:
Не "что делает этот проект?" а "как изменились разговоры, решения и архитектуры после его появления?"

Respond in Russian language only."""

def generate_post(assessment_content, human_correction=None):
    if not ANTHROPIC_API_KEY:
        print("ОШИБКА: ANTHROPIC_API_KEY не задан")
        sys.exit(1)
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    correction_note = ""
    if human_correction:
        correction_note = f"ВАЖНО: есть правка человека:\n{human_correction}\nИспользуй эту позицию - она финальная.\n"
    user_prompt = f"""Напиши пост для Telegram-канала на основе этой оценки проекта.

{correction_note}
ОЦЕНКА:
{assessment_content}

Верни только текст поста. Без пояснений."""
    print("Генерирую пост через Claude Sonnet...")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    post_text = response.content[0].text.strip()
    print(f"Пост сгенерирован ({len(post_text)} знаков)")
    return post_text

def publish_to_telegram(text):
    if not TELEGRAM_BOT_TOKEN:
        print("ОШИБКА: TELEGRAM_BOT_TOKEN не задан")
        sys.exit(1)
    if not TELEGRAM_CHANNEL_ID:
        print("ОШИБКА: TELEGRAM_CHANNEL_ID не задан")
        sys.exit(1)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    print(f"Публикую в канал {TELEGRAM_CHANNEL_ID}...")
    response = requests.post(url, json=payload, timeout=30)
    if response.status_code == 200:
        message_id = response.json()["result"]["message_id"]
        print(f"Опубликовано. Message ID: {message_id}")
        return True
    else:
        print(f"ОШИБКА Telegram API: {response.status_code}")
        print(response.text)
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Конкретный файл оценки")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--include-published", action="store_true")
    args = parser.parse_args()

    if args.file:
        check_vault_path()
        filepath = os.path.join(VAULT_PATH, args.file)
        if not os.path.exists(filepath):
            print(f"ОШИБКА: файл не найден: {filepath}")
            sys.exit(1)
        content = load_assessment(filepath)
        if not is_shift_assessment(content):
            print("ОШИБКА: оценка в файле не СДВИГ")
            sys.exit(1)
        filename = args.file
    else:
        filepath, content = find_latest_shift(exclude_published=not args.include_published)
        if not filepath:
            print("Нет новых оценок СДВИГ для публикации.")
            sys.exit(0)
        filename = os.path.basename(filepath)

    human_correction = get_human_correction(content)
    if human_correction:
        print(f"Найдена правка человека:\n{human_correction}\n")
    else:
        print("Правок человека нет - использую оценку Claude.")

    post_text = generate_post(content, human_correction)
    post_text += f"\n\nГраф: {GRAPH_URL}"
    print("\n" + "-" * 50)
    print("ПОСТ:")
    print(post_text)
    print("-" * 50)
    print(f"Знаков: {len(post_text)}")

    if args.dry_run:
        print("\n[dry-run] Публикация пропущена.")
        return

    success = publish_to_telegram(post_text)
    if success:
        mark_as_published(filename)
        print(f"\nГотово. Файл: {filename}")
    else:
        print("\nПубликация не удалась.")
        sys.exit(1)

if __name__ == "__main__":
    main()
