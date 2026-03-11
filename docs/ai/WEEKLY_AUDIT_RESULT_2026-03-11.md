# WEEKLY AUDIT RESULT 2026-03-11

> Filename requested by task: `2026-03-11`
> Runtime checks actually executed: `2026-03-11`
> Mode: `read-only`

## Что проверено

- SSH до `S1` и `S2` с локальной машины; отдельно подтвержден `S1 -> ssh s2`.
- `hostname`, `uptime`, `df -h /`, `free -h`, ключевые listening ports на `S1` и `S2`.
- Critical docker containers, critical systemd services, `NRestarts`, failed units.
- Local health endpoints:
  - `S1 http://127.0.0.1:3100/health`
  - `S1 http://127.0.0.1:3102/health`
  - `S1 http://127.0.0.1:8443/health`
  - `S2 http://127.0.0.1:3100/health`
  - `S2 -> S1 http://187.77.74.126:8443/health`
- External bridge/gateway probe по audit checklist:
  - `https://n8n.brendservice24.ru/bridge-ha/health`
- `nginx` / `Caddy` path assumptions и live route blocks.
- Workflow live state по exact workflow IDs.
- `jobs.json`, stale timers, `lastStatus=null`, `consecutiveErrors`.
- `okdesk-pipeline` placement, `:3200`, `S2 crontab`, `n8n/docling/db/cache` container health.
- Prompt / memory paths внутри live internal container.
- Model routing layering:
  - internal `model-strategy.json`
  - internal `openclaw.json`
  - internal `jobs.json`
  - external `fix-model-strategy.py`
  - external `openclaw.json`

## Что ок

- Доступы:
  - `S1` reachable, hostname = `srv1373331.hstgr.cloud`
  - `S2` reachable, hostname = `6612399-hf274138.twc1.net`
  - `S1 -> ssh s2` работает
- Базовое состояние:
  - `S1` uptime = `1 day, 19h`, disk `/` = `49%`
  - `S2` uptime = `13 days, 7h`, disk `/` = `71%`
  - ключевые ports на обоих серверах соответствуют baseline:
    - `S1`: `22`, `80`, `443`, `8443`, `3100`, `3102`, `15432`
    - `S2`: `22`, `80`, `443`, `5678`, `15432`, `3200`, `3300`, `3301`
- Контейнеры и сервисы:
  - `S1`: `openclaw-kbxr-openclaw-1`, `openclaw-ext-openclaw-1`, `boris-emails-pg-1` = `Up` + `healthy`
  - `S2`: `app-n8n-1`, `app-n8n-worker-1`, `app-db-1`, `app-cache-1`, `app-docling-1`, `bs24-api`, `bs24-miniapp` и converter containers = `Up`; health checks у monitored containers = `healthy`
  - critical services active:
    - `S1`: `claude-bridge`, `openai-bridge`, `openclaw-agent-bridge`, `openclaw-hooks-proxy`, `nginx`, `infra-monitor`, `boris-doctor`, `fail2ban`
    - `S2`: `caddy`, `claude-bridge`, `infra-monitor`, `n8n-doctor`, `okdesk-pipeline`
  - на `S2` failed units не найдено
- Bridge / gateway:
  - `S1` local health endpoints возвращают `{"status":"ok"}`
  - canonical external probe `https://n8n.brendservice24.ru/bridge-ha/health` возвращает `200 application/json`
  - upstreams живы:
    - `S2 http://127.0.0.1:3100/health` = `ok`
    - `S2 -> S1 http://187.77.74.126:8443/health` = `ok`
  - live paths соответствуют baseline:
    - `Caddyfile` = `/etc/caddy/Caddyfile`
    - `S1 /etc/nginx/sites-enabled/n8n-public-edge` = regular file
    - `/hooks/` на `S1` указывает на `172.18.0.2:18790/hooks/`
- Workflows:
  - `WF3` = `active`
  - `WF8 relay` = `active`
  - `WF10` = `active`
  - `Telegram Logger` = `active`
  - `WF Watchdog` = `active`
  - `WF11` = `inactive`
  - `WF8 Watchdog` = `inactive`
  - `Email Attachment Parser` = `inactive`
- Cron / jobs / timers:
  - `boris-email-router.timer` = `disabled + inactive`
  - `chief-doctor.timer` = `disabled + inactive`
  - `jobs.json`: `nonzero_errors=0`
  - единственный `lastStatus=null` = `Дайджест развития — Канал мастеров`
  - у weekly digest `nextRunAtMs` уже задан; это по-прежнему выглядит как `not yet run`, а не broken cron
