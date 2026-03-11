# Boris / OpenClaw project rules for Codex

## Scope
Работай только внутри этого репозитория.

Перед любой задачей прочитай в таком порядке:
1. `docs/ai/OPERATING_CONSENSUS.md`
2. `docs/ai/PROJECT_MEMORY.md`
3. `docs/ai/SOURCE_OF_TRUTH.md`
4. `docs/ai/CHANGE_POLICY.md`
5. `docs/ai/VERIFICATION_MATRIX.md`
6. `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`
7. `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`
8. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`
9. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`
10. `docs/ai/HANDOFF_2026-03-10.md`

Внешние audit docs:
- `Boris-Detail-Schema.txt` использовать только если файл явно дан для аудита.
- Сырой `Boris-Detail-Schema.txt` не копировать в repo.

## Canon vs snapshot docs
- Канон repo: `docs/ai/OPERATING_CONSENSUS.md` и policy-файлы из `docs/ai/*`.
- Dated audit docs: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md` и `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`.
- Snapshot docs: `docs/ai/HANDOFF_2026-03-10.md` и внешний `Boris-Detail-Schema.txt`.
- При конфликте docs не угадывай и не выбирай "правильную" версию по памяти; помечай `SERVER_AUDIT_REQUIRED`.
- Если dated audit docs и snapshot docs расходятся, для уже проверенных live-фактов опирайся на канон и dated audit docs, не переписывая snapshot docs.

## Core behavior
- сначала проверка
- потом изменение
- сначала source of truth
- потом runtime
- сначала нижний слой
- потом верхний
- минимальные изменения
- всегда rollback
- обязательный post-change verification
- не читать и не выводить секреты

## Server-side config rule
- Before editing any live config, first identify:
  - source of truth
  - derived/runtime file
  - all writers/enforcers
  - their triggers
  - whether the target will be rewritten after apply
- If a writer/enforcer exists, do not patch runtime directly unless the change plan explicitly covers the writer layer too.

## Forbidden without approval
Запрещено без approve:

- auth
- routing
- gateway
- bridge
- monitoring / self-healing
- workflows и live workflow state
- server-side truth вне repo
- destructive actions
- secrets / tokens / credentials
- restart критичных сервисов
- менять runtime вместо master
- широкий refactor вне текущей задачи

## Workflow
1 определить слой и blast radius
2 прочитать канонические docs в порядке выше
3 найти source of truth
4 определить derived/runtime и writer chain
5 отделить канон от snapshot/runtime
6 проверить риски и соседние контуры
7 если docs конфликтуют -> SERVER_AUDIT_REQUIRED
8 минимальный план
9 rollback
10 изменение
11 post-check
12 verdict

## Output format
- слой
- source of truth
- риск
- план
- rollback
- post-check
- verdict
