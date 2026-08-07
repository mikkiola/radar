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
import html
import anthropic
import requests
from datetime import datetime, timedelta
from vault_language import ENGLISH_ASSESSMENT_HEADING, is_english_body

import vault_write

MODEL_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "99_System", "model_config.json")

def load_model_config():
    with open(MODEL_CONFIG_PATH) as f:
        return json.load(f)

MODEL_CONFIG = load_model_config()


VAULT_ROOT = os.environ.get("VAULT_ROOT", os.path.expanduser("~/radar/radar"))
ASSESSMENTS_PATH = os.path.join(VAULT_ROOT, "01_Assessments")
PATTERNS_PATH = os.path.join(VAULT_ROOT, "02_Patterns")
ARCHIVE_PATH = os.path.join(VAULT_ROOT, "03_Archive")
ANALYSTS_PATH = os.path.join(VAULT_ROOT, "04_Analysts")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_OWNER_ID = os.environ.get("TELEGRAM_OWNER_ID")

DAYS_NO_SIGNAL = 90
MONTHS_FALSIFY = 6
DAYS_ASSESSMENT_BATCH = 14  # оценки старше этого срока не идут в промпт кластеризации,
# иначе объем растет вместе с vault и Sonnet обрывает JSON на max_tokens (инцидент 2026-07-11)
DAYS_PATTERN_ACTIVITY = 60  # паттерны без новых подтверждающих оценок дольше этого срока
# не передаются в промпт кластеризации - новым оценкам маловероятно с ними совпасть

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


class UnrecoverableJSONError(Exception):
    """JSON-ответ LLM, который нельзя безопасно восстановить."""

    def __init__(self, parse_error, stop_reason, raw):
        self.parse_error = parse_error
        self.stop_reason = stop_reason
        self.raw_length = len(raw)
        self.raw_start = raw[:300]
        self.raw_end = raw[-300:]
        super().__init__(str(parse_error))


class ParsedLLMJSON(dict):
    """Результат разбора с признаком частичного восстановления."""

    def __init__(self, value, repair_used=False):
        super().__init__(value)
        self.repair_used = repair_used


