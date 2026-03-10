# OPERATING CONSENSUS

## Purpose
Этот файл задает общий канон памяти и общий safety contour для Claude и Codex внутри этого репозитория.

## Scope
- Только repo docs и project instruction files.
- Runtime, server-side truth, live workflows и secrets находятся вне этого repo.
- `docs/ai/HANDOFF_2026-03-10.md` и внешний `Boris-Detail-Schema.txt` используются для аудита, а не как live master.

## Canonical read order
1. `docs/ai/OPERATING_CONSENSUS.md`
2. `docs/ai/PROJECT_MEMORY.md`
3. `docs/ai/SOURCE_OF_TRUTH.md`
4. `docs/ai/CHANGE_POLICY.md`
5. `docs/ai/VERIFICATION_MATRIX.md`
6. `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`
7. `docs/ai/HANDOFF_2026-03-10.md`
8. `Boris-Detail-Schema.txt` только если файл явно дан для аудита; сырой файл не копировать в repo.

## Document priority
- `AGENTS.md` и `CLAUDE.md` это agent entry points; они должны ссылаться на один и тот же канон и не расходиться по правилам проекта.
- Канон repo: этот файл плюс `docs/ai/PROJECT_MEMORY.md`, `docs/ai/SOURCE_OF_TRUTH.md`, `docs/ai/CHANGE_POLICY.md`, `docs/ai/VERIFICATION_MATRIX.md`, `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`.
- Snapshot docs: `docs/ai/HANDOFF_2026-03-10.md` и внешний `Boris-Detail-Schema.txt`.
- Live server-side truth проверяется только вне repo.

## Canon vs snapshots
- Канон определяет правила работы, safety contour и способ чтения памяти.
- Snapshot docs нужны для аудита, инвентаризации и фиксации состояния на дату снимка.
- Snapshot docs нельзя автоматически повышать до source of truth для live-системы.

## Conflict handling
- Если канон и snapshot docs расходятся, не угадывать.
- Если факта нет в repo и он относится к live-системе, не додумывать.
- В таких случаях помечать `SERVER_AUDIT_REQUIRED`.
- Не переписывать snapshot-документы в качестве live truth без server-side verification.

## Shared safety contour
- сначала проверка, потом изменение;
- сначала source of truth, потом runtime;
- сначала нижний слой, потом верхний;
- только минимальный change set;
- всегда иметь rollback;
- всегда делать post-change verification;
- не читать и не выводить секреты.

## Forbidden without explicit approve
- auth;
- routing;
- gateway;
- bridge;
- monitoring / self-healing;
- workflows и live workflow state;
- server-side truth вне этого repo;
- runtime/generated files вместо master;
- secrets / tokens / credentials;
- restart критичных сервисов или контейнеров;
- destructive actions;
- широкий refactor вне текущей задачи.

## Current unresolved contradictions
- `okdesk-pipeline`: `HANDOFF` описывает S1 и неразвернутый service, схема описывает другой live-контур; требуется `SERVER_AUDIT_REQUIRED`.
- Model routing: `HANDOFF` и схема расходятся по cron/subagent и External Boris моделям; требуется `SERVER_AUDIT_REQUIRED`.
- Workflow status snapshot: `HANDOFF` и схема расходятся по части статусов n8n workflow; требуется `SERVER_AUDIT_REQUIRED`.
