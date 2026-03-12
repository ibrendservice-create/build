# CHANGE POLICY

Canonical default approvals: `docs/ai/DEFAULT_APPROVALS.md`.
Если task-specific scope уже или другой policy/doc строже, действует более строгая граница.

## Можно без отдельного approve
- read-only inspection в repo;
- read-only inspection на согласованных серверах и read-only SSH / `pre-check` на согласованных хостах;
- диагностика;
- health-check;
- использовать existing server-side secrets in-place для согласованных `pre-check` / `apply` / `post-check`, не раскрывая значения и не сохраняя их;
- backup;
- file-level rollback из только что созданного backup, если `post-check` не проходит;
- rollback plan;
- документация и read-only проверки;
- docs-only updates, docs-only commits и docs-only push;
- правки только в repo docs и project instruction files;
- точечный apply только в явно названном scope (`one file | one field | one job | one service contour`) и только по схеме `pre-check -> backup -> minimal apply -> post-check -> rollback on fail`;
- выравнивание канона между `AGENTS.md`, `CLAUDE.md` и `docs/ai/*`, если это не затрагивает runtime и server-side truth.
- отражение dated audit deltas в каноне repo, если правка явно ссылается на read-only audit docs и не переписывает snapshot docs как live master.
- docs-only фиксация drift между live-аудитом и snapshot docs без изменения `HANDOFF_2026-03-10.md`.

## Нельзя без явного approve
- `restart` / `reload`;
- перезапуск критичных контейнеров;
- auth/routing/gateway/bridge changes;
- monitoring/self-healing changes;
- workflow changes и изменение live workflow state;
- server-side truth вне repo;
- `rotate / revoke / create / delete` secrets / tokens / credentials;
- destructive SQL и удаление данных;
- ручная правка live `jobs.json`;
- правка generated/runtime вместо master;
- broad live refactor;
- изменения вне согласованного scope;
- переписывание `docs/ai/HANDOFF_2026-03-10.md` или внешней схемы как будто это live master.
- занесение в канон неаудированных live-фактов без `SERVER_AUDIT_REQUIRED`.

## Если документы конфликтуют
- не угадывать;
- не выбирать победителя по памяти;
- не переписывать snapshot docs как live truth;
- помечать `SERVER_AUDIT_REQUIRED`.
- если dated audit docs уже подтверждают live drift, отражать этот drift только в каноне repo и ссылаться на audit docs.
