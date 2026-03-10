# CHANGE POLICY

## Можно без отдельного approve
- чтение файлов и конфигов;
- диагностика;
- health-check;
- backup;
- rollback plan;
- документация и read-only проверки;
- правки только в repo docs и project instruction files;
- выравнивание канона между `AGENTS.md`, `CLAUDE.md` и `docs/ai/*`, если это не затрагивает runtime и server-side truth.
- отражение dated audit deltas в каноне repo, если правка явно ссылается на read-only audit docs и не переписывает snapshot docs как live master.
- docs-only фиксация drift между live-аудитом и snapshot docs без изменения `HANDOFF_2026-03-10.md`.

## Нельзя без явного approve
- перезапуск критичных контейнеров;
- auth/routing/gateway/bridge changes;
- monitoring/self-healing changes;
- workflow changes и изменение live workflow state;
- server-side truth вне repo;
- смена токенов и секретов;
- destructive SQL и удаление данных;
- правка generated/runtime вместо master;
- широкие рефакторинги.
- переписывание `docs/ai/HANDOFF_2026-03-10.md` или внешней схемы как будто это live master.
- занесение в канон неаудированных live-фактов без `SERVER_AUDIT_REQUIRED`.

## Если документы конфликтуют
- не угадывать;
- не выбирать победителя по памяти;
- не переписывать snapshot docs как live truth;
- помечать `SERVER_AUDIT_REQUIRED`.
- если dated audit docs уже подтверждают live drift, отражать этот drift только в каноне repo и ссылаться на audit docs.
