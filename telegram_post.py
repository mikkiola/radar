#!/usr/bin/env python3
"""
telegram_post.py — публикация поста из оценки СДВИГ в Telegram канал

Использование:
  python3 telegram_post.py                        # берёт последнюю оценку СДВИГ
  python3 telegram_post.py --file "имя-файла.md" # берёт конкретный файл
  python3 telegram_post.py --dry-run              # генерирует пост без публикации

Переменные окружения:
  ANTHROPIC_API_KEY  — ключ Claude API (обязательно)
  TELEGRAM_BOT_TOKEN — токен бота (обязательно)
  TELEGRAM_CHANNEL_ID — ID или @username канала (обязательно)
"""

import os
import sys
import glob
import argparse
import requests
from datetime import datetime
from anthropic import Anthropic

# ─── Конфигурация ─────────────────────────────────────────────────────────────

VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar/01_Assessments"))
PUBLISHED_LOG = os.environ.get("PUBLISHED_LOG", os.path.expanduser("~/radar/radar/99_System/published_posts.log"))

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")

# ─── Чтение файлов оценок ─────────────────────────────────────────────────────

def check_vault_path():
    """Проверить что vault существует перед любой работой с файлами."""
    if not os.path.exists(VAULT_PATH):
        print(f"ОШИБКА: vault не найден: {VAULT_PATH}")
        print("Проверь путь. Vault должен быть в ~/radar/radar/01_Assessments/")
        sys.exit(1)
    print(f"Vault найден: {VAULT_PATH}")


def load_assessment(filepath):
    """Загрузить файл оценки и вернуть текст."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def is_shift_assessment(content):
    """Проверить что оценка — СДВИГ (не ШУМ)."""
    # Ищем строку с оценкой в шапке файла
    for line in content.splitlines():
        if line.startswith("**Оценка:**"):
            return "СДВИГ" in line
    return False


def get_human_correction(content):
    """
    Извлечь правку человека из блока ## Правка человека.
    Возвращает строку с правкой или None если правки нет.
    """
    lines = content.splitlines()
    in_block = False
    corrections = []

    for line in lines:
        if line.strip() == "## Правка человека":
            in_block = True
            continue
        if in_block:
            # Следующий заголовок — конец блока
            if line.startswith("## "):
                break
            # Пропускаем HTML-комментарии и пустые строки
            stripped = line.strip()
            if stripped and not stripped.startswith("<!--"):
                corrections.append(stripped)

    return "\n".join(corrections) if corrections else None


def find_latest_shift(exclude_published=True):
    """
    Найти самый свежий файл с оценкой СДВИГ.
    Если exclude_published=True — пропускать уже опубликованные.
    """
    check_vault_path()

    published = load_published_log() if exclude_published else set()

    # Берём все .md файлы, сортируем по дате в имени (YYYY-MM-DD в начале)
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
    """Загрузить лог опубликованных постов."""
    if not os.path.exists(PUBLISHED_LOG):
        return set()
    with open(PUBLISHED_LOG, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def mark_as_published(filename):
    """Добавить файл в лог опубликованных."""
    os.makedirs(os.path.dirname(PUBLISHED_LOG), exist_ok=True)
    with open(PUBLISHED_LOG, "a", encoding="utf-8") as f:
        f.write(filename + "\n")
    print(f"Отмечен как опубликованный: {filename}")


# ─── Генерация поста через Claude Sonnet ──────────────────────────────────────

SYSTEM_PROMPT = """Ты редактор Telegram-канала «Публичный радар архитектора».

Владелец канала — Ольга, архитектор знаний. Она пишет от первого лица.

ГОЛОС КАНАЛА:
- Прямой. Утверждение, не вопрос.
- Без вводных фраз. Сразу суть.
- Без объяснений для широкой аудитории.
- Без CTA и призывов к действию.
- Без эмодзи-маркеров списков.
- Длина: 300–800 знаков.

СТРУКТУРА ПОСТА:
1. Утверждение-сдвиг — одна строка
2. Что именно меняется — 2-4 предложения конкретно
3. Почему важно сейчас — 1-2 предложения
4. Один вывод — не совет, зафиксированная точка

ЗАПРЕЩЕНО:
- "в современном мире", "в эпоху X", "на сегодняшний день"
- "безусловно", "несомненно", "очевидно", "важно отметить"
- "данный", "осуществлять", "реализовывать", "обеспечивать"
- списки из трёх ровных пунктов
- пассивный залог где можно активный
- вводные предложения без информации

