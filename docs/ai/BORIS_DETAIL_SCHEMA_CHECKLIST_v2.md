# BORIS DETAIL SCHEMA CHECKLIST v2

```text
╔════════════════════════════════════════════════════════════════════════════════════╗
║                BORIS / OPENCLAW / BS24 — РАБОЧАЯ СХЕМА-ЧЕКЛИСТ                    ║
║                weekly audit + change plan, top-down, from critical to minor       ║
╠════════════════════════════════════════════════════════════════════════════════════╣
║ ПОРЯДОК ЧТЕНИЯ                                                                    ║
║ 1. Сначала source of truth                                                         ║
║ 2. Потом live/runtime                                                              ║
║ 3. Идти сверху вниз                                                                ║
║ 4. Если стоп на уровне N, выше N не считать надёжным                              ║
╚════════════════════════════════════════════════════════════════════════════════════╝
```

Рабочая схема для Бориса.
Назначение: один документ для weekly audit и для change plan.

Основа:
- repo canon и baseline;
- внешний `Boris-Detail-Schema.txt` как snapshot structure;
- внешний `BS24-MASTER-PLAN-v2.0.md` как business intent.

Правило чтения:
- идти сверху вниз;
- если стоп на текущем уровне, выше не подниматься;
- сначала source of truth, потом runtime;
- snapshot и внешние схемы не повышать до live master без аудита.

## Визуальная карта системы

```text
КЛИЕНТЫ / КООРДИНАТОРЫ / ТЕХНИКИ / EMAIL / OKDESK
                    |
                    v
     PUBLIC EDGE / DELIVERY ENTRY
     S1 nginx + S2 Caddy + canonical public probes
                    |
         +----------+-----------+
         |                      |
         v                      v
   WEBHOOK / HOOKS         UI / API / BRIDGE-HA
   Telegram / Okdesk       n8n / bridge delivery
         |                      |
         +----------+-----------+
                    |
                    v
          BORIS / OPENCLAW BOT ON S1
          internal container + scripts + skills + cron runtime
                    |
      +-------------+-------------+-------------------+
      |                           |                   |
      v                           v                   v
  Bridge / models            Memory / rules       Local Boris PG
  Claude/OpenAI path         RULES.md + storage   emails / sync contour
      |                           |                   |
      +-------------+-------------+-------------------+
                    |
                    v
              BS24 INTEGRATIONS ON S2
         n8n + PostgreSQL + Docling + okdesk-pipeline
                    |
                    v
          BUSINESS LOOP / DISPATCH / FOLLOW-UP
```

## Карта OpenClaw-Бота

```text
OPENCLAW / BORIS (S1)
|
+-- Container runtime
|   `-- openclaw-kbxr-openclaw-1
|
+-- Brain / policy
|   +-- RULES.md  -> /data/.openclaw/workspace/memory/RULES.md
|   +-- CLAUDE.md -> operational context only
|   `-- openclaw.json / model layers / startup protection
|
+-- Skills / tools / scripts
|   +-- skills = orchestration layer
|   +-- scripts = heavy business logic
|   `-- cron/jobs = background automation layer
|
+-- Delivery
|   +-- Telegram
|   +-- /hooks/
|   +-- Agent Bridge
|   `-- bridge-ha / public ingress path
|
+-- Data
|   +-- local Boris PG on S1
|   +-- memory / mem_events / emails contour
|   `-- S2 -> S1 sync contour
|
`-- Dependencies below/around
    +-- Bridge / OAuth / model routing
    +-- nginx / Caddy / ingress
    +-- monitoring / self-healing
    `-- S2 services: n8n, DB, Docling, okdesk-pipeline
