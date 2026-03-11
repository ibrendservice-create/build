# OBSERVER DOCTOR MVP

Дата: 2026-03-11
Статус: implemented in repo, manual-only

## Что создано

- `observer-doctor` реализован как `skill + script` внутри repo.
- Это observer-only MVP для ручного read-only отчёта по infra liveness и BS24 business-liveness.
- Контур намеренно не превращён в `cron`, `heartbeat`, `workflow` или auto-repair.

## File layout

- skill: `.openclaw/workspace/skills/observer-doctor/SKILL.md`
- script: `scripts/observer_doctor.py`
- decision doc: `docs/ai/DOCTOR_AGENT_DECISION.md`
- this doc: `docs/ai/OBSERVER_DOCTOR_MVP.md`

## Operating mode

- `manual only`
- `read-only`
- `report only`
- `no auto-repair`

## Что именно проверяет

### Infra liveness

- audited core services на `S1` и `S2`
- critical containers на `S2`
- presence/freshness already existing heartbeat/state signals:
  - `S1` infra heartbeat/state files
  - `S2` business `.hb` files
- canonical public `bridge-ha` probe:
  - only `https://n8n.brendservice24.ru/bridge-ha/health`
  - valid only with `application/json` / JSON body
- `okdesk-pipeline.service` и listener `:3200` на `S2`

### BS24 business-liveness

- canonical workflow state по exact workflow IDs:
  - `WF3`
  - `WF8 relay`
  - `WF10`
  - `Telegram Logger`
  - `WF Watchdog`
  - `WF11`
  - `WF8 Watchdog`
  - `Email Attachment Parser`
- freshness of existing business heartbeat files:
  - `sla-check.hb`
  - `nudge-send.hb`
  - `followup-scan.hb`
  - `followup-send.hb`
  - `dispatch-reminders.hb`
- derived dispatch liveness rollup:
  - pipeline up
  - listener `:3200` up
  - workflows match canon
  - business heartbeat signals fresh within conservative threshold

## Что не трогает

- no restart
- no rollback
- no re-register
- no payload replay
- no activate/deactivate workflow
- no writes to existing heartbeat/state files
- no writes to:
  - `openclaw.json`
  - `jobs.json`
  - `RULES.md`
  - `CLAUDE.md`
  - `SKILL.md`
  - `commitments.json`
- no changes to:
  - `routing`
  - `workflows`
  - `bridge`
  - `monitoring`
  - `model files`
  - `jobs`
  - `auth`
  - `gateway`

## Как безопасно запускать

Локально в repo:

```bash
python3 scripts/observer_doctor.py --mode infra --format pretty
python3 scripts/observer_doctor.py --mode business --format pretty
python3 scripts/observer_doctor.py --mode full --format pretty
```

Safe live-check без deploy и без установки на `S1`:

```bash
ssh s1 'PYTHONDONTWRITEBYTECODE=1 python3 -B - --mode full --format pretty --timeout-sec 5 --ssh-connect-timeout-sec 5' < scripts/observer_doctor.py
```

Safe JSON report:

```bash
ssh s1 'PYTHONDONTWRITEBYTECODE=1 python3 -B - --mode full --format json --timeout-sec 5 --ssh-connect-timeout-sec 5' < scripts/observer_doctor.py
```

## Какие WARN сейчас считаются нормальными

Ниже только dated snapshot по safe live-check `2026-03-11T05:35:26Z`.
Для более позднего live-состояния нужен новый safe live-check; не считать это вечной live truth.

- `s2.hb.nudge_send`
  - current reason: heartbeat file present, but older than conservative `3600s` threshold
- `s2.hb.followup_scan`
  - current reason: heartbeat file present, but older than conservative `3600s` threshold
- `s2.hb.followup_send`
  - current reason: heartbeat file present, but older than conservative `3600s` threshold
- `s2.dispatch_liveness`
  - current reason: derived `WARN`, because pipeline/listener/workflows are `OK`, but part of business heartbeat signals are stale under the conservative threshold

На том же safe live-check:

- `public.bridge_ha.json` = `OK`
- `s2.hb.sla_check` = `OK`
- `s2.hb.dispatch_reminders` = `OK`
- `FAIL` not observed

## Почему эти WARN не считаются жёстким incident by default

- business heartbeats относятся к monitoring/business-liveness signal, а не к semantic business truth
- threshold intentionally conservative
- exact per-job cadence не подтверждён в repo docs для каждого heartbeat отдельно
- поэтому stale/missing business heartbeat в MVP идёт в `WARN`, а не в automatic `FAIL`
