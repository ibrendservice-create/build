# Boris / OpenClaw project rules for Codex

## Scope
- Работай только внутри этого репозитория.
- Перед началом любой задачи сначала прочитай:
  - docs/ai/PROJECT_MEMORY.md
  - docs/ai/SOURCE_OF_TRUTH.md
  - docs/ai/CHANGE_POLICY.md
  - docs/ai/HANDOFF.md

## Required workflow
1. Сначала определи слой изменения и blast radius.
2. Сначала найди source of truth.
3. Не правь generated/runtime файлы, если есть master.
4. Не смешивай задачу с широким рефакторингом.
5. Всегда готовь backup и rollback.
6. После изменений проверяй соседние контуры.

## Forbidden without explicit approval
- Не трогать auth.
- Не трогать routing.
- Не трогать gateway.
- Не трогать bridge.
- Не трогать monitoring и self-healing.
- Не делать destructive actions.
- Не менять secrets, tokens, credentials.
- Не перезапускать критичные сервисы без approve.

## Verification standard
После любого изменения проверить:
- целевой компонент;
- зависимости ниже;
- зависимости выше;
- routing и delivery;
- hooks / cron / skills, если затронуты;
- monitoring / self-healing;
- config drift;
- возможность rollback.

## Output format
Всегда отвечай кратко:
- слой;
- source of truth;
- риск;
- план;
- rollback;
- post-check;
- вердикт: SAFE / NEEDS APPROVAL / BLOCKED / RISKY.