```

## Уровни сверху вниз

```text
УРОВЕНЬ 1  Критичный фундамент              блоки 1-4
УРОВЕНЬ 2  Core runtime                     блоки 5-8
УРОВЕНЬ 3  Delivery и control               блоки 9-11
УРОВЕНЬ 4  BS24 integrations                блоки 12-13
УРОВЕНЬ 5  Business loop / roadmap boundary блок 14
```

## Legend

- `critical foundation` = без этого верхние уровни не валидны
- `watch item` = не авария, но weekly контроль обязателен
- `legacy noise` = не current live dependency, но может шуметь
- `do-not-touch` = contour только с explicit approve

## Критичный фундамент

```text
══════════════════════════════════════════════════════════════════════════════════════
УРОВЕНЬ 1 — КРИТИЧНЫЙ ФУНДАМЕНТ
servers / ingress / core services / Boris PG data plane
══════════════════════════════════════════════════════════════════════════════════════
```

### Блок 1. Серверы, SSH, базовая связность
- Что это: `S1`, `S2`, SSH, hostname, uptime, disk, memory, ключевые listening ports.
- Зачем это для BS24: без серверов и связности не работают Борис, pipeline, workflows, dispatch.
- Source of truth: `docs/ai/BASELINE_2026-03-10.md`, `docs/ai/OPERATING_CONSENSUS.md`, dated audit docs по `S1/S2`.
- Live fact / expected state:
  - `S1` = Boris/OpenClaw/bridges/nginx/local PG
  - `S2` = n8n/PostgreSQL/Caddy/pipeline/docling
  - `S1 -> S2` сеть рабочая; alias drift не равен network failure
- Как проверять:
  - SSH до `S1` и `S2`
  - `hostname`, `uptime`, `df -h /`, `free -h`
  - `ss -ltnp` по ключевым портам
- Stop condition:
  - нет SSH на нужный host
  - отсутствует ключевой runtime port
  - network/host expectation не совпадает с каноном
- Что нельзя трогать:
  - firewall
  - routing
  - cloud/network settings
  - SSH daemon
- Типичные drift / known issues:
  - alias drift `ssh s2`
  - stale assumptions по портам и host placement
- Owner decision: не нужен, пока речь только о проверке.

### Блок 2. Public ingress и canonical health probes
- Что это: публичные домены, nginx/Caddy ingress, external health URLs.
- Зачем это для BS24: через ingress идут webhooks, bridge-ha, pipeline edge, UI/API.
- Source of truth: `docs/ai/SOURCE_OF_TRUTH.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BRIDGE_HA.md`, gateway addendum/docs.
- Live fact / expected state:
  - canonical public `bridge-ha` probe = `https://n8n.brendservice24.ru/bridge-ha/health`
  - `ops.brendservice24.ru/bridge-ha/*` не canonical route
  - `ops` domain активен, но `/bridge-ha/*` на нём не поддерживается
- Как проверять:
  - public `curl -kI` и body check
  - проверять не только `HTTP 200`, но и `application/json` / JSON body
  - читать live ingress blocks на `S1/S2`
- Stop condition:
  - canonical probe не даёт expected JSON
  - route mapping расходится с каноном
- Что нельзя трогать:
  - nginx
  - Caddy
  - Cloudflare/DNS
  - bridge failover routing
- Типичные drift / known issues:
  - `200 text/html` на неверном URL
  - snapshot topology вводит в заблуждение по `ops` domain
- Owner decision:
  - нужен только если владелец хочет поддерживать `/bridge-ha/*` и на `ops` domain.

### Блок 3. Core services и контейнеры
- Что это: critical systemd services и critical docker containers на `S1/S2`.
- Зачем это для BS24: это runtime-основание для Бориса, pipeline, n8n, DB, bridges.
- Source of truth: baseline, weekly audit, dated full audit.
- Live fact / expected state:
  - `S1`: `claude-bridge`, `openai-bridge`, `openclaw-agent-bridge`, `openclaw-hooks-proxy`, `nginx`, `infra-monitor`, `boris-doctor`, `fail2ban`
  - `S2`: `caddy`, `claude-bridge`, `infra-monitor`, `n8n-doctor`, `okdesk-pipeline`
  - critical containers = `Up` and healthy where health exists
- Как проверять:
  - `docker ps`
  - `systemctl is-active`
  - `systemctl show ... -p NRestarts`
  - targeted local health endpoints
- Stop condition:
  - core service inactive
  - container unhealthy / missing
  - restart loop on core contour
- Что нельзя трогать:
  - restarts критичных сервисов
  - compose changes
  - monitoring/self-healing
- Типичные drift / known issues:
  - historical restart count без active loop
  - stale failed units вне канона
- Owner decision: не нужен для read-only; нужен, если contour признан legacy и планируется apply.

### Блок 4. Boris PG data plane и S2 -> S1 sync
- Что это: local Boris PostgreSQL contour на `S1`, sync из `S2`, связанные legacy artefacts.
- Зачем это для BS24: тут живут `emails`, `mem_events`, `technicians`-related sync и operational memory/data links.
- Source of truth: `docs/ai/SOURCE_OF_TRUTH.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_PG_TUNNEL.md`, baseline.
- Live fact / expected state:
  - current Boris PG mode on `S1` = `local`
  - backend = `boris-emails-pg-1` on `172.18.0.1:15432`
  - `pg-tunnel-s2.service` не current live dependency
  - live sync `S2 -> S1` идёт через `ssh/scp` scripts
