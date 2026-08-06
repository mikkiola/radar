import os
import json
import re
import requests
from datetime import date

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "99_System", "model_config.json")
VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar"))
FEEDBACK_DIR = os.path.join(VAULT_PATH, "98_Feedback", "Infrastructure")
DOCS_URL = "https://platform.claude.com/docs/en/about-claude/models/overview"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_OWNER_ID = os.environ.get("TELEGRAM_OWNER_ID")

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def fetch_known_sonnet_ids(html_text):
    return sorted(set(re.findall(r"claude-sonnet-\d+", html_text)))

def check_for_update():
    config = load_config()
    current = config["sonnet"]
    resp = requests.get(DOCS_URL, timeout=15)
    ids_found = fetch_known_sonnet_ids(resp.text)
    if not ids_found:
        print("Список моделей не найден на странице - формат мог измениться.")
        return None
    latest = ids_found[-1]
    if latest != current:
        return {"current": current, "latest": latest}
    return None

def write_feedback(diff):
    os.makedirs(FEEDBACK_DIR, exist_ok=True)
    path = os.path.join(FEEDBACK_DIR, f"model_update_{date.today().isoformat()}.md")
    content = f"""# Feedback: обновление модели Sonnet

**Дата:** {date.today().isoformat()}
**Категория:** Infrastructure Feedback
**Severity:** MEDIUM

## Событие
Обнаружена новая версия Sonnet: {diff['latest']}.
Текущая в проде: {diff['current']}.

## Root Cause Analysis
Что произошло: Anthropic выпустил новую версию модели.
Почему не обнаружено раньше: обнаружено автоматически, штатная работа check_model_updates.py.
Что должно измениться: провести smoke-test новой модели, при успехе - обновить model_config.json вручную.

## Proposed Change
Ручное обновление sonnet в 99_System/model_config.json после проверки breaking changes в разделе обновлений на platform.claude.com.

## Status
Open
"""
    with open(path, "w") as f:
        f.write(content)
    return path

def smoke_test(model_id):
    from anthropic import Anthropic
    client = Anthropic()
    try:
        client.messages.create(
            model=model_id,
            thinking={"type": "disabled"},
            max_tokens=50,
            messages=[{"role": "user", "content": "ping"}],
        )
        return True, None
    except Exception as e:
        return False, str(e)

def notify_owner(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_OWNER_ID:
        print("Telegram не настроен, уведомление пропущено.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_OWNER_ID, "text": text}, timeout=10)

if __name__ == "__main__":
    diff = check_for_update()
    if diff:
        path = write_feedback(diff)
        notify_owner(f"Новая модель Sonnet: {diff['latest']}. Feedback создан: {path}")
        print(f"Найдена новая модель: {diff['latest']}. Feedback: {path}")
    else:
        print("Изменений нет.")
