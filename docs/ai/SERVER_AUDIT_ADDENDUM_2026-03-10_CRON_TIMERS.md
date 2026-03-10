# SERVER AUDIT ADDENDUM 2026-03-10 CRON TIMERS

Узкий read-only аудит по `Cron / timer housekeeping`.
Изменения в live не выполнялись.

## Что проверено

- Live `systemd timers` на `S1`:
  - `boris-email-router.timer`
  - `chief-doctor.timer`
- Live `systemd` metadata и unit files на `S1`:
  - `systemctl show`
  - `systemctl status`
  - `systemctl cat`
  - `journalctl`
- Live `crontab` на `S1` и `S2`.
- Live `jobs.json` на `S1`:
  - все `job` states;
  - entries с `lastStatus=null`.
- Сверка с:
  - `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`
  - `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`
  - `docs/ai/FINAL_REMAINING_ACTIONS.md`

## Что stale

### `boris-email-router.timer`
- `enabled`
- `active (elapsed)`
- `Trigger: n/a`
- `LastTriggerUSec=Mon 2026-03-09 03:59:15 UTC`
- unit file обещает запуск `every 10 minutes`

### `chief-doctor.timer`
- `enabled`
- `active (elapsed)`
- `Trigger: n/a`
- `LastTriggerUSec=Mon 2026-03-09 03:59:15 UTC`
- unit file тоже обещает запуск `every 10 minutes`

Вывод: оба timers выглядят реально stale, а не просто `disabled legacy`.

## Что harmless

### `Дайджест развития — Канал мастеров`
- `enabled=true`
- `lastRunAtMs=null`
- `lastStatus=null`
- `nextRunAtMs=1773637200000`
- это соответствует `2026-03-16 05:00:00 UTC`
- schedule = weekly cron `0 8 * * 1`, `Europe/Moscow`
- model = `bridge/claude-opus-4-6`

Вывод: по текущим данным это похоже на `еще не было первого запуска`, а не на broken cron.

## Что risky

### `boris-email-router.timer`
- риск: timer выглядит как ожидаемый periodic live-механизм, но фактически не имеет следующего запуска.
- связанный `service` сейчас `inactive (dead)` с `Result=success`, то есть это похоже не на явное падение service, а на зависший timer contour.

### `chief-doctor.timer`
- риск: timer тоже выглядит как ожидаемый periodic live-механизм, но не планирует следующий запуск.
- связанный `service` сейчас `inactive (dead)` с `Result=success`.

Общий вывод: это не чистый docs drift. Это `housekeeping debt` с `operational risk`.

## Что требует owner decision

### `boris-email-router.timer`
- Нужно подтвердить, это еще нужный periodic contour или уже legacy.
- Если contour нужен, timer сейчас выглядит broken/stale.
- Если contour не нужен, это live legacy debt, который надо отдельно выводить из системы.

### `chief-doctor.timer`
- Нужно подтвердить, это еще нужный periodic contour или уже legacy.
- Если contour нужен, timer сейчас выглядит broken/stale.
- Если contour не нужен, это live legacy debt.

### `Дайджест развития — Канал мастеров`
- Owner decision по текущим данным не требуется.
- Это не похоже на broken state; apply нужен только если владелец захочет менять intended weekly behavior.

## Что можно исправить только в repo

- Уточнить docs так, чтобы:
  - `boris-email-router.timer` и `chief-doctor.timer` были отмечены как `enabled + elapsed + no next trigger`, а не просто `stale-looking`;
  - `Дайджест развития — Канал мастеров` был отмечен как `not yet run`, а не как broken cron;
  - backlog явно разделял:
    - real timer debt;
    - harmless first-run-pending cron state.
- Зафиксировать, что на `S2` этот contour не timer-based, а crontab-based.

## Что требует approve

- Любые live changes:
  - `systemctl disable/enable/start/stop/restart` для `boris-email-router.timer` или `chief-doctor.timer`;
  - правка timer/service unit files;
  - `daemon-reload`;
  - правка `crontab`;
  - правка `jobs.json`.
- Любое server-side решение:
  - оставить timers как legacy;
  - чинить timers как active contour.

## Вердикт

- `WARN`
- Реально stale и требующие внимания:
  - `boris-email-router.timer`
  - `chief-doctor.timer`
- Harmless по текущим данным:
  - `Дайджест развития — Канал мастеров`
- Это `housekeeping debt` с `operational risk`.
- Перед любым apply по двум timers нужен `owner decision`.
