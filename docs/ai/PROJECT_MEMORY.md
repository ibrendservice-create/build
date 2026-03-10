# PROJECT MEMORY

## Цель
Надёжное развитие OpenClaw/Boris без поломки текущих сервисов, routing, bridge, prompts, cron, skills и monitoring.

## Базовые принципы
- сначала проверка, потом изменение;
- сначала source of truth, потом runtime;
- сначала нижний слой, потом верхний;
- минимальный change set;
- обязательный rollback;
- обязательная post-change verification;
- не читать и не выводить секреты;
- не трогать auth, routing, gateway, bridge, monitoring и destructive actions без approve.
- при конфликте snapshot docs и dated audit docs не угадывать; использовать канон repo и при необходимости помечать `SERVER_AUDIT_REQUIRED`.

## Рабочий порядок
1. Определи слой и blast radius.
2. Найди source of truth.
3. Определи, что может сломаться.
4. Дай минимальный план.
5. Подготовь rollback.
6. После изменения проверь соседние контуры.

## Проектные контуры
- Claude: CLAUDE.md + docs/ai/*
- Codex: AGENTS.md + docs/ai/*

## Audit-backed live deltas 2026-03-10
- `okdesk-pipeline` реально active на S2; это drift относительно `HANDOFF`.
- Internal cron models live = `bridge/claude-opus-4-6`.
- External live routing = `anthropic/claude-haiku-4-5 -> openai/gpt-5`.
- Live prompt/memory paths: `.openclaw/SOUL.md` отсутствует; `RULES.md` живет в `.openclaw/workspace/memory/RULES.md`.
- Live gateway/file paths: Caddyfile = `/etc/caddy/Caddyfile`; `sites-enabled` на S1 = regular files; local `8443` health = `http`.
- Live Docling доступен внутри docker-сети и не обязан публиковать host `:5001`.
- Live workflow statuses, подтвержденные аудитом: WF3 `active`, WF8 relay `active`, WF10 `active`, WF11 `inactive`, WF8 Watchdog `inactive`.
- S1 -> S2 `ssh s2` это alias-dependent path; alias drift не равен network failure.

## Как использовать эти deltas
- Это repo-visible память, основанная на read-only аудите `2026-03-10`.
- Если `HANDOFF` или внешний schema-файл расходятся с этими пунктами, считать это snapshot drift.
- Если задача зависит от более нового live-состояния, требуется `SERVER_AUDIT_REQUIRED`.
