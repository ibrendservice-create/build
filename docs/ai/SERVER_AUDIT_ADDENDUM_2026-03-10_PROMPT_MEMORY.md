# SERVER AUDIT ADDENDUM 2026-03-10 PROMPT MEMORY

## Что проверено

- Наличие на S1 и внутри контейнера путей:
  - `/data/.openclaw/SOUL.md`
  - `/data/.openclaw/memory/RULES.md`
  - `/data/.openclaw/workspace/memory/RULES.md`
  - `/data/CLAUDE.md`
- Поиск loader, bootstrap и runtime-ссылок на `SOUL.md`, `RULES.md`, `workspace/memory` и `CLAUDE.md` в live code и scripts на S1.
- Поиск live-следов использования этих путей в session traces и логах контейнера.
- Проверка содержимого директорий:
  - `.openclaw/memory`
  - `.openclaw/workspace/memory`

## Что найдено

- На S1 отсутствуют:
  - `/data/.openclaw/SOUL.md`
  - `/data/.openclaw/memory/RULES.md`
- На S1 существуют:
  - `/data/.openclaw/workspace/memory/RULES.md`
  - `/data/CLAUDE.md`
- `.openclaw/memory` фактически используется как storage path и содержит `main.sqlite`, а не markdown-правила.
- `workspace/memory` содержит `RULES.md`, `commitments.json`, `INDEX.md`, daily memory и другие live memory files.
- В live `CLAUDE.md` и вспомогательных скриптах на S1 правила указываются как `/data/.openclaw/workspace/memory/RULES.md`.
- В runtime/session traces есть обращения именно к `/data/.openclaw/workspace/memory/RULES.md`.
- Признаков, что runtime падает из-за отсутствия `.openclaw/SOUL.md` или `.openclaw/memory/RULES.md`, не найдено.
- В runtime dist `SOUL.md` обрабатывается условно: если файл присутствует, он учитывается; обязательность для этого деплоя не подтверждена.

## Реальный source of truth

- Для live правил на S1: `/data/.openclaw/workspace/memory/RULES.md`
- `CLAUDE.md` на S1 не является master-источником правил; он ссылается на `workspace/memory/RULES.md`.
- `.openclaw/memory/RULES.md` не является live source of truth.
- `.openclaw/SOUL.md` не подтверждён как обязательный runtime master для текущего деплоя.

## Это docs drift или runtime issue

- Текущее состояние выглядит как `docs drift`, а не активная runtime-проблема.
- `HANDOFF_2026-03-10.md` в этой части описывает устаревшие пути для `SOUL.md` и `RULES.md`.
- Реального loader failure по отсутствующим путям аудит не показал.

## Что можно исправить только в repo

- Держать canonical docs на audited live-факте:
  - `RULES.md` живёт в `workspace/memory`
  - `.openclaw/SOUL.md` в live отсутствует
  - `.openclaw/memory` сейчас storage path, а не rules path
- Явно пометить в docs, что `HANDOFF_2026-03-10.md` в этой части содержит snapshot drift.
- Не описывать `CLAUDE.md` как source of truth правил; фиксировать его как operational context file.

## Что требует approve

- Любая server-side правка prompt/memory layout на S1.
- Любая попытка добавить или восстанавливать `.openclaw/SOUL.md`.
- Любая попытка переносить `RULES.md` между `workspace/memory` и `.openclaw/memory`.
- Любые изменения loader, bootstrap или config, которые определяют чтение prompt/memory файлов.

## Вердикт

- `WARN`
- Слой не сломан, но snapshot docs в части prompt/memory source-of-truth устарели.
