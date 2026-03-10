# SERVER AUDIT RESULT 2026-03-10 FULL

## Summary
- Общий статус = `WARN`.
- Блокирующих `FAIL` на слоях 2-8 не найдено.
- Главный риск = drift между live и snapshot docs.
- Сетевой вопрос `S1 -> S2` после low-risk fix помечен как resolved alias drift, а не как активная network problem.

## Слой: контейнеры и процессы
**Что проверено**
- `docker ps` на S1 и S2.
- `systemctl --state=running` на S1 и S2.
- `docker inspect` health для критичных контейнеров.

**Что найдено**
- На S1 все 3 ожидаемых контейнера `Up` и `healthy`.
- На S2 весь n8n/DB/Redis/Docling/BS24 stack `Up`, health нормальный.
- На S1 активны `claude-bridge`, `openai-bridge`, `openclaw-agent-bridge`, `openclaw-hooks-proxy`, `nginx`, `infra-monitor`, `boris-doctor`.
- На S2 активны `caddy`, `claude-bridge`, `infra-monitor`, `n8n-doctor`, `okdesk-pipeline.service`.

**Красные флаги**
- Live противоречит snapshot docs: `okdesk-pipeline.service` реально запущен на S2, а не "не развернут".

**PASS / WARN / FAIL**
- `WARN`

## Слой: model routing
**Что проверено**
- Наличие `model-strategy.json`, internal `openclaw.json`, `jobs.json`, external `openclaw.json`.
- Safe `jq` по model-полям без чтения секретов.

**Что найдено**
- Internal `model-strategy.json` живой: primary=`bridge/claude-sonnet-4-6`, fallbacks=`gpt-5/codex/...`.
- Internal `openclaw.json` отражает эту default-chain.
- В `jobs.json` 13 cron jobs, и все явно используют `bridge/claude-opus-4-6`.
- External live routing = `anthropic/claude-haiku-4-5 -> openai/gpt-5`.

**Красные флаги**
- Live расходится с snapshot docs: internal crons не `claude-sonnet-4-6`, а `claude-opus-4-6`.
- External Boris не `gpt-4o/codex`, а `haiku -> gpt-5`.
- Source of truth для cron split: defaults живут в strategy/openclaw, а cron model override живет в `jobs.json`.

**PASS / WARN / FAIL**
- `WARN`

## Слой: prompts / memory / skills
**Что проверено**
- Наличие `SOUL.md`, `CLAUDE.md`, memory dirs.
- `RULES.md` по двум путям.
- Counts по skills и scripts.
- Telegram mention settings из internal `openclaw.json`.

**Что найдено**
- Live есть `CLAUDE.md`, `.openclaw/memory`, `.openclaw/workspace/memory`, `workspace/memory/RULES.md`.
- Есть 22 `SKILL.md` и 50 scripts.
- Mention patterns и policies читаются нормально.

**Красные флаги**
- `.openclaw/SOUL.md` отсутствует.
- `.openclaw/memory/RULES.md` отсутствует.
- Фактический live-путь правил = `workspace/memory/RULES.md`, что расходится со snapshot docs.

**PASS / WARN / FAIL**
- `WARN`

## Слой: bridge / gateway
**Что проверено**
- `systemctl is-active`.
- `ss -ltnp`.
- Local `/health`.
- `bridge-ha/health`.
- nginx route blocks.
- Caddy route blocks.
- Тип файлов в `sites-enabled`.

**Что найдено**
- `claude-bridge`, `openai-bridge`, `agent-bridge`, `nginx`, `caddy` активны.
- `3100` и `3102` отдают `{"status":"ok"}`.
- `8443` жив, но local health отвечает по `http`, не по `https`.
- `bridge-ha` снаружи отвечает `ok`.
- nginx содержит `/openai/v1`, `/hooks`, `/webhook`.
- Caddy routes есть в `/etc/caddy/Caddyfile`.
- `/hooks` смотрит на актуальный path `172.18.0.2:18790/hooks/`.
- Последующий read-only locate показал, что active server-side checks уже используют `/etc/caddy/Caddyfile` и `http://localhost:8443/health`.
- Active checks также не требуют symlink-type для `/etc/nginx/sites-enabled/*`.

**Красные флаги**
- Для этого контура подтвержден только docs drift: snapshot assumptions про `/opt/app/Caddyfile`, symlink-only `sites-enabled` и local HTTPS на `8443` устарели.
- Active server-side misconfiguration для этих path/probe assumptions locate не подтвердил.

**PASS / WARN / FAIL**
- `WARN`

## Слой: monitoring / self-healing
**Что проверено**
- `systemctl is-active`.
- `systemctl show` с `NRestarts`.
- `journalctl -u infra-monitor -S -2h`.
- State и heartbeat files.

**Что найдено**
- На S1 активны `infra-monitor`, `boris-doctor`, `fail2ban`.
- На S2 активны `infra-monitor`, `n8n-doctor`.
- У всех проверенных сервисов `NRestarts=0`.
- Heartbeat и state обновлялись в `19:14-19:15`.
- В state есть `known_services`, `known_containers`, `last_health_report`, `hb_seen_*`.