def _strip_json_code_fence(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        if len(parts) > 1:
            raw = parts[1]
            if raw.startswith("json"):
                raw = raw[4:]
    return raw.strip()


def _repair_llm_json(raw):
    """Обрезать ответ после последнего полного объекта верхнего массива."""
    stack = []
    last_boundary = None
    in_string = False
    escaped = False

    for index, char in enumerate(raw):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char in "{[":
            stack.append(char)
        elif char in "}]":
            expected_open = "{" if char == "}" else "["
            if not stack or stack[-1] != expected_open:
                continue
            stack.pop()
            if char == "}" and len(stack) == 2:
                last_boundary = (index, stack.copy())

    if last_boundary is None:
        return None

    index, open_brackets = last_boundary
    closing_brackets = {"{": "}", "[": "]"}
    return raw[:index + 1] + "".join(closing_brackets[bracket] for bracket in reversed(open_brackets))


def parse_llm_json(raw, stop_reason=None):
    """Разобрать JSON LLM и при необходимости восстановить полный префикс."""
    raw = _strip_json_code_fence(raw)
    repair_attempted = False
    repair_succeeded = False
    try:
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as error:
            repair_attempted = True
            repaired_raw = _repair_llm_json(raw)
            if repaired_raw is None:
                raise UnrecoverableJSONError(error, stop_reason, raw) from error
            try:
                result = json.loads(repaired_raw)
            except json.JSONDecodeError as repair_error:
                raise UnrecoverableJSONError(repair_error, stop_reason, raw) from repair_error
            repair_succeeded = True

        if not isinstance(result, dict):
            raise UnrecoverableJSONError(
                ValueError("верхний уровень JSON должен быть объектом"), stop_reason, raw
            )
        return ParsedLLMJSON(result, repair_used=repair_succeeded)
    finally:
        print(
            f"[llm-json] stop_reason={stop_reason}, "
            f"repair_attempted={repair_attempted}, repair_succeeded={repair_succeeded}"
        )


def send_json_error_telegram(error, context):
    """Отправить безопасную диагностику неразбираемого ответа LLM."""
    commit_sha = os.environ.get("CI_COMMIT_SHA")
    lines = [
        "<b>Паттерны: неразбираемый JSON от LLM</b>",
        f"Причина: {html.escape(str(error.parse_error))}",
        f"stop_reason: {html.escape(str(error.stop_reason))}",
        f"Длина ответа: {error.raw_length}",
        context,
        f"Начало ответа: <code>{html.escape(error.raw_start)}</code>",
        f"Конец ответа: <code>{html.escape(error.raw_end)}</code>",
    ]
    if commit_sha:
        lines.append(f"CI_COMMIT_SHA: {html.escape(commit_sha)}")
    send_telegram("\n".join(lines))


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
        if line.startswith((ENGLISH_ASSESSMENT_HEADING, "## Что меняется в экосистеме")):
            in_section = True
            continue
        if in_section:
            if line.startswith("##"):
                break
            if line.strip():
                lines.append(line.strip())
    summary = " ".join(lines).strip()
    return summary[:300] if summary else content[:300]


def extract_source_block(content):
    """Извлечь файл/локацию/цитату из блока **Источник:** оценки.
    Возвращает пустые строки для оценок без этого блока (написанных до его введения)."""
    source = {"file": "", "location": "", "quote": ""}
    in_block = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("**Источник:**"):
            in_block = True
            continue
        if not in_block:
            continue
        if stripped.startswith("##"):
            break
        if stripped.startswith("файл:"):
            value = stripped[len("файл:"):].strip()
            if value and value != "не указан":
                source["file"] = value
        elif stripped.startswith("локация:"):
            value = stripped[len("локация:"):].strip()
            if value and value != "не указана":
                source["location"] = value
        elif stripped.startswith("цитата:"):
            value = stripped[len("цитата:"):].strip().strip('"')
            if value and value != "не указана":
                source["quote"] = value
    return source


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
    """Прочитать все VALIDATED_SHIFT-оценки из 01_Assessments/ - читает только status
    из frontmatter, никогда текстовое поле **Оценка:** (устраняет Split-Brain)."""
    files = glob.glob(os.path.join(ASSESSMENTS_PATH, "*.md"))
    assessments = []
    for filepath in sorted(files):
        frontmatter, body = vault_write.read_frontmatter(filepath)
        if frontmatter is None or frontmatter.get("status") != "VALIDATED_SHIFT":
            continue
        title = ""
        repo_url = ""
        file_date = ""
        for line in body.splitlines():
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
            "content": extract_shift_summary(body),
            "source": extract_source_block(body),
        })
    return assessments


# ---------------------------------------------------------------------------
# Кластеризация
# ---------------------------------------------------------------------------

def get_existing_patterns(active_days=None):
    """Вернуть:
    - active_names: названия паттернов для передачи в промпт Sonnet (если active_days задан -
      только паттерны с активностью за последние active_days дней по get_last_signal_date,
      иначе все)
    - all_names: все названия существующих паттернов (для статистики)
    - covered_files: множество filename оценок которые уже входят в какой-либо паттерн
    """
    os.makedirs(PATTERNS_PATH, exist_ok=True)
    active_names = set()
    all_names = set()
    covered_files = set()
    threshold = datetime.now() - timedelta(days=active_days) if active_days else None
    for filepath in glob.glob(os.path.join(PATTERNS_PATH, "*.md")):
        name = os.path.basename(filepath).replace(".md", "").strip()
        all_names.add(name)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        # Ищем все [[ссылки]] в разделе Связи - это имена файлов оценок
        found = re.findall(r"\[\[(.+?)\]\]", content)
        for link in found:
            covered_files.add(link.strip() + ".md")
        if threshold is None or get_last_signal_date(content, filepath) >= threshold:
            active_names.add(name)
    return active_names, all_names, covered_files