- Pipeline / integrations:
  - `okdesk-pipeline.service` на `S2` = `active/running`
  - `WorkingDirectory=/opt/apps/okdesk-pipeline`
  - listener `127.0.0.1:3200` есть на `S2`
  - `S2 crontab` по `localhost:3200` и `/opt/apps/okdesk-pipeline/...` на месте
  - `app-n8n-1`, `app-docling-1`, `app-db-1`, `app-cache-1` = `healthy`
  - `docker exec app-db-1 pg_isready -U postgres -d n8n` = accepting connections
- Prompt / memory:
  - внутри live internal container:
    - `MISSING /data/.openclaw/SOUL.md`
    - `MISSING /data/.openclaw/memory/RULES.md`
    - `EXISTS /data/.openclaw/workspace/memory/RULES.md`
    - `EXISTS /data/CLAUDE.md`
  - `.openclaw/memory` содержит `main.sqlite`, то есть выглядит как storage path
- Model routing:
  - internal cron master в `model-strategy.json` = `bridge/claude-opus-4-6`
  - internal `jobs.json` models = `bridge/claude-opus-4-6`
  - internal `openclaw.json` default-chain по-прежнему включает `bridge/claude-sonnet-4-6`
  - external fixer constants:
    - primary = `anthropic/claude-haiku-4-5`
    - fallback = `openai/gpt-5`
  - external `openclaw.json` отражает тот же live chain

## Что drift

- На `S1` есть server-side unit `pg-tunnel-s2.service`, которого нет в repo canon:
  - unit = `disabled + failed`
  - причина падения: `bind [172.18.0.1]:15432: Address already in use`
  - это выглядит как unmanaged stale contour, а не как baseline feature
- По public `bridge-ha` URL есть docs ambiguity:
  - canonical probe из audit checklist `https://n8n.brendservice24.ru/bridge-ha/health` = `OK`
  - probe на `https://ops.brendservice24.ru/bridge-ha/health` возвращает `200 text/html`
  - пока это трактуется как `docs drift / contour ambiguity`; для apply по ops-domain нужен `SERVER_AUDIT_REQUIRED`

## Что risky

- `pg-tunnel-s2.service` оставляет `failed` unit на `S1`:
  - это не ломает текущий baseline, потому что unit `disabled`
  - но это operational noise и источник будущей путаницы вокруг PostgreSQL connectivity
- `openclaw-hooks-proxy.service` сейчас `active`, но `NRestarts=5`:
  - по `journalctl` рестарты были `2026-03-10 10:41-10:42 UTC`
  - после `2026-03-10 10:42:37 UTC` сервис стоит стабильно, то есть active loop сейчас не подтвержден
  - это watch item, а не текущий incident
- `S2` disk usage = `71%`:
  - это не drift против baseline
  - это operational watch item, который weekly audit должен держать в поле зрения

## Что требует owner decision

- Решить, что делать с `pg-tunnel-s2.service`:
  - это ещё нужный contour или уже legacy debt
  - пока repo canon его не описывает
- Решить, должен ли `ops.brendservice24.ru/bridge-ha/*` оставаться supported public route:
  - сейчас для weekly health canonical external probe подтвержден только на `n8n.brendservice24.ru`
  - для apply без owner decision этот contour не трогать

## Что можно исправить только в repo

- Явно зафиксировать в weekly/ops docs, что canonical external probe для `bridge-ha` сейчас = `https://n8n.brendservice24.ru/bridge-ha/health`.
- Отразить, что `pg-tunnel-s2.service` сейчас выглядит как unmanaged stale server-side artefact, а не repo-backed baseline contour.
- Отразить weekly watch item по `openclaw-hooks-proxy`:
  - рестарты были
  - активного loop на дату `2026-03-11` не подтверждено

## Что требует approve

- Любые server-side действия по `pg-tunnel-s2.service`:
  - `enable/disable/start/stop/restart`
  - редактирование unit
  - cleanup server-side artefact
- Любые gateway / Caddy / nginx / bridge changes вокруг `bridge-ha`, `/hooks`, `8443`, reverse-proxy paths или failover logic.
- Любые server-side изменения `okdesk-pipeline` placement, service, cron calls, deploy paths или restart.
- Любые live changes model routing:
  - `model-strategy.json`
  - internal/external `openclaw.json`
  - `jobs.json`
  - fixer / circuit-breaker scripts
- Любые server-side изменения prompt/memory layout, loader paths или восстановление `SOUL.md`.

## Вердикт

- Weekly status = `WARN`
- Блокирующих runtime `FAIL` не найдено.
- Baseline `2026-03-10` в основном сохраняется.
- Новые weekly attention points:
  - `pg-tunnel-s2.service` как stale failed unit вне repo canon
  - `openclaw-hooks-proxy` restart history без текущего active loop
  - docs ambiguity по public `bridge-ha` URL
