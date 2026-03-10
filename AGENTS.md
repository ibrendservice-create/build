# Boris / OpenClaw project rules for Codex

## Scope
Работай только внутри этого репозитория.

Перед любой задачей прочитай:

docs/ai/PROJECT_MEMORY.md
docs/ai/SOURCE_OF_TRUTH.md
docs/ai/CHANGE_POLICY.md
docs/ai/VERIFICATION_MATRIX.md
docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md
docs/ai/HANDOFF_2026-03-10.md

## Core behavior
- сначала проверка
- потом изменение
- сначала source of truth
- потом runtime
- сначала нижний слой
- потом верхний
- минимальные изменения
- всегда rollback

## Forbidden without approval
Запрещено без approve:

- auth
- routing
- gateway
- bridge
- monitoring
- destructive actions
- secrets / tokens
- restart критичных сервисов
- менять runtime вместо master

## Workflow
1 определить слой
2 найти source of truth
3 проверить риски
4 минимальный план
5 rollback
6 изменение
7 verification
8 verdict

## Output format
- слой
- source of truth
- риск
- план
- rollback
- verification
- verdict