def split_recent_assessments(assessments, days):
    """Разделить оценки на batch за последние `days` дней (по полю date) и более старые.
    Оценки без распознаваемой даты попадают в recent - не рискуем молча потерять их из batch.
    """
    threshold = datetime.now() - timedelta(days=days)
    recent = []
    older = []
    for a in assessments:
        try:
            a_date = datetime.strptime(a["date"], "%Y-%m-%d")
        except (ValueError, TypeError):
            recent.append(a)
            continue
        if a_date >= threshold:
            recent.append(a)
        else:
            older.append(a)
    return recent, older


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
Respond in English. All external_confirmation, our_unique_signals, and external_only_signals values must be in English."""
        external_json_fields = """,
      "external_confirmation": ["AnalystName DATE (weight W): matching thesis"],
      "our_unique_signals": ["what we see that analysts do not mention"],
      "external_only_signals": ["what analysts mention that is not in our signals"]"""

    prompt = f"""You are a pattern-clustering engine for an open-source technology radar.
Today's date is {today}.

You receive short summaries of technology shift assessments collected from real repositories.
Your job is ONLY to group them based on what is written in the summaries themselves.

CRITICAL RULES:
- Base ALL conclusions ONLY on the summaries provided. Do not use your training knowledge about market trends.
- Minimum 2 assessments per cluster.
- A cluster must represent a STRUCTURAL shift in how knowledge or value is organized.
- Name each cluster as a short English noun phrase (3-6 words) describing WHAT IS CHANGING.
- All name, description, hypothesis_right, and hypothesis_wrong values must be in English.
- Orphans = assessments that don't fit any cluster with 2+ members.
- {existing_text}

OUR_SIGNALS:
{assessments_text}{analysts_block}

Tasks:
1. Cluster OUR_SIGNALS into patterns as described above.
2. For each cluster: check if there is confirmation in EXTERNAL_ANALYSTS.
3. Find External-only signals - what analysts see that is NOT in OUR_SIGNALS.{external_instructions}

