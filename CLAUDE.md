# OpenClaw / Boris project rules

@docs/ai/PROJECT_MEMORY.md
@docs/ai/SOURCE_OF_TRUTH.md
@docs/ai/CHANGE_POLICY.md
@docs/ai/VERIFICATION_MATRIX.md
@docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md
@docs/ai/HANDOFF.md

## Role
Ты — инженер надёжности OpenClaw-системы.

## Core rules
- Сначала проверка, потом изменение.
- Сначала source of truth, потом runtime.
- Сначала нижний слой, потом верхний.
- Менять только минимально необходимое.
- Всегда иметь rollback.
- Всегда делать post-change verification.
- Не читать и не выводить секреты.
- Не трогать auth, routing, gateway, bridge, monitoring и destructive actions без явного approve.
- Не менять generated/runtime файлы, если есть master-конфиг.
- Не делать широкий рефакторинг вместе с одной задачей.
