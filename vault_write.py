import os
import requests
import yaml
from datetime import date

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_OWNER_ID = os.environ.get("TELEGRAM_OWNER_ID")

FRONTMATTER_DELIMITER = "---"
HISTORY_HEADING = "## История оценок"
CANONICAL_FIELD_ORDER = [
    "status", "maturity_score", "novelty_score", "state_value", "state_confidence",
    "assertion_vector", "evidence_log", "root_commit_sha", "verdict_history",
]


def _ordered_frontmatter(frontmatter):
    """Гарантировать канонический порядок ключей схемы (status первым и т.д.),
    независимо от порядка, в котором вызывающий код собрал словарь. Неизвестные
    дополнительные ключи (если появятся в будущих фазах) идут после канонических."""
    ordered = {k: frontmatter[k] for k in CANONICAL_FIELD_ORDER if k in frontmatter}
    for k, v in frontmatter.items():
        if k not in ordered:
            ordered[k] = v
    return ordered


def parse_frontmatter(content):
    """Разобрать YAML frontmatter из уже прочитанной строки содержимого файла.
    Возвращает (frontmatter_dict, body). Если содержимое не начинается с frontmatter-блока -
    возвращает (None, content) - вызывающий код сам решает, что делать с файлом без
    frontmatter. Единственное место в проекте, разбирающее frontmatter-блок - и
    read_frontmatter(), и любой код, уже держащий содержимое файла в памяти
    (напр. telegram_post.py), используют эту функцию, а не пишут разбор заново."""
    opening = FRONTMATTER_DELIMITER + "\n"
    if not content.startswith(opening):
        return None, content

    closing = "\n" + FRONTMATTER_DELIMITER + "\n"
    end = content.find(closing, len(opening))
    if end == -1:
        return None, content

    yaml_block = content[len(opening):end]
    body = content[end + len(closing):]
    try:
        frontmatter = yaml.safe_load(yaml_block)
    except yaml.YAMLError:
        return None, content
    return (frontmatter or {}), body


def read_frontmatter(filepath):
    """Прочитать YAML frontmatter и тело файла оценки с диска. См. parse_frontmatter()."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return parse_frontmatter(content)


def write_frontmatter(filepath, frontmatter, body):
    """Точечно записать frontmatter+тело обратно в файл - единственное место в проекте,
    сериализующее YAML-блок оценки."""
    frontmatter = _ordered_frontmatter(frontmatter)
    yaml_block = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False, default_flow_style=False)
    content = f"{FRONTMATTER_DELIMITER}\n{yaml_block}{FRONTMATTER_DELIMITER}\n{body}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def _send_candidate_low_confidence_dm(filepath, narrative_line):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_OWNER_ID:
        print("[vault_write] TELEGRAM_BOT_TOKEN/TELEGRAM_OWNER_ID не заданы, уведомление не отправлено")
        return
    text = f"CANDIDATE_LOW_CONFIDENCE: {os.path.basename(filepath)}\n{narrative_line}"
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_OWNER_ID, "text": text},
            timeout=10,
        )
        if r.status_code != 200:
            print(f"[vault_write] ошибка отправки уведомления: {r.status_code} - {r.text[:200]}")
    except Exception as e:
        print(f"[vault_write] исключение при отправке уведомления: {e}")


def append_event(frontmatter, event_type, **fields):
    """Чистая функция - мутирует и возвращает frontmatter, не трогает диск.
    Единственный сейчас определённый event_type - "state_transition"
    (date, event_type, state_value, state_confidence). Схема для будущих
    event_type (license_changed/archived/release, Фаза 3b) не
    зафиксирована - **fields оставляет это открытым без переписывания
    сигнатуры позже."""
    event = {"date": date.today().strftime("%Y-%m-%d"), "event_type": event_type, **fields}
    frontmatter["evidence_log"] = list(frontmatter.get("evidence_log") or []) + [event]
    return frontmatter


def write_verdict_entry(filepath, status, narrative_line, extra_frontmatter=None,
                         body_template=None, state_value=None):
    """Единственная точка записи status+verdict_history+'## История оценок' в файл оценки -
    общая для analyze.py (первичная оценка) и update_assessments.py (переоценка). Устраняет
    Split-Brain между машиночитаемым verdict_history и человекочитаемым логом: оба поля
    обновляются одним диск-write, не двумя независимыми путями.

    Если файл ещё не существует - создаёт его целиком: extra_frontmatter (остальные поля
    схемы: maturity_score, novelty_score, assertion_vector, evidence_log, root_commit_sha)
    и body_template (весь текст тела файла, включая пустой '## История оценок') обязательны.

    Если файл существует - точечно обновляет status, добавляет запись в verdict_history и
    дописывает narrative_line в существующий '## История оценок'; extra_frontmatter и
    body_template игнорируются, остальные поля/секции не трогаются.

    state_value (Фаза 3, Decision B+) - новое LLM-суждение о lifecycle-тренде репозитория,
    None по умолчанию. Если передан - state_confidence вычисляется детерминированно из
    количества уже накопленных evidence_log-событий ДО этой записи (0 -> low, 1+ -> high,
    не LLM self-report), state_value/state_confidence пишутся во frontmatter и
    append_event() добавляет "state_transition"-событие в evidence_log. Если None (например
    confirm_candidate.py - человеческое решение, не новое LLM-суждение) - evidence_log не
    трогается вообще.

    Если status == "CANDIDATE_LOW_CONFIDENCE" - шлёт личное уведомление владельцу
    (TELEGRAM_BOT_TOKEN/TELEGRAM_OWNER_ID), независимо от того, кто вызвал функцию.

    Возвращает True при успешной записи, False при ошибке (без исключения - вызывающий код
    логирует и продолжает со следующим файлом/репозиторием).
    """
    if os.path.exists(filepath):
        frontmatter, body = read_frontmatter(filepath)
        if frontmatter is None:
            print(f"[vault_write] ОШИБКА: {filepath} существует без frontmatter, write_verdict_entry пропущен")
            return False
    else:
        if extra_frontmatter is None or body_template is None:
            print(f"[vault_write] ОШИБКА: {filepath} не существует, но extra_frontmatter/body_template не переданы")
            return False
        frontmatter = dict(extra_frontmatter)
        body = body_template

    today = date.today().strftime("%Y-%m-%d")
    frontmatter["status"] = status
    history = list(frontmatter.get("verdict_history") or [])
    history.append({"date": today, "verdict": status})
    frontmatter["verdict_history"] = history

    if state_value is not None:
        prior_count = len(frontmatter.get("evidence_log") or [])
        state_confidence = "high" if prior_count >= 1 else "low"
        frontmatter["state_value"] = state_value
        frontmatter["state_confidence"] = state_confidence
        append_event(frontmatter, "state_transition",
                      state_value=state_value, state_confidence=state_confidence)

    if HISTORY_HEADING in body:
        body = body.replace(HISTORY_HEADING, f"{HISTORY_HEADING}\n{narrative_line}", 1)
    else:
        body = body.rstrip("\n") + f"\n\n{HISTORY_HEADING}\n{narrative_line}\n"

    write_frontmatter(filepath, frontmatter, body)

    if status == "CANDIDATE_LOW_CONFIDENCE":
        _send_candidate_low_confidence_dm(filepath, narrative_line)

    return True
