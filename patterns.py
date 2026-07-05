#!/usr/bin/env python3
"""
patterns.py - кластеризация и обслуживание паттернов vault Radar

Что делает:
1. Читает все файлы СДВИГ из 01_Assessments/ (только суть сдвига - экономия токенов)
2. Sonnet анализирует и предлагает кластеры (только на основе переданных файлов)
3. Создаёт файлы паттернов в 02_Patterns/ (не перезаписывает существующие)
4. Архивирует паттерны без новых сигналов 90+ дней -> 03_Archive/
5. Помечает паттерны как ПОДТВЕРЖДЁН / ОПРОВЕРГНУТ раз в 6 месяцев
6. Отправляет итог в Telegram
"""

import os
import re
import glob
import json
import anthropic
import requests
from datetime import datetime, timedelta

MODEL_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "99_System", "model_config.json")

def load_model_config():
    with open(MODEL_CONFIG_PATH) as f:
        return json.load(f)

MODEL_CONFIG = load_model_config()


VAULT_PATH = os.environ.get("VAULT_PATH", os.path.expanduser("~/radar/radar"))
ASSESSMENTS_PATH = os.path.join(VAULT_PATH, "01_Assessments")
PATTERNS_PATH = os.path.join(VAULT_PATH, "02_Patterns")
ARCHIVE_PATH = os.path.join(VAULT_PATH, "03_Archive")
ANALYSTS_PATH = os.path.join(VAULT_PATH, "04_Analysts")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_OWNER_ID = os.environ.get("TELEGRAM_OWNER_ID")