МЕТРИКА: хороший пост через год выглядит как предсказание, не как новость.

Respond in Russian language only."""


def generate_post(assessment_content, human_correction=None):
    """
    Сгенерировать пост из файла оценки через Claude Sonnet.
    Если есть правка человека — использовать её как основу.
    """
    if not ANTHROPIC_API_KEY:
        print("ОШИБКА: ANTHROPIC_API_KEY не задан")
        sys.exit(1)

    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    correction_note = ""
    if human_correction:
        correction_note = f"""
ВАЖНО: Ольга добавила правку в блок "Правка человека":
{human_correction}

Используй её позицию, а не оценку Claude — она финальная.
"""

    user_prompt = f"""Напиши пост для Telegram-канала на основе этой оценки опенсорс-проекта.

{correction_note}
ОЦЕНКА:
{assessment_content}

Пост должен:
- начинаться с конкретного утверждения о сдвиге в экосистеме
- объяснять что именно меняется (конкретно, без абстракций)
- заканчиваться одним выводом — зафиксированной точкой, не рекомендацией
- быть написан от первого лица (Ольга)
- укладываться в 300–800 знаков

Верни только текст поста. Без пояснений."""

    print("Генерирую пост через Claude Sonnet...")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    post_text = response.content[0].text.strip()
    print(f"Пост сгенерирован ({len(post_text)} знаков)")
    return post_text


# ─── Публикация в Telegram ─────────────────────────────────────────────────────

def publish_to_telegram(text):
    """Опубликовать пост в Telegram канал через Bot API."""
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
    }

    print(f"Публикую в канал {TELEGRAM_CHANNEL_ID}...")
    response = requests.post(url, json=payload, timeout=30)

    if response.status_code == 200:
        result = response.json()
        message_id = result["result"]["message_id"]
        print(f"Опубликовано. Message ID: {message_id}")
        return True
    else:
        print(f"ОШИБКА Telegram API: {response.status_code}")
        print(response.text)
        return False


# ─── Точка входа ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Публикация поста из оценки СДВИГ в Telegram канал"
    )
    parser.add_argument(
        "--file",
        help="Конкретный файл оценки из 01_Assessments/ (только имя файла)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Сгенерировать пост без публикации в Telegram",
    )
    parser.add_argument(
        "--include-published",
        action="store_true",
        help="Не пропускать уже опубликованные файлы",
    )
    args = parser.parse_args()

    # ── Шаг 1: Получить файл оценки ──
    if args.file:
        check_vault_path()
        filepath = os.path.join(VAULT_PATH, args.file)
        if not os.path.exists(filepath):
            print(f"ОШИБКА: файл не найден: {filepath}")
            sys.exit(1)
        content = load_assessment(filepath)
        if not is_shift_assessment(content):
            print(f"ОШИБКА: оценка в файле не СДВИГ")
            print("Используй --file только с файлами где **Оценка:** СДВИГ")
            sys.exit(1)
        filename = args.file
    else:
        filepath, content = find_latest_shift(
            exclude_published=not args.include_published
        )
        if not filepath:
            print("Нет новых оценок СДВИГ для публикации.")
            print("Все файлы уже опубликованы или оценок СДВИГ нет.")
            sys.exit(0)
        filename = os.path.basename(filepath)

    # ── Шаг 2: Проверить правку человека ──
    human_correction = get_human_correction(content)
    if human_correction:
        print(f"Найдена правка человека:\n{human_correction}\n")
    else:
        print("Правок человека нет — использую оценку Claude.")

    # ── Шаг 3: Сгенерировать пост ──
    post_text = generate_post(content, human_correction)

    print("\n" + "─" * 50)
    print("ПОСТ:")
    print(post_text)
    print("─" * 50)
    print(f"Знаков: {len(post_text)}")

    # ── Шаг 4: Опубликовать или dry-run ──
    if args.dry_run:
        print("\n[dry-run] Публикация пропущена.")
        return

    success = publish_to_telegram(post_text)

    if success:
        mark_as_published(filename)
        print(f"\nГотово. Файл: {filename}")
    else:
        print("\nПубликация не удалась. Файл не помечен как опубликованный.")
        sys.exit(1)


if __name__ == "__main__":
    main()
