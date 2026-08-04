import requests
import os
import json
import re
from datetime import date, datetime
from vault_language import is_english_body

import vault_write

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar/01_Assessments"))
DAYS_THRESHOLD = 30
MODEL_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "99_System", "model_config.json")

VERDICT_TO_STATUS = {
    "СДВИГ": "VALIDATED_SHIFT",
    "ШУМ": "REJECTED_NOISE",
}

VALID_STATE_VALUES = {
    "Prototype", "Growing", "Mature", "Maintenance", "Declining", "Archived", "Spam",
}


def _map_state_value(state_raw):
    """Отобразить сырой STATE-текст от LLM в state_value для write_verdict_entry().
    Пустая строка (STATE line отсутствует вовсе) -> None - нет данных, признак,
    что LLM не ответил на этот вопрос. Непустая, но не входящая в
    VALID_STATE_VALUES -> "invalid" - LLM ответил, но неверным значением, что
    диагностически отличимо от отсутствия данных (позволяет позже посчитать,
    как часто LLM промахивается с этой классификацией)."""
    if state_raw in VALID_STATE_VALUES:
        return state_raw
    if state_raw:
        return "invalid"
    return None


def load_model_config():
    with open(MODEL_CONFIG_PATH) as f:
        return json.load(f)


MODEL_CONFIG = load_model_config()


def get_old_assessments():
    """Находим оценки старше 30 дней."""
    today = date.today()
    old_files = []

    if not os.path.exists(VAULT_PATH):
        print(f"   Vault не найден: {VAULT_PATH}")
        return []

    for filename in os.listdir(VAULT_PATH):
        if not filename.endswith(".md"):
            continue
        try:
            match = re.search(r"(\d{4}-\d{2}-\d{2})\.md$", filename)
            file_date = datetime.strptime(match.group(1), "%Y-%m-%d").date() if match else None
            if file_date is None:
                continue
            days_old = (today - file_date).days
            if days_old >= DAYS_THRESHOLD:
                old_files.append({
                    "filename": filename,
                    "filepath": os.path.join(VAULT_PATH, filename),
                    "days_old": days_old
                })
        except Exception:
            continue

    return old_files


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


def update_assessment(filepath, filename, days_old):
    """Читаем файл и просим Claude обновить оценку с учётом мнения Ольги.
    Пишем через write_verdict_entry() - если новый вердикт отличается от текущего status,
    статус не флипается напрямую, а уходит в CANDIDATE_LOW_CONFIDENCE (карантин, ждёт
    второго подтверждения человеком - Фаза 3)."""
    frontmatter, body = vault_write.read_frontmatter(filepath)
    if frontmatter is None:
        print(f"   ОШИБКА: {filename} без frontmatter, пропускаю переоценку")
        return

    current_status = frontmatter.get("status")
    today = date.today().strftime("%Y-%m-%d")
    response_language = "English" if is_english_body(body) else "Russian"

    # Читаем мнение Ольги если есть
    opinion = read_owner_opinion(filepath)
    opinion_context = (
        f"\nМнение владельца радара об этом проекте:\n{opinion}\n"
        if opinion else ""
    )

    prompt = f"""Ты - измерительный прибор агентного и ИИ-рынка.
Respond in {response_language}. Write ОБНОВЛЕНИЕ in {response_language}.

Ниже оценка opensource-проекта сделанная {days_old} дней назад.
Твоя задача: оценить актуальность гипотезы на сегодня.
{opinion_context}
{body}

Отвечай СТРОГО в этом формате:
ОЦЕНКА: СДВИГ или ШУМ (может измениться или остаться)
ИЗМЕНЕНИЕ: подтверждается или опровергается или без изменений
STATE: Prototype, Growing, Mature, Maintenance, Declining, Archived или Spam - lifecycle TREND (momentum) репозитория с момента последней проверки, НЕ повтор ОЦЕНКИ другими словами - растёт ли активность/принятие или падает, а не "СДВИГ это или ШУМ"
ОБНОВЛЕНИЕ: [2-3 предложения - что произошло в экосистеме за это время что влияет на оценку. Если есть мнение владельца - учти его в анализе]"""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": MODEL_CONFIG["haiku"],
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )

        if response.status_code != 200:
            print(f"   Ошибка API: {response.status_code}")
            return

        text = response.json()["content"][0]["text"]

        lines = {}
        for line in text.strip().split("\n"):
            if ": " in line:
                key, val = line.split(": ", 1)
                lines[key.strip()] = val.strip()

        ocenka = lines.get("ОЦЕНКА", "")
        izmenenie = lines.get("ИЗМЕНЕНИЕ", "")
        obnovlenie = lines.get("ОБНОВЛЕНИЕ", "")
        state_raw = lines.get("STATE", "")

        if ocenka not in VERDICT_TO_STATUS or izmenenie not in {"подтверждается", "опровергается", "без изменений"}:
            print(f"   Неожиданные ОЦЕНКА/ИЗМЕНЕНИЕ для {filename}: {ocenka!r}/{izmenenie!r}")
            return

        state_value = _map_state_value(state_raw)
        if state_value == "invalid":
            print(f"   Неожиданный STATE для {filename}: {state_raw!r} - recheck пишется с state_value=invalid")

        new_mapped_status = VERDICT_TO_STATUS[ocenka]
        final_status = new_mapped_status if new_mapped_status == current_status else "CANDIDATE_LOW_CONFIDENCE"

        opinion_note = " [с учётом мнения Ольги]" if opinion else ""
        narrative_line = f"- {today} - {ocenka} ({izmenenie}){opinion_note}: {obnovlenie}"

        written = vault_write.write_verdict_entry(filepath, final_status, narrative_line, state_value=state_value)
        if not written:
            print(f"   ОШИБКА записи: {filename}")
            return

        flip_note = f" [status: {current_status} -> {final_status}]" if final_status != current_status else ""
        print(f"   {ocenka} ({izmenenie}){opinion_note} - {filename}{flip_note}")

    except Exception as e:
        print(f"   Ошибка {filename}: {e}")


if __name__ == "__main__":
    print("Ищем оценки старше 30 дней...")
    old_files = get_old_assessments()

    if not old_files:
        print(f"   Нет оценок старше {DAYS_THRESHOLD} дней.")
    else:
        print(f"   Найдено: {len(old_files)} файлов для обновления")
        for f in old_files:
            update_assessment(f["filepath"], f["filename"], f["days_old"])

    print("\nГотово.")
