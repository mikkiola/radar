import requests
import os
import json
from datetime import date, datetime

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar/01_Assessments"))
DAYS_THRESHOLD = 30
MODEL_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "99_System", "model_config.json")


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
            date_str = filename[:10]
            file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
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
    """Читаем файл и просим Claude обновить оценку с учётом мнения Ольги."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    today = date.today().strftime("%Y-%m-%d")

    # Читаем мнение Ольги если есть
    opinion = read_owner_opinion(filepath)
    opinion_context = (
        f"\nМнение владельца радара об этом проекте:\n{opinion}\n"
        if opinion else ""
    )

    prompt = f"""Ты - измерительный прибор агентного и ИИ-рынка.
Respond in Russian language only.

Ниже оценка opensource-проекта сделанная {days_old} дней назад.
Твоя задача: оценить актуальность гипотезы на сегодня.
{opinion_context}
{content}

Отвечай СТРОГО в этом формате:
ОЦЕНКА: СДВИГ или ШУМ (может измениться или остаться)
ИЗМЕНЕНИЕ: подтверждается или опровергается или без изменений
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

        opinion_note = " [с учётом мнения Ольги]" if opinion else ""
        new_entry = f"- {today} - {ocenka} ({izmenenie}){opinion_note}: {obnovlenie}"

        updated_content = content.replace(
            "## История оценок",
            f"## История оценок\n{new_entry}"
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(updated_content)

        print(f"   {ocenka} ({izmenenie}){opinion_note} - {filename}")

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