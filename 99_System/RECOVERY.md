# RECOVERY.md

**Путь назначения:** `99_System/RECOVERY.md` (vault-репозиторий, ветка `vault`)
**Статус:** финальный текст, запись в GitLab — вручную (Правило 17)

---

## Зависимости системы

- GitLab: `gitlab.com/lyolich777ka/radar` — аккаунт `lyolich777ka`, ветки `master` (скрипты) и `vault` (данные)
- Anthropic API: ключ в GitLab CI → переменная `ANTHROPIC_API_KEY`
- Telegram-бот: `@radar_architect_bot` — токен в GitLab CI → переменная `TELEGRAM_BOT_TOKEN`
- Telegram-канал: `@radar_public` — переменная `TELEGRAM_CHANNEL_ID`
- Telegram владелец (уведомления об ошибках): `TELEGRAM_OWNER_ID` (`227280271`)
- Модели: источник правды — `99_System/model_config.json`, не хардкодить

## Восстановление с нуля (цель < 1 часа)

1. Создать новый GitLab-репозиторий.
2. Скопировать ветку `master` (скрипты).
3. Создать ветку `vault`, скопировать данные из бэкапа (см. ниже).
4. Добавить CI-переменные: `ANTHROPIC_API_KEY`, `GITLAB_PUSH_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID`, `TELEGRAM_OWNER_ID` — все Masked, без Protected (Правило 8).
5. Проверить `99_System/model_config.json` — актуальность ID моделей.
6. Запустить pipeline вручную (radar job) для smoke-теста.

## Бэкап vault

Vault — ветка `vault` в GitLab (`gitlab.com/lyolich777ka/radar`). Зеркало — локальная копия на маке `~/radar/radar/` через Obsidian Git, отдельный git-репозиторий от Brain vault.

При потере GitLab: локальная копия на маке актуальна в пределах последнего пуша. Восстановление — `git remote set-url` на новый репозиторий и push веткой `vault` (Правило 9 — только с явным указанием папки).

## Ротация ключей

При компрометации `ANTHROPIC_API_KEY`:

1. Отозвать ключ на console.anthropic.com.
2. Создать новый ключ.
3. Обновить CI-переменную `ANTHROPIC_API_KEY`.
4. Проверить отсутствие старого ключа в git history (`git log -p` / `git grep` по репозиторию, обе ветки).

Аналогичная процедура применима к `TELEGRAM_BOT_TOKEN` (отзыв через `@BotFather` → `/revoke`) и `GITLAB_PUSH_TOKEN` (Access Tokens → Revoke → создать новый).

---

**Сверка с `AGENT_INSTRUCTION_radar_v5.md`:** расхождений не найдено. Имя репозитория актуально (`radar`, не `opensource-radar`), переменные CI совпадают.

Версия: 1.0 | Источник черновика: `Risk_Mitigation_Radar_v1_0.md`, Риск 4