- Как проверять:
  - `systemctl status pg-tunnel-s2`
  - `ss -ltnp | grep 15432`
  - `docker inspect boris-emails-pg-1`
  - `sync-pg-from-s2.sh`, `sync-executors-from-s2.sh`, свежие sync logs
- Stop condition:
  - local PG mode/state не совпадает с каноном
  - sync contour не читается или локальный PG не отвечает
- Что нельзя трогать:
  - local PG bind / compose
  - sync scripts / crontab
  - monitoring/self-healing вокруг PG contour
- Типичные drift / known issues:
  - `pg-tunnel-s2.service` как legacy noise
  - конфликт tunnel с local PG по `172.18.0.1:15432`
- Owner decision:
  - нужен для future судьбы `pg-tunnel-s2`: contingency contour или decommission.

## Core runtime

```text
══════════════════════════════════════════════════════════════════════════════════════
УРОВЕНЬ 2 — CORE RUNTIME
bridge / OpenClaw runtime / models / prompt-memory
══════════════════════════════════════════════════════════════════════════════════════
```

### Блок 5. Bridge / OAuth / HA delivery
- Что это: Claude Bridge, OpenAI Bridge 2, bridge-ha, OAuth delivery contour.
- Зачем это для BS24: без него нет AI-classification, enrichment, QC, Boris replies и failover.
- Source of truth: baseline, `OPERATING_CONSENSUS`, gateway/model docs, dated bridge-related audits.
- Live fact / expected state:
  - local health on `S1` = `3100`, `3102`, `8443`
  - bridge-ha public probe работает через canonical `n8n` URL
  - S2 keeps fallback path to local `3100`
- Как проверять:
  - `curl` local `/health`
  - public `bridge-ha` JSON probe
  - ingress blocks for `/bridge-ha/*`, `/openai/v1/`, `/hooks/`
- Stop condition:
  - no JSON health on canonical bridge path
  - local bridge dead
  - route points to wrong backend
- Что нельзя трогать:
  - OAuth creds
  - bridge config
  - ingress and failover logic
- Типичные drift / known issues:
  - bridge instability under load
  - false-positive probe by `HTTP 200` only
- Owner decision: только если меняется supported public routing contour.

### Блок 6. OpenClaw runtime и config protection
- Что это: internal Boris container, mounts, startup cleanup, config protection chain.
- Зачем это для BS24: это core brain/runtime, где живут agent logic, scripts, cron runtime, memory writes.
- Source of truth: repo canon, baseline, model routing docs, prompt/memory docs.
- Live fact / expected state:
  - internal runtime = `openclaw-kbxr-openclaw-1`
  - config protection layered
  - runtime/generated files не master
- Как проверять:
  - container health
  - startup/patcher references
  - consistency between master files and effective runtime
- Stop condition:
  - runtime file принимается за master без доказательства
  - patcher / startup contour расходится с каноном
- Что нельзя трогать:
  - generated/runtime config напрямую
  - startup scripts
  - patchers without approve
- Типичные drift / known issues:
  - overwrite risk for runtime config on startup
  - layered source-of-truth confusion
- Owner decision:
  - нужен только для архитектурного упрощения layered contour.

### Блок 7. Model routing и cron model layer
- Что это: internal default-chain, internal cron models, external Boris chain, fixers/enforcers.
- Зачем это для BS24: неправильный слой routing ломает cron, replies, enrichment и fallback economy.
- Source of truth: `docs/ai/SOURCE_OF_TRUTH.md`, model routing addendum, baseline.
- Live fact / expected state:
  - internal default-chain master = `model-strategy.json`
  - internal cron declarative master = `model-strategy.json`
  - internal cron effective runtime = `jobs.json`
  - internal cron live model = `bridge/claude-opus-4-6`
  - external chain master = external `fix-model-strategy.py`
- Как проверять:
  - `jq` on strategy/runtime files
  - compare default-chain vs cron vs external
  - inspect fixer ownership
- Stop condition:
  - runtime file трактуется как единственный master
  - cron models расходятся с expected layer
- Что нельзя трогать:
  - model files
  - fixers
  - startup hooks
  - related cron