DAYS_NO_SIGNAL = 90
MONTHS_FALSIFY = 6

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def send_telegram(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_OWNER_ID:
        print("[Telegram] токены не заданы, пропускаю")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_OWNER_ID, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print(f"[Telegram] ошибка: {r.text}")
    except Exception as e:
        print(f"[Telegram] исключение: {e}")


# ---------------------------------------------------------------------------
# Чтение оценок - только суть сдвига, не весь файл
# ---------------------------------------------------------------------------

def extract_shift_summary(content):
    """Извлечь только раздел 'Что меняется в экосистеме' - 2-3 предложения."""
    in_section = False
    lines = []
    for line in content.splitlines():
        if line.startswith("## Что меняется в экосистеме"):
            in_section = True
            continue
        if in_section:
            if line.startswith("##"):
                break
            if line.strip():
                lines.append(line.strip())
    summary = " ".join(lines).strip()
    return summary[:300] if summary else content[:300]


def read_analysts():
    """Прочитать файлы аналитиков из 04_Analysts/."""
    if not os.path.exists(ANALYSTS_PATH):
        return []
    files = glob.glob(os.path.join(ANALYSTS_PATH, "*.md"))
    analysts = []
    for filepath in sorted(files):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        name = ""
        weight = 1.0
        date = ""
        for line in content.splitlines():
            if line.startswith("**Аналитик:**"):
                name = line.replace("**Аналитик:**", "").strip()
            elif line.startswith("**Вес доверия:**"):
                try:
                    weight = float(line.replace("**Вес доверия:**", "").strip())
                except ValueError:
                    pass
            elif line.startswith("**Дата выпуска:**"):
                date = line.replace("**Дата выпуска:**", "").strip()
        claims = []
        current_claim = {}
        for line in content.splitlines():
            if line.startswith("### Claim "):
                if current_claim:
                    claims.append(current_claim)
                current_claim = {}
            elif line.startswith("**Тезис:**") and current_claim is not None:
                current_claim["thesis"] = line.replace("**Тезис:**", "").strip()
            elif line.startswith("**Уверенность:**") and current_claim is not None:
                current_claim["confidence"] = line.replace("**Уверенность:**", "").strip()
        if current_claim:
            claims.append(current_claim)
        if name and claims:
            analysts.append({"name": name, "weight": weight, "date": date, "claims": claims})
    return analysts


def read_assessments():
    """Прочитать все СДВИГ-оценки из 01_Assessments/."""
    files = glob.glob(os.path.join(ASSESSMENTS_PATH, "*.md"))
    assessments = []
    for filepath in sorted(files):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if "**Оценка:** СДВИГ" not in content:
            continue
        title = ""
        repo_url = ""
        file_date = ""
        for line in content.splitlines():
            if line.startswith("# Оценка:"):
                title = line.replace("# Оценка:", "").strip()
            if line.startswith("**Репозиторий:**"):
                repo_url = line.replace("**Репозиторий:**", "").strip()
            if line.startswith("**Дата:**"):
                file_date = line.replace("**Дата:**", "").strip()
        assessments.append({
            "filename": os.path.basename(filepath),
            "title": title or os.path.basename(filepath),
            "repo_url": repo_url,
            "date": file_date,
            "content": extract_shift_summary(content),
        })
    return assessments


# ---------------------------------------------------------------------------
# Кластеризация
# ---------------------------------------------------------------------------

def get_existing_patterns():
    """Вернуть:
    - names: множество названий для передачи в промпт Sonnet
    - covered_files: множество filename оценок которые уже входят в паттерн
    """
    os.makedirs(PATTERNS_PATH, exist_ok=True)
    names = set()
    covered_files = set()
    for filepath in glob.glob(os.path.join(PATTERNS_PATH, "*.md")):
        names.add(os.path.basename(filepath).replace(".md", "").strip())
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        # Ищем все [[ссылки]] в разделе Связи — это имена файлов оценок
        found = re.findall(r"\[\[(.+?)\]\]", content)
        for link in found:
            covered_files.add(link.strip() + ".md")
    return names, covered_files


def cluster_with_sonnet(assessments, existing_patterns, analysts=None):
    if analysts is None:
        analysts = []

    assessments_text = ""
    for i, a in enumerate(assessments, 1):
        assessments_text += (
            f"\n[{i}] {a['title']} ({a['date']})\n"
            f"Файл: {a['filename']}\n"
            f"Суть: {a['content']}\n"
        )

    existing_text = (
        f"Уже существующие паттерны (НЕ создавать повторно): {', '.join(existing_patterns)}"
        if existing_patterns else ""
    )

    analysts_block = ""
    if analysts:
        analysts_block = "\n\nEXTERNAL_ANALYSTS:\n"
        for analyst in analysts:
            analysts_block += f"\n[{analyst['name']}] (дата: {analyst['date']}, вес: {analyst['weight']})\n"
            for claim in analyst["claims"]:
                analysts_block += f"- {claim['thesis']} (уверенность: {claim.get('confidence', '')})\n"

    today = datetime.now().strftime("%Y-%m-%d")

    external_instructions = ""
    external_json_fields = ""
    if analysts:
        external_instructions = """
4. For each cluster find:
   - external_confirmation: claims from EXTERNAL_ANALYSTS that match this cluster (format: "AnalystName DATE (вес W): thesis")
   - our_unique_signals: what OUR_SIGNALS show that EXTERNAL_ANALYSTS do NOT mention
   - external_only_signals: what EXTERNAL_ANALYSTS mention that is NOT in OUR_SIGNALS
Respond in Russian language only."""
        external_json_fields = """,
      "external_confirmation": ["AnalystName DATE (вес W): тезис который совпадает"],
      "our_unique_signals": ["что видим мы, аналитики не видят"],
      "external_only_signals": ["что видят аналитики, нас нет"]"""

    prompt = f"""You are a pattern-clustering engine for an open-source technology radar.
Today's date is {today}.

You receive short summaries of technology shift assessments collected from real repositories.
Your job is ONLY to group them based on what is written in the summaries themselves.

CRITICAL RULES:
- Base ALL conclusions ONLY on the summaries provided. Do not use your training knowledge about market trends.
- Minimum 2 assessments per cluster.
- A cluster must represent a STRUCTURAL shift in how knowledge or value is organized.
- Name each cluster as a short Russian noun phrase (3-6 words) describing WHAT IS CHANGING.
- Orphans = assessments that don't fit any cluster with 2+ members.
- {existing_text}

OUR_SIGNALS:
{assessments_text}{analysts_block}

Tasks:
1. Cluster OUR_SIGNALS into patterns as described above.
2. For each cluster: check if there is confirmation in EXTERNAL_ANALYSTS.
3. Find External-only signals — what analysts see that is NOT in OUR_SIGNALS.{external_instructions}

Respond ONLY in JSON, no preamble, no markdown backticks:
{{
  "clusters": [
    {{
      "name": "Название паттерна на русском",
      "description": "Одно предложение - что меняется структурно",
      "assessment_files": ["filename1.md", "filename2.md"],
      "earliest_signal": "YYYY-MM-DD",
      "hypothesis_right": "Что увидим через 12 месяцев если паттерн реален",
      "hypothesis_wrong": "Что увидим через 12 месяцев если ошиблись"{external_json_fields}
    }}
  ],
  "orphans": ["filename.md"]
}}"""

    response = client.messages.create(
        model=MODEL_CONFIG["sonnet"],
        thinking={"type": "disabled"},
        max_tokens=5200,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    # Защита от обрезанного JSON
    if not raw.endswith("}"):
        last_bracket = raw.rfind("}")
        if last_bracket != -1:
            raw = raw[:last_bracket + 1]
            open_count = raw.count("{")
            close_count = raw.count("}")
            if open_count > close_count:
                raw += "}" * (open_count - close_count)

    return json.loads(raw)


def create_pattern_file(cluster, covered_files):
    today = datetime.now().strftime("%Y-%m-%d")
    safe_name = re.sub(r'[/\\:*?"<>|]', "-", cluster["name"])
    filename = f"{safe_name} {today}.md"
    filepath = os.path.join(PATTERNS_PATH, filename)

    if os.path.exists(filepath):
        print(f"[patterns] уже существует, пропускаю: {filename}")
        return None

    # Проверяем пересечение с уже покрытыми оценками
    new_files = set(cluster["assessment_files"])
    overlap = new_files & covered_files
    if len(overlap) >= len(new_files) / 2:
        print(f"[patterns] дубль по оценкам, пропускаю: {cluster['name']} (пересечение: {overlap})")
        return None

    links = [f"[[{f.replace('.md', '')}]]" for f in cluster["assessment_files"]]
    links_str = ", ".join(links) if links else "-"

    external_confirmation = cluster.get("external_confirmation", [])
    our_unique = cluster.get("our_unique_signals", [])
    external_only = cluster.get("external_only_signals", [])

    external_section = ""
    if external_confirmation or our_unique or external_only:
        conf_lines = "\n".join(f"- {c}" for c in external_confirmation) if external_confirmation else "- нет"
        our_lines = "\n".join(f"- {s}" for s in our_unique) if our_unique else ""
        ext_lines = "\n".join(f"- {s}" for s in external_only) if external_only else ""

        external_section = f"""
## Внешнее подтверждение
{conf_lines}

## Расхождения
"""
        if our_lines:
            external_section += f"**Наш уникальный сигнал:**\n{our_lines}\n"
        if ext_lines:
            external_section += f"**External-only signal:**\n{ext_lines}\n"

    content = f"""# {cluster['name']}

**Первый сигнал:** {cluster.get('earliest_signal', today)}
**Подтверждающие оценки:** {links_str}
**Создан:** {today} (автоматически, patterns.py)
**Статус:** АКТИВНЫЙ

## Суть
{cluster['description']}

## Почему важно сейчас
[Добавить вручную]

## Если права
{cluster.get('hypothesis_right', '[Добавить вручную]')}

## Если ошиблась
{cluster.get('hypothesis_wrong', '[Добавить вручную]')}
{external_section}
## История наблюдений
- {today} - паттерн выделен автоматически из {len(cluster['assessment_files'])} оценок

## Правка человека
<!-- Не согласна с кластером? Добавь строку: - [дата] - [комментарий] -->

## Связи
{"".join(f"- [[{f.replace('.md', '')}]]" + chr(10) for f in cluster['assessment_files'])}
**Модель:** claude-sonnet-5
**Промпт версия:** v1.0"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[patterns] создан: {filename}")
    return filename


# ---------------------------------------------------------------------------
# Архивирование
# ---------------------------------------------------------------------------

def get_last_signal_date(pattern_content, pattern_filepath):
    dates = re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", pattern_content)
    if dates:
        return max(datetime.strptime(d, "%Y-%m-%d") for d in dates)
    mtime = os.path.getmtime(pattern_filepath)
    return datetime.fromtimestamp(mtime)


def archive_stale_patterns():
    os.makedirs(ARCHIVE_PATH, exist_ok=True)
    archived = []
    threshold = datetime.now() - timedelta(days=DAYS_NO_SIGNAL)

    for filepath in glob.glob(os.path.join(PATTERNS_PATH, "*.md")):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if any(s in content for s in ["**Статус:** АРХИВ", "**Статус:** ПОДТВЕРЖДЁН", "**Статус:** ОПРОВЕРГНУТ"]):
            continue
        last_signal = get_last_signal_date(content, filepath)
        if last_signal < threshold:
            updated = content.replace(
                "**Статус:** АКТИВНЫЙ",
                f"**Статус:** АРХИВ\n**Архивирован:** {datetime.now().strftime('%Y-%m-%d')} - нет новых сигналов {DAYS_NO_SIGNAL}+ дней"
            )
            dest = os.path.join(ARCHIVE_PATH, os.path.basename(filepath))
            with open(dest, "w", encoding="utf-8") as f:
                f.write(updated)
            os.remove(filepath)
            name = os.path.basename(filepath).replace(".md", "")
            archived.append(name)
            print(f"[archive] перенесён: {name}")

    return archived


# ---------------------------------------------------------------------------
# Фальсификация
# ---------------------------------------------------------------------------

def should_falsify(pattern_content):
    if "ФАЛЬСИФИКАЦИЯ ПРОВЕДЕНА" in pattern_content:
        return False
    dates = re.findall(r"Создан:\*\* (\d{4}-\d{2}-\d{2})", pattern_content)
    if not dates:
        return False
    created = datetime.strptime(dates[0], "%Y-%m-%d")
    return datetime.now() - created >= timedelta(days=MONTHS_FALSIFY * 30)


def falsify_pattern(filepath, pattern_content, assessments):
    dates = re.findall(r"Создан:\*\* (\d{4}-\d{2}-\d{2})", pattern_content)
    if not dates:
        return None
    today = datetime.now().strftime("%Y-%m-%d")
    newer = [a for a in assessments if a.get("date") and a["date"] > dates[0]]
    if not newer:
        return None

    newer_text = "\n".join(
        f"- {a['title']} ({a['date']}): {a['content'][:200]}" for a in newer[:15]
    )

    hypothesis_right = ""
    hypothesis_wrong = ""
    lines = pattern_content.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("## Если права") and i + 1 < len(lines):
            hypothesis_right = lines[i + 1].strip()
        if line.startswith("## Если ошиблась") and i + 1 < len(lines):
            hypothesis_wrong = lines[i + 1].strip()

    prompt = f"""You are evaluating whether a technology pattern hypothesis has been confirmed or refuted.
Today is {today}.

CRITICAL: Base your verdict ONLY on the new assessments provided. Do not use your training knowledge.

Pattern hypothesis IF CORRECT: {hypothesis_right}
Pattern hypothesis IF WRONG: {hypothesis_wrong}

New assessments after pattern creation:
{newer_text}

Respond in JSON only:
{{
  "verdict": "ПОДТВЕРЖДЁН" or "ОПРОВЕРГНУТ" or "РАНО_СУДИТЬ",
  "reasoning": "2-3 sentences in Russian based only on the assessments above"
}}"""

    response = client.messages.create(
        model=MODEL_CONFIG["sonnet"],
        thinking={"type": "disabled"},
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    result = json.loads(raw.strip())

    verdict = result.get("verdict", "РАНО_СУДИТЬ")
    reasoning = result.get("reasoning", "")

    if verdict == "РАНО_СУДИТЬ":
        print(f"[falsify] рано судить: {os.path.basename(filepath)}")
        return None

    today_str = datetime.now().strftime("%Y-%m-%d")
    updated = pattern_content.replace("**Статус:** АКТИВНЫЙ", f"**Статус:** {verdict}")
    updated += f"\n\n## Фальсификация {today_str}\n**Вердикт:** {verdict}\n**Основание:** {reasoning}\nФАЛЬСИФИКАЦИЯ ПРОВЕДЕНА\n"

    if verdict == "ОПРОВЕРГНУТ":
        dest = os.path.join(ARCHIVE_PATH, os.path.basename(filepath))
        with open(dest, "w", encoding="utf-8") as f:
            f.write(updated)
        os.remove(filepath)
        print(f"[falsify] опровергнут, в архив: {os.path.basename(filepath)}")
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"[falsify] подтверждён: {os.path.basename(filepath)}")

    return verdict


def run_falsification(assessments):
    os.makedirs(ARCHIVE_PATH, exist_ok=True)
    results = {"confirmed": [], "refuted": []}
    for filepath in glob.glob(os.path.join(PATTERNS_PATH, "*.md")):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if not should_falsify(content):
            continue
        name = os.path.basename(filepath).replace(".md", "")
        print(f"[falsify] проверяю: {name}")
        verdict = falsify_pattern(filepath, content, assessments)
        if verdict == "ПОДТВЕРЖДЁН":
            results["confirmed"].append(name)
        elif verdict == "ОПРОВЕРГНУТ":
            results["refuted"].append(name)
    return results


# ---------------------------------------------------------------------------
# Главная функция
# ---------------------------------------------------------------------------

def main():
    print(f"[patterns] vault: {VAULT_PATH}")

    if not os.path.exists(ASSESSMENTS_PATH):
        print(f"[patterns] ОШИБКА: папка не найдена: {ASSESSMENTS_PATH}")
        send_telegram("Паттерны: ошибка - папка 01_Assessments не найдена")
        return

    os.makedirs(PATTERNS_PATH, exist_ok=True)
    os.makedirs(ARCHIVE_PATH, exist_ok=True)

    assessments = read_assessments()
    print(f"[patterns] СДВИГ оценок: {len(assessments)}")

    analysts = read_analysts()
    print(f"[patterns] аналитиков: {len(analysts)}")

    telegram_lines = ["<b>Радар - обслуживание паттернов</b>"]

    # 1. Архивирование устаревших
    archived = archive_stale_patterns()
    if archived:
        telegram_lines.append(f"\nАрхивировано (нет сигналов {DAYS_NO_SIGNAL}+ дней): {len(archived)}")
        for name in archived:
            telegram_lines.append(f"- {name}")

    # 2. Фальсификация гипотез
    if assessments:
        falsify_results = run_falsification(assessments)
        if falsify_results["confirmed"]:
            telegram_lines.append(f"\nПодтверждено паттернов: {len(falsify_results['confirmed'])}")
            for name in falsify_results["confirmed"]:
                telegram_lines.append(f"- {name}")
        if falsify_results["refuted"]:
            telegram_lines.append(f"\nОпровергнуто и архивировано: {len(falsify_results['refuted'])}")
            for name in falsify_results["refuted"]:
                telegram_lines.append(f"- {name}")

    # 3. Кластеризация
    if not assessments:
        telegram_lines.append("\nНет СДВИГ оценок для кластеризации")
        send_telegram("\n".join(telegram_lines))
        return

    existing_patterns, covered_files = get_existing_patterns()
    print(f"[patterns] существующих паттернов: {len(existing_patterns)}, покрытых оценок: {len(covered_files)}")

    print("[patterns] кластеризация через Sonnet...")
    result = cluster_with_sonnet(assessments, existing_patterns, analysts)

    clusters = result.get("clusters", [])
    orphans = result.get("orphans", [])
    print(f"[patterns] кластеров: {len(clusters)}, осиротевших оценок: {len(orphans)}")

    created = []
    skipped = []
    for cluster in clusters:
        filename = create_pattern_file(cluster, covered_files)
        if filename:
            created.append(cluster["name"])
            # Добавляем новые файлы в covered чтобы не дублировать в этом же запуске
            covered_files.update(cluster["assessment_files"])
        else:
            skipped.append(cluster["name"])

    if created:
        telegram_lines.append(f"\nНовых паттернов создано: {len(created)}")
        for name in created:
            telegram_lines.append(f"- {name}")
    if skipped:
        telegram_lines.append(f"\nПропущено (уже существуют): {len(skipped)}")
    if orphans:
        telegram_lines.append(f"\nБез паттерна: {len(orphans)} оценок (не набрали пары)")
    if not created and not skipped and not archived:
        telegram_lines.append("\nВсё в порядке, новых изменений нет")

    send_telegram("\n".join(telegram_lines))
    print("[patterns] готово")


if __name__ == "__main__":
    main()
