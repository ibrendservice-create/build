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