**Красные флаги**
- Критичных runtime-флагов нет.
- Live state лежит через symlink в `/var/lib/apps-data/infra-monitor/state`, а не проверяется только по `/opt/infra-monitor/state`.
- Journal за 2 часа пуст, поэтому слой подтверждается в основном state-файлами.

**PASS / WARN / FAIL**
- `PASS`

## Слой: cron / jobs
**Что проверено**
- `crontab -l` на S1 и S2.
- Relevant `systemctl list-timers`.
- `jobs.json` length и state.
- Поиск `payload.prompt`.

**Что найдено**
- S1 crontab в целом совпадает со snapshot docs по watchdog/sync/backup/fixer задачам.
- S2 crontab содержит живые pipeline jobs на `localhost:3200`.
- `jobs.json` содержит 13 jobs.
- Почти у всех cron jobs `lastStatus=ok` и `consecutiveErrors=0`.
- Jobs с `payload.prompt` не найдены.

**Красные флаги**
- `Дайджест развития — Канал мастеров` еще ни разу не запускался (`lastStatus=null`).
- На S1 `boris-email-router.timer` и `chief-doctor.timer` есть, но без следующего запуска.
- S2 cron еще раз подтверждает, что `okdesk-pipeline` реально живой, вопреки snapshot docs.

**PASS / WARN / FAIL**
- `WARN`

## Слой: интеграции
**Что проверено**
- `okdesk-pipeline` на S1 и S2.
- Integration containers.
- Live workflow flags из PostgreSQL `n8n`.
- Counts по `emails`, `technicians`, `mem_events`.
- Host ports.
- Docling health из сети n8n.

**Что найдено**
- На S1 есть только код `/opt/okdesk-pipeline -> /opt/apps/okdesk-pipeline`, но нет unit и нет `:3200`.
- На S2 есть активный `okdesk-pipeline.service` и `127.0.0.1:3200`.
- Stack `n8n/db/cache/docling/bs24` живой.
- Live workflow flags: WF3 `active`, WF8 Boris relay `active`, WF10 `active`, Telegram Logger `active`, WF Watchdog `active`, а WF11 `inactive`, Email Attachment Parser `inactive`, WF8 Watchdog `inactive`.
- Последующий workflow-audit подтвердил эти флаги по exact workflow IDs, а не только по именам.
- Counts: `emails=39683`, `technicians=5809`, `mem_events=30203`.
- Docling отвечает `{"status":"ok"}` из docker-сети n8n.
- Host `ss` на S2 показывает `5678`, `15432`, `3200`, `3300`, `3301`, но не `5001`.
- Последующий read-only locate показал, что active checks для Docling идут через container/docker-network health и не требуют host `:5001`.

**Красные флаги**
- Главный live drift: `okdesk-pipeline` живет на S2 и работает, а snapshot docs пишут, что service не развернут.
- WF11 live `inactive`, хотя в snapshot docs он `Active`.
- WF8 Watchdog live `inactive`.
- Для `WF11` и `WF8 Watchdog` read-only аудит подтверждает docs drift, но не подтверждает runtime-аварию; перед apply нужен owner decision.
- `Email Attachment Parser inactive` совпадает между snapshot docs и live и сейчас выглядит нормой.
- Ожидание host `:5001` для Docling относится к docs drift, а не к active server-side defect.

**PASS / WARN / FAIL**
- `WARN`

## Общий статус
- `WARN`
- Реальных блокирующих `FAIL` на слоях 2-8 не найдено.
- Основной риск = не поломка live-системы, а drift между live и snapshot docs.
- Сетевой вопрос `S1 -> S2` больше не считается активной проблемой; он resolved через alias fix на S1. Детали в `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`.

## What requires approve
- Любые server-side изменения для `okdesk-pipeline`, `systemd`, `nginx`, `Caddy`, `bridge`, `routing`, `monitoring`, `self-healing`, `cron`, `timers`, `workflows`, `DB`.
- Любая правка live model routing: `model-strategy.json`, internal/external `openclaw.json`, `jobs.json`.
- Любые изменения prompt/memory source of truth на S1.
- Любой restart критичных сервисов или контейнеров.

## What can be fixed in repo only
- Обновить snapshot docs, чтобы отразить live-факт: `okdesk-pipeline` развернут и active на S2.
- Зафиксировать live model routing: internal cron = `bridge/claude-opus-4-6`, external = `claude-haiku-4-5 -> gpt-5`.
- Исправить prompt/memory paths: нет `.openclaw/SOUL.md`, `RULES.md` живет в `workspace/memory`.
- Исправить bridge/gateway docs: Caddyfile = `/etc/caddy/Caddyfile`, `8443` local health = `http`, `sites-enabled` сейчас regular files, и active checks уже соответствуют этим live-фактам.
- Исправить integration docs: active checks не требуют host `:5001` для Docling, а workflow reconciliation делать по workflow id с текущим live state: `WF11/WF8 Watchdog=inactive`, `Email Attachment Parser=inactive`.
