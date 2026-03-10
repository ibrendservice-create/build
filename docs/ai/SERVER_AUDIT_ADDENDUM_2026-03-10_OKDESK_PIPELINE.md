# SERVER AUDIT ADDENDUM 2026-03-10 OKDESK PIPELINE

## Что проверено

- Snapshot-ожидания в `docs/ai/HANDOFF_2026-03-10.md`, `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_REMEDIATION_BACKLOG.md` и `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md` сверены с live.
- На `S1` и `S2` read-only проверены:
  - наличие кода и путей;
  - `systemctl status` и `list-unit-files` для `okdesk-pipeline`;
  - наличие live process;
  - listener `:3200`;
  - `crontab -l` на вызовы `localhost:3200` и `okdesk-pipeline`.
- На `S2` дополнительно проверены unit file и `cwd` live process.

## Live placement

- Live runtime `okdesk-pipeline` реально работает на `S2`.
- Подтверждение:
  - `okdesk-pipeline.service` active on `S2`;
  - live process `node server.mjs` работает на `S2`;
  - `WorkingDirectory` и `cwd` процесса = `/opt/apps/okdesk-pipeline`;
  - listener = `127.0.0.1:3200`;
  - cron calls на `http://localhost:3200/...` есть на `S2`.
- Evidence competing runtime на `S1` не найдено.

## Что есть на S1

- Есть только symlink `/opt/okdesk-pipeline -> /opt/apps/okdesk-pipeline`.
- Целевой dir `/opt/apps/okdesk-pipeline` отсутствует.
- `server.mjs` по ожидаемому path отсутствует.
- `okdesk-pipeline.service` отсутствует.
- Live process по `okdesk-pipeline` не найден.
- Listener `:3200` отсутствует.
- Cron calls на `localhost:3200` или `okdesk-pipeline` не найдены.
- Timers по `okdesk` не найдены.

## Что есть на S2

- Есть dir `/opt/apps/okdesk-pipeline`.
- Есть `okdesk-pipeline.service`.
- Unit `enabled` и `active`.
- `WorkingDirectory=/opt/apps/okdesk-pipeline`.
- `ExecStart=/usr/bin/node server.mjs`.
- Main PID живой, `cwd` процесса = `/opt/apps/okdesk-pipeline`.
- Listener `127.0.0.1:3200` поднят этим `node` process.
- Есть cron calls на `localhost:3200`:
  - `/api/follow-up/scan`
  - `/api/follow-up/send`
  - `/api/nudge/send`
  - `/api/dispatch/reminders/process`
  - `/api/sla/check`
- Есть S2 cron/scripts под `/opt/apps/okdesk-pipeline/...`.
- Systemd timers по `okdesk` не найдены; контур использует `cron + systemd service`.

## Docs drift или operational issue

- Это не runtime split и не competing runtime.
- Это подтверждённый `docs drift` со stale path на `S1`.
- `HANDOFF_2026-03-10.md` описывает другой контур, но live placement однозначно указывает на `S2`.
- Operational risk есть только в том, что stale `S1` path может ввести в заблуждение при будущих deploy/rollback действиях.

## Что можно исправить только в repo

- Обновлять канон и backlog так, чтобы:
  - canonical placement = `S2`;
  - live runtime source of truth = `S2 unit + S2 cron calls + S2 :3200`;
  - `S1` описывался как stale path/symlink, а не как runtime host.
- Явно помечать, что reconciliation по `okdesk-pipeline` нужно делать по live runtime host, а не по snapshot docs.

## Что требует approve

- Любые server-side изменения:
  - создание, удаление или редактирование `okdesk-pipeline.service`;
  - перенос runtime между `S1` и `S2`;
  - правка `S2 crontab`;
  - правка `S1 symlink/path`;
  - деплой кода на `S1` или `S2`;
  - restart service.
- Любые изменения `routing`, `Caddy` или `nginx` вокруг pipeline.

## Вердикт

- `WARN`
- Live placement однозначный: `okdesk-pipeline` работает на `S2`.
- Competing runtime между `S1` и `S2` не найден.
- Основная проблема сейчас: `docs drift` плюс stale `S1` path, а не active runtime conflict.
