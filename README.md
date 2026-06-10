# Публичный радар

Измерительный прибор агентного и ИИ-рынка. Каждый день собирает opensource-проекты, оценивает их через Claude и публикует сдвиги в Telegram-канале [@radar_public](https://t.me/radar_public).

## Что делает

Система автоматически:
- собирает проекты из GitHub Trending, Hacker News, Awesome Lists
- фильтрует нерелевантное (игры, иконки, чеклисты)
- оценивает каждый проект через Claude Haiku — СДВИГ или ШУМ
- сохраняет оценки в Obsidian vault с фальсифицируемыми гипотезами
- генерирует посты через Claude Sonnet и публикует в Telegram

Центр системы — граф знаний, не канал. Telegram — публичный интерфейс исследования.

## Быстрый старт

```bash
git clone https://gitlab.com/lyolich777ka/opensource-radar.git
cd opensource-radar
pip install anthropic requests

ANTHROPIC_API_KEY="ключ" python3 radar_step0.py
```

## Скрипты

| Скрипт | Что делает |
|---|---|
| `radar_step0.py` | Сбор проектов из HN / GitHub / Awesome Lists + фильтр |
| `filter.py` | Тематический фильтр (AI / MCP / LLM / автоматизация) |
| `analyze.py` | Оценка проектов через Claude Haiku, запись в vault |
| `update_assessments.py` | Обновление оценок старше 30 дней |
| `telegram_post.py` | Генерация поста через Claude Sonnet и публикация в канал |

## Архитектура

```
GitHub / HN / Awesome Lists
        ↓
radar_step0.py + filter.py     — сбор и фильтрация
        ↓
analyze.py                     — оценка через Claude Haiku
        ↓
vault/01_Assessments/          — файлы оценок с гипотезами
        ↓
HITL: проверка человеком       — блок "Правка человека" в каждом файле
        ↓
telegram_post.py               — пост через Claude Sonnet → @radar_public
```

## Переменные окружения

| Переменная | Где взять |
|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com |
| `TELEGRAM_BOT_TOKEN` | @BotFather в Telegram |
| `TELEGRAM_CHANNEL_ID` | @username канала |

## Vault с оценками

Оценки проектов хранятся в ветке `vault`:
[gitlab.com/lyolich777ka/opensource-radar/-/tree/vault/01_Assessments](https://gitlab.com/lyolich777ka/opensource-radar/-/tree/vault/01_Assessments)

## CI/CD

GitLab CI запускает радар каждый день в 12:00 по Хошимину (Asia/Bangkok).

---

Версия: 1.0 | Обновлено: 10.06.2026
