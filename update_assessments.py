import requests
import os
from datetime import date, datetime

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
VAULT_PATH = os.path.expanduser("~/radar/01_Assessments")
DAYS_THRESHOLD = 30

def get_old_assessments():
    """Находим оценки старше 30 дней."""
    today = date.today()
    old_files = []
    
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
        except:
            continue
    
    return old_files

def update_assessment(filepath, filename, days_old):
    """Читаем файл и просим Claude обновить оценку."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    today = date.today().strftime("%Y-%m-%d")
    
    prompt = f"""Ты — измерительный прибор агентного и ИИ-рынка.

Ниже оценка opensource-проекта сделанная {days_old} дней назад.
Твоя задача: оценить актуальность гипотезы на сегодня.

{content}

Отвечай СТРОГО в этом формате:
ОЦЕНКА: СДВИГ или ШУМ (может измениться или остаться)
ИЗМЕНЕНИЕ: подтверждается или опровергается или без изменений
ОБНОВЛЕНИЕ: [2-3 предложения — что произошло в экосистеме за это время что влияет на оценку]"""

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
        
        # Добавляем запись в историю оценок
        new_entry = f"- {today} — {ocenka} ({izmenenie}): {obnovlenie}"
        updated_content = content.replace(
            "## История оценок",
            f"## История оценок\n{new_entry}"
        )
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print(f"   {ocenka} ({izmenenie}) — {filename}")
        
    except Exception as e:
        print(f"   Ошибка {filename}: {e}")

if __name__ == "__main__":
    print("Ищем оценки старше 30 дней...")
    old_files = get_old_assessments()
    
    if not old_files:
        print(f"   Нет оценок старше {DAYS_THRESHOLD} дней. Скрипт запустится автоматически когда они появятся.")
    else:
        print(f"   Найдено: {len(old_files)} файлов для обновления")
        for f in old_files:
            update_assessment(f["filepath"], f["filename"], f["days_old"])
    
    print("\nГотово.")