- Типичные drift / known issues:
  - internal cron periodic enforcer weaker than external
  - `circuit-breaker-internal.py` not SoT for cron models
- Owner decision:
  - нужен для future simplification/consolidation of routing architecture.

### Блок 8. Prompt / rules / memory source of truth
- Что это: live rules path, memory layout, prompt bootstrap.
- Зачем это для BS24: без корректного rules path Борис теряет policy, tone, commitments logic.
- Source of truth: `docs/ai/SOURCE_OF_TRUTH.md`, prompt/memory addendum, baseline.
- Live fact / expected state:
  - rules SoT on `S1` = `/data/.openclaw/workspace/memory/RULES.md`
  - `/data/.openclaw/memory` = storage/DB path
  - `.openclaw/SOUL.md` absent
  - `CLAUDE.md` not master rules source
- Как проверять:
  - path existence inside live container
  - loader/bootstrap refs
  - no unexpected second rules master
- Stop condition:
  - rules path differs from canon
  - two competing rule sources appear
- Что нельзя трогать:
  - live prompt/memory layout
  - loader paths
  - compatibility files without approve
- Типичные drift / known issues:
  - snapshot docs point to stale paths
  - confusion between rules path and storage path
- Owner decision:
  - нужен только если меняется intended rules layout.

## Delivery и control

```text
══════════════════════════════════════════════════════════════════════════════════════
УРОВЕНЬ 3 — DELIVERY И CONTROL
hooks / telegram / monitoring / cron / skills
══════════════════════════════════════════════════════════════════════════════════════
```

### Блок 9. Hooks, Agent Bridge, Telegram delivery
- Что это: delivery chain from webhooks and chats into Boris/n8n and back.
- Зачем это для BS24: это прямой operational интерфейс с координаторами, техниками и событиями Okdesk.
- Source of truth: baseline, live ingress docs, Boris detail schema, workflow canon.
- Live fact / expected state:
  - `/hooks/` route lives on `S1`
  - Telegram path uses `n8n.brendservice24.ru/webhook/...`
  - `WF8 relay` active
- Как проверять:
  - route blocks for `/hooks/`, `/webhook/`
  - health of related services
  - workflow state by exact ID
- Stop condition:
  - webhook ingress missing
  - delivery chain points to wrong host/path
- Что нельзя трогать:
  - webhook destinations
  - TG delivery logic
  - workflow flags without approve
- Типичные drift / known issues:
  - workflow labels drift vs IDs
  - ingress mental model drift between domains
- Owner decision:
  - нужен, если changing intended delivery topology.

### Блок 10. Monitoring, self-healing, doctor, heartbeat
- Что это: infra-monitor, doctors, watchdogs, heartbeats, service-guard.
- Зачем это для BS24: держит прод в живом состоянии и создаёт раннее обнаружение drift/failure.
- Source of truth: baseline, operating consensus, server-side monitoring docs where audited, change runbook.
- Live fact / expected state:
  - monitoring contour active on both servers
  - heartbeat/state updates свежие
  - self-healing не должен быть source of truth для business contours
- Как проверять:
  - `systemctl is-active`
  - `NRestarts`
  - state/heartbeat freshness
  - no unexplained failed/looping core service
- Stop condition:
  - monitoring inactive
  - heartbeat stale without explained reason
  - monitoring starts conflicting with current canonical mode
- Что нельзя трогать:
  - self-healing logic
  - sudoers
  - auto-enroll lists
  - doctor scripts
- Типичные drift / known issues:
  - monitoring may remember stale contours
  - legacy service noise can remain in health space
- Owner decision:
  - нужен, если contour is demoted to legacy or promoted to required runtime.

### Блок 11. Cron, jobs, timers, skills
- Что это: OpenClaw cron jobs, host crontab, timers, skills/tooling layer.
- Зачем это для BS24: background sync, digests, promises, memory, backup, marketplace support.
- Source of truth: baseline, weekly audit rules, source-of-truth docs, Boris schema for structural map.
- Live fact / expected state:
  - internal cron models = `bridge/claude-opus-4-6`
  - `S1` file-level `jobs.json` = 13 enabled OpenClaw jobs
  - `S1` host `crontab` = 21 active entries
  - `S1` skills workspace = 24 top-level dirs: 22 real skills + service dirs `scripts`, `snippets`
  - live plugin/tool layer confirmed by session traces + plugin files, not by old snapshot
  - stale timers already safe-disabled on `S1`
  - weekly digest may be `not yet run`, not broken
  - skills are repo/runtime tooling, not live business master by themselves
