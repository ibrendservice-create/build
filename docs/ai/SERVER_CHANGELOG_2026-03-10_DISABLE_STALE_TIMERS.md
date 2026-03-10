# SERVER CHANGELOG 2026-03-10 DISABLE STALE TIMERS

## Что было не так

- На `S1` два timers были подтверждены как stale:
  - `boris-email-router.timer`
  - `chief-doctor.timer`
- Оба находились в состоянии:
  - `enabled`
  - `active (elapsed)`
  - `Trigger: n/a`
  - `LastTriggerUSec=Mon 2026-03-09 03:59:15 UTC`
- Это было классифицировано как `housekeeping debt` с `operational risk`, а не как harmless docs drift.
- Owner decision:
  - оба timers = `legacy candidate`
  - `repair` не делать
  - подготовить и выполнить только `safe disable`

## Что именно отключено

На `S1` выполнено только:
- `stop boris-email-router.timer`
- `disable boris-email-router.timer`
- `stop chief-doctor.timer`
- `disable chief-doctor.timer`

Вне scope и не изменялось:
- `boris-email-router.service`
- `chief-doctor.service`
- `crontab`
- `jobs.json`
- `S2`
- `daemon-reload`

## Путь к backup

- `/root/backup/timer-disable-20260310-234654`

Backup содержит:
- timer unit files
- service unit files
- pre-state snapshot
- `systemctl list-timers --all` до apply

## Pre-check

Pre-check совпал с аудитом `2026-03-10`, apply не был остановлен.

### `boris-email-router.timer`
- `ActiveState=active`
- `SubState=elapsed`
- `UnitFileState=enabled`
- `LastTriggerUSec=Mon 2026-03-09 03:59:15 UTC`
- `NextElapseUSecRealtime=` empty

### `chief-doctor.timer`
- `ActiveState=active`
- `SubState=elapsed`
- `UnitFileState=enabled`
- `LastTriggerUSec=Mon 2026-03-09 03:59:15 UTC`
- `NextElapseUSecRealtime=` empty

### Related services before apply
- `boris-email-router.service` = `inactive (dead)`
- `chief-doctor.service` = `inactive (dead)`

## Post-check

Post-check прошёл.

### `systemctl is-enabled`
- `boris-email-router.timer` = `disabled`
- `chief-doctor.timer` = `disabled`

### `systemctl is-active`
- `boris-email-router.timer` = `inactive`
- `chief-doctor.timer` = `inactive`

### `systemctl status`
- оба timers = `inactive (dead)`
- в journal зафиксировано:
  - `Deactivated successfully`
  - `Stopped ...timer`

### Related services after apply
- `boris-email-router.service` = `inactive (dead)`
- `chief-doctor.service` = `inactive (dead)`

## Rollback required or not

- `Rollback required` = `no`
- Причина: pre-check совпал с аудиторным состоянием, apply прошёл узко и post-check подтвердил ожидаемый результат.

## Итог

- `successful`
