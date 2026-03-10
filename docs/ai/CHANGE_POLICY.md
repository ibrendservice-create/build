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

## Если документы конфликтуют
- не угадывать;
- не выбирать победителя по памяти;
- не переписывать snapshot docs как live truth;
- помечать `SERVER_AUDIT_REQUIRED`.