Respond ONLY in JSON, no preamble, no markdown backticks:
{{
  "clusters": [
    {{
      "name": "English pattern name",
      "description": "One English sentence describing the structural change",
      "assessment_files": ["filename1.md", "filename2.md"],
      "earliest_signal": "YYYY-MM-DD",
      "hypothesis_right": "What we will observe in 12 months if the pattern is real",
      "hypothesis_wrong": "What we will observe in 12 months if we are wrong"{external_json_fields}
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

    raw = response.content[0].text
    stop_reason = response.stop_reason
    try:
        return parse_llm_json(raw, stop_reason)
    except UnrecoverableJSONError as error:
        send_json_error_telegram(
            error,
            f"Размер batch: {len(assessments)}",
        )
        raise


def _pattern_links(pattern_filepath):
    """Множество filename оценок, которые паттерн уже перечисляет в [[ссылках]]."""
    with open(pattern_filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return {m.strip() + ".md" for m in re.findall(r"\[\[(.+?)\]\]", content)}


def find_dominant_pattern(overlap_files):
    """Найти существующий паттерн с наибольшим пересечением по overlap_files.
    При равенстве побеждает первый по алфавиту filename."""
    best_name = None
    best_count = 0
    for filepath in sorted(glob.glob(os.path.join(PATTERNS_PATH, "*.md"))):
        count = len(_pattern_links(filepath) & overlap_files)
        if count > best_count:
            best_count = count
            best_name = os.path.basename(filepath).replace(".md", "")
    return best_name


def count_existing_backlinks(pattern_name):
    """Сколько файлов оценок уже содержат обратную пометку на этот паттерн.
    Механический подсчёт по 01_Assessments/ - не зависит от файла паттерна,
    поэтому корректно растёт между отдельными запусками, даже если сам файл
    паттерна никогда не перезаписывается."""
    marker = f"**Часть паттерна:** [[{pattern_name}]]"
    count = 0
    for filepath in glob.glob(os.path.join(ASSESSMENTS_PATH, "*.md")):
        with open(filepath, "r", encoding="utf-8") as f:
            if marker in f.read():
                count += 1
    return count


def mark_assessment_as_pattern_member(assessment_filename, pattern_name):
    """Точечно дописать обратную пометку в файл оценки о вхождении в существующий паттерн.
    Не трогает статус СДВИГ/ШУМ и не перезаписывает файл целиком.
    Однократное событие на пару (оценка, паттерн) - если пометка на этот паттерн уже есть,
    повторно не пишем."""
    filepath = os.path.join(ASSESSMENTS_PATH, assessment_filename)
    if not os.path.exists(filepath):
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    marker = f"**Часть паттерна:** [[{pattern_name}]]"
    if marker in content:
        return False

    n = count_existing_backlinks(pattern_name) + 1
    today = datetime.now().strftime("%Y-%m-%d")
    new_line = f"{marker} (не новый сигнал - {n}-е подтверждение, {today})"

    lines = content.splitlines(keepends=True)
    insert_at = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("**Часть паттерна:**"):
            insert_at = i + 1
        elif insert_at is None and stripped.startswith("**Промпт версия:**"):
            insert_at = i + 1
    if insert_at is None:
        return False

    lines.insert(insert_at, new_line + "\n")
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return True


def create_pattern_file(cluster, covered_files, assessments_by_filename=None):
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
        dominant = find_dominant_pattern(overlap)
        if dominant:
            for assessment_filename in sorted(overlap):
                if mark_assessment_as_pattern_member(assessment_filename, dominant):
                    print(f"[patterns] обратная пометка: {assessment_filename} -> [[{dominant}]]")
        return None

    links = [f"[[{f.replace('.md', '')}]]" for f in cluster["assessment_files"]]
    links_str = ", ".join(links) if links else "-"

    sources_section = ""
    if assessments_by_filename:
        source_lines = []
        for f in cluster["assessment_files"]:
            a = assessments_by_filename.get(f)
            src = (a or {}).get("source") or {}
            if not (src.get("file") or src.get("location") or src.get("quote")):
                continue
            quote = src.get("quote")
            source_lines.append(
                f"- [[{f.replace('.md', '')}]] — "
                f"файл: {src.get('file') or 'не указан'}, "
                f"локация: {src.get('location') or 'не указана'}, "
                f"цитата: {f'\"{quote}\"' if quote else 'не указана'}"
            )
        if source_lines:
            sources_section = "## Sources\n" + "\n".join(source_lines) + "\n\n"

    external_confirmation = cluster.get("external_confirmation", [])
    our_unique = cluster.get("our_unique_signals", [])
    external_only = cluster.get("external_only_signals", [])

    external_section = ""
    if external_confirmation or our_unique or external_only:
        conf_lines = "\n".join(f"- {c}" for c in external_confirmation) if external_confirmation else "- none"
        our_lines = "\n".join(f"- {s}" for s in our_unique) if our_unique else ""
        ext_lines = "\n".join(f"- {s}" for s in external_only) if external_only else ""

        external_section = f"""
## External Confirmation
{conf_lines}

## Discrepancies
"""
        if our_lines:
            external_section += f"**Our Unique Signal:**\n{our_lines}\n"
        if ext_lines:
            external_section += f"**External-only signal:**\n{ext_lines}\n"

    content = f"""# {cluster['name']}

**Первый сигнал:** {cluster.get('earliest_signal', today)}
**Подтверждающие оценки:** {links_str}
**Создан:** {today} (автоматически, patterns.py)
**Статус:** АКТИВНЫЙ

## Summary
{cluster['description']}

{sources_section}## Why It Matters Now
[Добавить вручную]

## If Right
{cluster.get('hypothesis_right', '[Добавить вручную]')}

## If Wrong
{cluster.get('hypothesis_wrong', '[Добавить вручную]')}
{external_section}
## Observation History
- {today} - pattern automatically identified from {len(cluster['assessment_files'])} assessments

## Правка человека
<!-- Не согласна с кластером? Добавь строку: - [дата] - [комментарий] -->

## Links
{"".join(f"- [[{f.replace('.md', '')}]]" + chr(10) for f in cluster['assessment_files'])}
**Модель:** {MODEL_CONFIG['sonnet']}
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


def extract_pattern_hypotheses(pattern_content):
    """Извлечь гипотезы паттерна из русского или English шаблона."""
    hypothesis_right = ""
    hypothesis_wrong = ""
    lines = pattern_content.splitlines()
    for i, line in enumerate(lines):
        if line.startswith(("## If Right", "## Если права")) and i + 1 < len(lines):
            hypothesis_right = lines[i + 1].strip()
        if line.startswith(("## If Wrong", "## Если ошиблась")) and i + 1 < len(lines):
            hypothesis_wrong = lines[i + 1].strip()
    return hypothesis_right, hypothesis_wrong


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

    hypothesis_right, hypothesis_wrong = extract_pattern_hypotheses(pattern_content)
    response_language = "English" if is_english_body(pattern_content) else "Russian"

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
  "reasoning": "2-3 sentences in {response_language} based only on the assessments above"
}}"""

    response = client.messages.create(
        model=MODEL_CONFIG["sonnet"],
        thinking={"type": "disabled"},
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text
    stop_reason = response.stop_reason
    try:
        result = parse_llm_json(raw, stop_reason)
        verdict = result.get("verdict")
        reasoning = result.get("reasoning")
        expected_verdicts = {"ПОДТВЕРЖДЁН", "ОПРОВЕРГНУТ", "РАНО_СУДИТЬ"}
        if verdict not in expected_verdicts:
            raise UnrecoverableJSONError(
                ValueError("неожиданный verdict"), stop_reason, raw
            )
        if verdict in {"ПОДТВЕРЖДЁН", "ОПРОВЕРГНУТ"} and (
            not isinstance(reasoning, str) or not reasoning.strip()
        ):
            raise UnrecoverableJSONError(
                ValueError("для вердикта требуется непустое reasoning"), stop_reason, raw
            )
    except UnrecoverableJSONError as error:
        send_json_error_telegram(
            error,
            f"Паттерн: {html.escape(os.path.basename(filepath))}",
        )
        raise

    if verdict == "РАНО_СУДИТЬ":
        print(f"[falsify] рано судить: {os.path.basename(filepath)}")
        return None

    today_str = datetime.now().strftime("%Y-%m-%d")
    updated = pattern_content.replace("**Статус:** АКТИВНЫЙ", f"**Статус:** {verdict}")
    falsification_heading = "## Falsification" if is_english_body(pattern_content) else "## Фальсификация"
    updated += f"\n\n{falsification_heading} {today_str}\n**Вердикт:** {verdict}\n**Основание:** {reasoning}\nФАЛЬСИФИКАЦИЯ ПРОВЕДЕНА\n"

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
    print(f"[patterns] vault: {VAULT_ROOT}")

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

    recent_assessments, older_assessments = split_recent_assessments(assessments, DAYS_ASSESSMENT_BATCH)
    print(f"[patterns] оценок за последние {DAYS_ASSESSMENT_BATCH} дней (batch для кластеризации): {len(recent_assessments)}")

    existing_patterns, all_patterns, covered_files = get_existing_patterns(active_days=DAYS_PATTERN_ACTIVITY)
    print(f"[patterns] существующих паттернов: {len(all_patterns)}, активных за {DAYS_PATTERN_ACTIVITY} дней (в промпт): {len(existing_patterns)}, покрытых оценок: {len(covered_files)}")

    old_unclustered = [a for a in older_assessments if a["filename"] not in covered_files]
    if old_unclustered:
        print(f"[patterns] ВНИМАНИЕ: оценок старше {DAYS_ASSESSMENT_BATCH} дней без паттерна: {len(old_unclustered)}")

    if not recent_assessments:
        telegram_lines.append(f"\nНет оценок за последние {DAYS_ASSESSMENT_BATCH} дней для кластеризации")
        send_telegram("\n".join(telegram_lines))
        return

    print("[patterns] кластеризация через Sonnet...")
    result = cluster_with_sonnet(recent_assessments, existing_patterns, analysts)

    if result.repair_used:
        telegram_lines.append("\nВНИМАНИЕ: JSON кластеризации восстановлен после обрезки ответа")

    clusters = result.get("clusters", [])
    orphans = result.get("orphans", [])
    print(f"[patterns] кластеров: {len(clusters)}, осиротевших оценок: {len(orphans)}")

    assessments_by_filename = {a["filename"]: a for a in recent_assessments}

    created = []
    skipped = []
    for cluster in clusters:
        filename = create_pattern_file(cluster, covered_files, assessments_by_filename)
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