- Как проверять:
  - `/var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json`
  - `crontab -l`
  - `systemctl list-timers` / exact timers
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/skills`
  - `/var/lib/apps-data/openclaw/data/scripts`
  - recent main-agent session traces for `toolCall.name`
  - plugin files under `/data/*/openclaw.plugin.json`
- Stop condition:
  - nonzero `consecutiveErrors`
  - stale unexpected timer in active contour
  - cron schedule drift in critical sync contour
  - missing critical skill/tooling entrypoint in live contour:
    `email-handler`, `okdesk`, `find-executor`, `parse-file`, `tender-specialist`
- Что нельзя трогать:
  - cron payload models
  - jobs master/effective layers
  - timers/services without owner decision
  - helper scripts unless task is explicitly script-scope
  - plugin files and tool-routing entrypoints without approve
- Типичные drift / known issues:
  - first-run-pending vs broken cron confusion
  - timer debt vs real cron failure
  - `scripts/` и `snippets/` выглядят как skills dirs, но не являются skills
  - old snapshot name `parse-attachment` is obsolete; live skill = `parse-file`
  - file-level `jobs.json` is schedule/config layer; runtime result state must be verified separately
- Owner decision:
  - нужен для legacy timer contours and any cron redesign.

#### Live inventory — Boris tools

- Live-observed tool calls in sampled main-agent session traces on `2026-03-11`:
  - `exec`, `process`, `read`, `web_fetch`, `write`, `edit`
  - `memory_search`, `memory_get`
  - `web_search`, `browser`, `message`
  - `subagents`, `sessions_spawn`, `session_status`, `sessions_history`
  - `gateway`, `cron`, `nodes`, `canvas`
- Live plugin entrypoints present inside Boris container:
  - `/data/route-command/openclaw.plugin.json`
  - `/data/callback-forward/openclaw.plugin.json`
- Operational reading:
  - `exec` remains the main bridge from Boris to server-side helper scripts
  - plugin files confirm `route-command` and Telegram callback forwarding contour exist in live runtime
  - tools list above is `live-observed`, not guessed from old schema
- Как видеть:
  - inspect recent session traces for unique `toolCall.name`
  - inspect plugin JSON files, not just docs
- Как тестить read-only:
  - tool existence = traces + plugin files + referenced helper paths
  - do not "test visibility" by executing production-affecting tool actions

#### Live inventory — Boris skills on `S1`

- Count:
  - 22 real skills with `SKILL.md`
  - 2 service dirs without `SKILL.md`: `scripts`, `snippets`
- Active skills map:
  - Search / memory / docs:
    `clawddocs`, `search`, `memory-search`, `email-search`, `gdrive-index`, `gog`
  - Files / contracts / legal:
    `parse-file`, `contract-audit`, `contract-legal`
  - Okdesk / executors / estimates / supply:
    `okdesk`, `find-executor`, `estimate-ticket`, `estimator`, `contractor-search`, `supply-search`, `vitrina`
  - Chat / business behavior:
    `email-handler`, `tender-specialist`, `negotiation`, `humanizer`
  - Platform / status / bridge:
    `claude-bridge`, `external-status`
- Role reminders from current frontmatter:
  - `email-handler` = входящие email notifications from n8n webhook
  - `tender-specialist` = tender analysis + email dialog in TENDER chat
  - `parse-file` = universal parser for Okdesk/email attachments, URLs, base64
  - `okdesk` = issues, statuses, comments, companies, employees, digests, SLA
  - `find-executor` = executor search and feedback loop
  - `contractor-search` = multi-platform contractor lookup
  - `estimator` / `estimate-ticket` = costing and budget estimation
  - `vitrina` = Telegram-based issue marketplace / response flow
  - `external-status` = Boris External health/status check
  - `clawddocs` = local OpenClaw docs search without network
- Note:
  - `claude-bridge`, `humanizer`, `supply-search` currently do not expose a short one-line frontmatter description as clearly as the other skills; treat their names as live, but verify role from `SKILL.md` before changes
- Как видеть:
  - list dirs in `/var/lib/apps-data/openclaw/data/.openclaw/workspace/skills`
  - confirm `SKILL.md` exists for real skills
- Как тестить read-only:
  - open `SKILL.md`
  - identify linked helper scripts and dependent skills
  - verify paths exist before any apply

#### Live inventory — Boris helper layer behind skills

- Current top-level non-backup helper files in `/var/lib/apps-data/openclaw/data/scripts`: `43`
- Main groups:
  - Tender / email:
    `tender-analysis-helper.py`, `parse-tender-email.py`, `bidzaar-api.py`, `build-summary.py`, `email-search-helper.py`, `tg-send-helper.py`
  - Okdesk / executors:
    `okdesk-api-query.mjs`, `okdesk-assignee-snapshot.py`, `okdesk-comment-helper.py`, `okdesk-comment-poller.py`, `okdesk-digest-data.mjs`, `okdesk-issues-helper.py`, `executor-tracker-helper.py`, `find-executor-helper.py`, `get-statuses.mjs`
  - Prices / estimates / market:
    `estimator.py`, `generate-autoprice.py`, `check-prices.py`, `check-ozon-margin.py`, `check-ratio.py`, `market-prices.py`, `parse-pricelists.py`, `parse-pricelists-v2.py`, `sync-pricelists.sh`
  - Contracts / legal / verification:
    `contract-audit-helper.py`, `contract-parser.py`, `contract-term-monitor.py`, `check-company.py`, `check-ozdf.py`, `verify-final.py`
  - Search / memory / docs:
    `memory-search-helper.py`, `unified-search-helper.py`, `fix-docs.py`, `analyze-all-files.py`, `classify-and-fix.py`
  - Platform / health / support:
    `boris-health-check.py`, `claude-bridge-helper.py`, `dev-digest-data.mjs`, `kill-k-write.sh`
- Operational reading:
  - most business-heavy skills are `skill + script`, not pure prompt-only skills
  - when checking a skill, verify its helper script layer immediately after `SKILL.md`

#### Live inventory — OpenClaw `jobs.json` on `S1`

- Count:
  - 13 enabled jobs
  - all inspected payload models = `bridge/claude-opus-4-6`
- Current jobs:
  - `Timur Morning Digest` — `0 9 * * *` — `Europe/Moscow`
  - `Timur Evening Digest` — `0 18 * * *` — `Europe/Moscow`
  - `Commitment Checker` — `30 9,14,18 * * *` — `Europe/Moscow`
  - `okdesk-supabase-sync` — `10 6,12,18 * * *` — `Europe/Moscow`
  - `gdrive-index-sync` — `0 7 * * *` — `Europe/Moscow`
  - `HH Monitor v3 (scan+offer, 30min 07-21)` — `*/30 7-21 * * *` — `Europe/Moscow`
  - `Email morning digest` — `5 9 * * *` — `Europe/Moscow`
  - `Email evening digest` — `5 18 * * *` — `Europe/Moscow`
  - `Weekly Self-Audit` — `0 10 * * 0` — `Europe/Moscow`
  - `Price List Sync + Contract Check` — `0 4,10,16,22 * * *` — `Europe/Moscow`
  - `Дайджест развития — Штаб` — `0 10 * * 1` — `Europe/Moscow`
  - `Дайджест развития — Канал мастеров` — `0 8 * * 1` — `Europe/Moscow`
  - `okdesk-comment-monitor` — `*/10 7-22 * * *` — no explicit `tz` field in inspected JSON
- Important reading rule:
  - current file-level `jobs.json` on `S1` gives schedule/model/config
  - do not assume it alone gives full runtime result state
- Как видеть:
  - inspect `/var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json`
  - verify `enabled`, schedule expr, `payload.model`
- Как тестить read-only:
  - compare names/schedules/models with canon
  - if runtime status is needed, verify through logs/session traces/UI, not by guessing from `jobs.json`

#### Live inventory — `S1` host `crontab`

- Count:
  - 21 active entries
- Current groups:
  - Watchdogs / monitor:
    `monitor-locks.sh`, `memory-watchdog.py`, `promise-watchdog.py`, `ssh-watchdog.sh`, `watchdog-meta.sh`, `audit-structure.sh`
  - Backup / KB:
    `backup-full.sh`, `config-snapshot.sh`, `audit-backup.sh`, KB `rsync`, KB `generate_docs`, KB `run_verifications`, KB `archive_old`
  - Boris data / sync / reminders:
    `sync-executors-from-s2.sh`, `sync-pg-from-s2.sh`, `okdesk-assignee-snapshot.py`, `sync-prices-to-s2.sh`, `tender-remind-check.sh`
  - Bridges / model protection:
    `refresh-fallback.sh`, external `fix-model-strategy.py`, internal `circuit-breaker-internal.py`
- Critical host-cron items not to forget:
  - `sync-executors-from-s2.sh`
  - `sync-pg-from-s2.sh`
  - `refresh-fallback.sh`
  - external `fix-model-strategy.py`
  - internal `circuit-breaker-internal.py`
- Как видеть:
  - `crontab -l` on `S1`
- Как тестить read-only:
  - verify entry exists
  - verify target path exists
  - verify contour role before assuming it is broken or stale

## BS24 integrations

```text
══════════════════════════════════════════════════════════════════════════════════════
УРОВЕНЬ 4 — BS24 INTEGRATIONS
okdesk-pipeline / n8n / workflows / email / Docling / DB
══════════════════════════════════════════════════════════════════════════════════════
```

### Блок 12. Okdesk pipeline, dispatch, vitrina
- Что это: pipeline intake -> enrich -> dispatch contour and executors vitrina.
- Зачем это для BS24: это ядро steps 1-5 service cycle; от него зависят classification, matching, assignment prep.
- Source of truth: baseline, `SOURCE_OF_TRUTH`, okdesk addendum, BS24 master plan.
- Live fact / expected state:
  - canonical runtime host = `S2`
  - runtime SoT = `S2 unit + S2 cron calls + S2 :3200`
  - `S1` not runtime host
  - dispatch/vitrina contour depends on `S2` pipeline outputs
- Как проверять:
  - `systemctl status okdesk-pipeline`
  - `ss -ltn | grep :3200`
  - `S2` crontab for pipeline calls
  - presence of executors sync contour
- Stop condition:
  - `S2 :3200` absent
  - pipeline host/placement differs from canon
  - signs of competing runtime
- Что нельзя трогать:
  - placement
  - systemd unit
  - cron calls
  - deploy paths
- Типичные drift / known issues:
  - stale `S1` path/symlink
  - snapshot docs may still imply wrong host
- Owner decision:
  - нужен for migration, placement cleanup, or intended role change.

### Блок 13. n8n, workflows, email, Docling, DB
- Что это: n8n orchestration layer plus mail/doc parsing/data services on `S2`.
- Зачем это для BS24: это production automation for parsing, relay, dispatch, logging, document handling.
- Source of truth: baseline, workflow audit facts, gateway/docs, Boris schema, BS24 plan.
- Live fact / expected state:
  - `WF3`, `WF8 relay`, `WF10`, `Telegram Logger`, `WF Watchdog` = active
  - `WF11`, `WF8 Watchdog`, `Email Attachment Parser` = inactive
  - Docling health is internal/docker-network based, not host `:5001`
  - PostgreSQL on `S2` is available for n8n/emails contour
- Как проверять:
  - workflow state by exact ID
  - container health
  - DB readiness
  - Docling internal health
- Stop condition:
  - active workflow state differs from canon without owner decision
  - n8n stack unhealthy
  - DB unavailable
- Что нельзя трогать:
  - workflow flags
  - DB schema
  - docling/gateway routing
- Типичные drift / known issues:
  - workflow name drift vs ID
  - host-port assumptions for Docling
- Owner decision:
  - нужен for `WF11`, `WF8 Watchdog`, or any workflow state change.

## Business loop / roadmap boundary

```text
══════════════════════════════════════════════════════════════════════════════════════
УРОВЕНЬ 5 — BUSINESS LOOP / ROADMAP BOUNDARY
current live state vs target product state
══════════════════════════════════════════════════════════════════════════════════════
```

### Блок 14. BS24 service cycle and motivation layer
- Что это: 10-step service cycle, AI-package, execution/QC/follow-up/close, rating/XP/progression.
- Зачем это для BS24: это business reason why Boris exists; цель — техник как партнёр с репутацией, не просто ресурс.
- Source of truth:
  - current live baseline = repo canon and audits
  - target state / business intent = `BS24-MASTER-PLAN-v2.0.md`
- Live fact / expected state:
  - steps 1-5 largely operational
  - steps 6-10 partial / mixed maturity
  - XP/rating engine is business contour, not free-form ops tweak
- Как проверять:
  - для weekly audit: only confirm current live contours supporting steps 1-5 and partial 6-10
  - для change plan: separate current live state from target product state
- Stop condition:
  - target-state text is being used as if it were live master
  - roadmap gap is misclassified as production incident
- Что нельзя трогать:
  - product behavior by ad hoc infra change
  - motivation/rating logic without owner decision
  - Mini App / future backend assumptions as live facts
- Типичные drift / known issues:
  - mixing roadmap with current live
  - treating partial step 6-10 coverage as outage instead of maturity gap
- Owner decision:
  - нужен for product shifts: Mini App, QC expansion, follow-up automation, public reputation mechanics.

## Watch items

- `openclaw-hooks-proxy` restart history without current active loop.
- `S2` disk usage trend.
- Weekly digest `lastStatus=null` until first successful run.
- Internal cron enforcer for `jobs.json` weaker than external fixer contour.
- Partial maturity in BS24 steps 6-10: execution UX, vision QC, follow-up, closeout feedback.

## Legacy noise

- `pg-tunnel-s2.service` on `S1`.
- `ops.brendservice24.ru/bridge-ha/*` as non-canonical path.
- Stale `S1` path/symlink for `okdesk-pipeline`.
- Snapshot assumptions that contradict audited canon.

## Do-Not-Touch контуры

- Gateway / ingress / Cloudflare / reverse proxy.
- Bridge config / OAuth / failover logic.
- Monitoring / self-healing / sudoers / doctor scripts.
- Workflow live flags and workflow logic.
- `okdesk-pipeline` placement, unit, cron calls, deploy paths.
- Model routing files, fixers, startup hooks.
- Prompt / memory live layout and loader paths.
- PG/local data plane and sync scripts.

## Weekly Audit shortcuts

- Start order:
  - Блок 1 -> Блок 2 -> Блок 3 -> Блок 4
  - если всё ок, потом Блок 5 -> 13
- Minimal weekly route:
  - SSH / hostname / ports
  - core services / containers / health
  - canonical public `bridge-ha` JSON probe
  - workflow IDs
  - cron/jobs/timers
  - Boris tools/skills inventory spot-check:
    `toolCall.name` sample, plugin files, 22 skills, 13 `jobs.json` jobs, 21 host-cron entries
  - `okdesk-pipeline` placement and `:3200`
  - prompt/rules path
  - model routing layer check
- Weekly classification:
  - `ok`
  - `drift`
  - `risky`
  - `owner decision`
  - `approve`

## Change Plan shortcuts

- Before any apply:
  - identify block
  - identify SoT
  - separate live fact vs target state
  - verify blast radius below and above
- Minimal change plan template:
  - Layer
  - Block
  - Source of truth
  - What changes
  - What must not change
  - Backup
  - Apply
  - Post-check
  - Rollback
  - Risk
- Hard stop:
  - if pre-check disagrees with canon
  - if contour is listed in Do-Not-Touch and no explicit approve exists
  - if roadmap text is being used as live truth

## Skills / Cron / Heartbeat placement rules

- Tools:
  - treat built-in tools as live only when confirmed by traces, plugin files, or audited runtime docs
  - do not promote names from old schema to current canon without live evidence
  - plugin entrypoints are part of Boris contour, but not equal to business source of truth
- Skills:
  - skills are tooling layer, not live business source of truth by default
  - use them after lower-layer health is confirmed
  - skill problems do not explain infra failure until lower blocks are green
  - `scripts/` and `snippets/` in skills workspace are service dirs, not real skills
  - if a skill delegates heavy logic to `/data/scripts`, audit the helper script immediately after `SKILL.md`
- Cron:
  - separate host crontab, OpenClaw `jobs.json`, and systemd timers
  - never assume one cron file is the only master without SoT check
  - classify `not yet run` separately from `broken`
  - current file-level `jobs.json` is first of all config/schedule layer; runtime result state may live elsewhere
- Heartbeats:
  - heartbeat/state belongs to monitoring contour, not to product truth
  - heartbeat stale = monitoring signal, not automatic proof of app failure
  - cross-server heartbeat must not override direct runtime verification
- Placement:
  - `okdesk-pipeline` runtime placement = `S2`
  - Boris PG data plane on `S1` = `local`
  - canonical public `bridge-ha` probe = `n8n` domain

## Быстрый verdict rule

- Если сломан блок 1-4: это critical foundation incident.
- Если сломан блок 5-8: это core runtime incident.
- Если сломан блок 9-13: это delivery/integration incident.
- Если разъехался блок 14 без падения рантайма: это roadmap/docs boundary issue, не обязательно prod incident.
