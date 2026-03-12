# DEFAULT APPROVALS

## Canon
- Этот файл является каноническим default-approvals слоем для repo docs, project instructions и operational workflow.
- Если task-specific scope уже, чем default approvals, действует более узкий scope.
- Если более высокий policy/doc запрещает действие, default approvals это не переопределяет.
- Если документы конфликтуют, применять более строгую границу и помечать `SERVER_AUDIT_REQUIRED`.

## По умолчанию разрешено
- read-only inspection в repo;
- read-only inspection на согласованных серверах;
- read-only SSH и `pre-check` на согласованных хостах;
- использовать уже существующие server-side `tokens / API keys / cookies / env secrets / existing secret-store values`, если без этого нельзя выполнить `pre-check`, `apply` или `post-check`;
- всегда делать backup перед apply;
- делать file-level rollback из только что созданного backup, если `post-check` не проходит;
- делать docs-only updates, docs-only commits и docs-only push;
- делать точечный apply только в явно названном scope:
  - один файл;
  - один field;
  - один job;
  - один service contour;
  - только по схеме `pre-check -> backup -> minimal apply -> post-check -> rollback on fail`.

## Ограничения на секреты
- не выводить значения в ответе;
- не печатать значения в `stdout/stderr`, если это не требуется самим безопасным использованием;
- не сохранять значения в repo, docs, changelog, temp files или shell history намеренно;
- не менять существующие секреты;
- не создавать новые секреты;
- не просить пользователя вручную вставлять секрет в чат, если его можно безопасно использовать из existing server-side source;
- если секрет нельзя безопасно использовать без раскрытия значения, остановиться и зафиксировать это как blocker.

## Без отдельного approve нельзя
- `restart` / `reload`;
- workflow changes и live workflow state;
- `routing / bridge / gateway / auth`;
- `monitoring / self-healing`;
- broad live refactor;
- destructive actions;
- `rotate / revoke / create / delete` secrets / tokens / credentials;
- ручные правки live `jobs.json`;
- изменения вне согласованного scope.

## Operational notes
- Перед live apply сначала определить `source of truth`, `master`, `derived/runtime`, `writers/enforcers` и их trigger chain.
- Если writer/enforcer может перезаписать target, runtime нельзя патчить напрямую без явного плана по writer layer.
- Default approvals ускоряют стандартные узкие задачи, но не расширяют blast radius и не заменяют pre-check/post-check discipline.
