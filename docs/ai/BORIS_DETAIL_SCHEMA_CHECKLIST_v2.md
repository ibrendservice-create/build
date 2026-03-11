# BORIS DETAIL SCHEMA CHECKLIST v2

Рабочая схема-чеклист для Бориса.
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

## Уровни

1. Критичный фундамент
2. Core runtime
3. Delivery и control
4. BS24 integrations
5. Business loop / roadmap boundary

## Критичный фундамент

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
  - stale timers already safe-disabled on `S1`
  - weekly digest may be `not yet run`, not broken
  - skills are repo/runtime tooling, not live business master by themselves
- Как проверять:
  - `jobs.json`
  - `crontab -l`
  - `systemctl list-timers` / exact timers
  - skills count and placement only when relevant
- Stop condition:
  - nonzero `consecutiveErrors`
  - stale unexpected timer in active contour
  - cron schedule drift in critical sync contour
- Что нельзя трогать:
  - cron payload models
  - jobs master/effective layers
  - timers/services without owner decision
- Типичные drift / known issues:
  - first-run-pending vs broken cron confusion
  - timer debt vs real cron failure
- Owner decision:
  - нужен для legacy timer contours and any cron redesign.

## BS24 integrations

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

- Skills:
  - skills are tooling layer, not live business source of truth by default
  - use them after lower-layer health is confirmed
  - skill problems do not explain infra failure until lower blocks are green
- Cron:
  - separate host crontab, OpenClaw `jobs.json`, and systemd timers
  - never assume one cron file is the only master without SoT check
  - classify `not yet run` separately from `broken`
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
