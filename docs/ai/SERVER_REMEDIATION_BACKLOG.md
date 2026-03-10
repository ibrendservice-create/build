# SERVER REMEDIATION BACKLOG

Сводный backlog собран по итогам:
- `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`
- `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`
- `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`
- `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`

## 1. Already fixed

### S1 -> S2 alias `s2` on S1
- Проблема: исходный сетевой `FAIL` был вызван отсутствием alias `s2` на S1, хотя маршрут, TCP и SSH по IP были рабочими.
- Риск: ложные `FAIL` в аудитах, сломанные runbook-команды и неверная диагностика связности между S1 и S2.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`.
- Минимальное исправление: на S1 в `/root/.ssh/config` добавлен минимальный block `Host s2 -> HostName 72.56.98.52 -> User root`.
- Rollback: восстановить `/root/.ssh/config` из backup `/root/.ssh/config.bak-20260310-194511` или удалить только block `Host s2`.
- Post-check:
  - `ssh -G s2 | egrep "^(hostname|user) "`
  - `ssh -o BatchMode=yes s2 "hostname -f"`

## 2. Docs-only resolved

### Canon aligned with audited live drift
- Проблема: snapshot docs расходились с live-аудитом по `okdesk-pipeline`, model routing, gateway/file paths и workflow statuses.
- Риск: планирование серверных изменений по устаревшему snapshot, а не по проверенному live-состоянию.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`.
- Минимальное исправление: audited drift отражён только в canonical docs repo без переписывания `HANDOFF_2026-03-10.md` как live master.
- Rollback: откатить docs-only commits, в которых drift был перенесён в канон.
- Post-check:
  - `AGENTS.md` и `CLAUDE.md` читают один и тот же канон;
  - canonical docs отделяют audited facts от snapshot docs;
  - `HANDOFF_2026-03-10.md` не использован как live source of truth.

### Prompt / memory source-of-truth aligned in canon
- Проблема: snapshot docs описывали `.openclaw/SOUL.md` и `.openclaw/memory/RULES.md`, но live-аудит подтвердил другой rules path и отсутствие `SOUL.md`.
- Риск: неверные server-side правки prompt/memory layout и ложные предположения о runtime bootstrap.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`.
- Минимальное исправление: в canonical docs зафиксировано, что live rules source of truth на S1 = `/data/.openclaw/workspace/memory/RULES.md`, `/data/.openclaw/memory` это storage/DB path, а `CLAUDE.md` не master-источник правил.
- Rollback: откатить docs-only commit, который переносит prompt/memory drift в канон.
- Post-check:
  - canonical docs больше не описывают `CLAUDE.md` как master-источник правил;
  - отсутствие `.openclaw/SOUL.md` помечено как docs drift, а не как runtime failure;
  - server-side prompt/memory changes помечены как approve-only.

### Network diagnosis normalized in docs
- Проблема: первый полный аудит трактовал проблему `S1 -> S2` как network issue, хотя это был alias drift.
- Риск: ненужная эскалация в DNS/firewall/routing и ложные выводы о деградации сети.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`, `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`.
- Минимальное исправление: в audit docs и каноне сетевой вопрос помечен как resolved alias drift, а не как активная network problem.
- Rollback: откатить docs-only обновления audit result/addendum.
- Post-check:
  - full audit больше не содержит active network `FAIL` по `S1 -> S2`;
  - alias issue отражён как resolved;
  - runbook не смешивает alias problem и real network problem.

### Gateway / health-check assumptions resolved by audit
- Проблема: snapshot docs и ранние выводы аудита создавали впечатление, что по gateway/health assumptions нужен server-side fix.
- Риск: ненужные server-side изменения в `gateway` и `monitoring`, хотя active checks уже соответствуют live.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, read-only locate active files `/opt/infra-monitor/service-guard.py`, `/opt/infra-monitor/monitor.sh`, `/opt/n8n-doctor/doctor.py`, `/opt/app/docker-compose.yml`, `/etc/systemd/system/multi-user.target.wants/caddy.service`.
- Минимальное исправление: server-side apply не делать; держать в каноне только audited facts:
  - `Caddyfile=/etc/caddy/Caddyfile`
  - local `8443` health uses `http`
  - active checks не требуют symlink для `nginx sites-enabled`
  - active checks не требуют host `:5001` для Docling
- Rollback: откатить только docs-only updates, если потребуется вернуть backlog к состоянию до locate.
- Post-check:
  - canonical docs не требуют server-side fix для этого контура
  - gateway/Docling assumptions описаны как docs drift, не как live defect
  - backlog больше не держит этот contour в pending server-side fixes

## 3. Next server-side fixes by priority

### okdesk-pipeline canonical placement on S2
- Проблема: live показывает `okdesk-pipeline.service` active на S2, а snapshot docs описывают другой контур.
- Риск: работа не с тем runtime-host, дублирование сервиса или ошибочные rollout-действия на S1.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`.
- Минимальное исправление: формально закрепить S2 как текущий live-runtime, проверить отсутствие competing unit/process на S1 и сверить cron/endpoints, которые уже бьют в `localhost:3200` на S2.
- Rollback: вернуть исходный unit-state и любые path/service changes на S2; если трогались crons или timers, откатить их отдельно.
- Post-check:
  - `systemctl status okdesk-pipeline`
  - `ss -ltn | grep :3200`
  - health endpoint pipeline
  - S2 cron calls на `localhost:3200`

### Cron / timer housekeeping
- Проблема: `boris-email-router.timer` и `chief-doctor.timer` выглядят stale, а `Дайджест развития — Канал мастеров` в `jobs.json` ещё ни разу не запускался.
- Риск: silent failure фоновых задач, потеря автоматических проверок или ложное ощущение, что jobs реально выполняются.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`.
- Минимальное исправление: отдельно разобрать intended state для stale timers и weekly digest job; включать, удалять или чинить только после подтверждения, что это не legacy.
- Rollback: restore previous crontab, timer state и `jobs.json`.
- Post-check:
  - `systemctl list-timers`
  - `jq` state fields в `jobs.json`
  - отсутствие новых ошибок в cron/service logs

## 4. Approve-only fixes

### Model routing normalization
- Проблема: live routing split между `model-strategy.json`, internal `openclaw.json`, `jobs.json` и external `openclaw.json`; snapshot docs устарели по cron и External Boris.
- Риск: поломка internal cron, external Boris или fallback-chain при правке не того master-слоя.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`.
- Минимальное исправление: сначала зафиксировать intended cron override и intended external chain; потом при необходимости править только один master-слой за раз.
- Rollback: timestamped backup `model-strategy.json`, internal/external `openclaw.json` и `jobs.json` с возвратом исходных версий.
- Post-check:
  - `jq` на все model files
  - сравнение providers/fallbacks
  - controlled cron/manual invocation для internal и external

### Prompt / memory source-of-truth cleanup on S1
- Проблема: `.openclaw/SOUL.md` отсутствует, `RULES.md` живёт только в `workspace/memory`, а snapshot docs описывают другой layout.
- Риск: появление двух расходящихся master-paths, сломанный bootstrap или лишний compatibility layer без подтвержденной необходимости.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`, `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`.
- Минимальное исправление: сначала выбрать один server-side master-path для правил и только потом решать, нужен ли compatibility file/symlink или правка loader-path.
- Rollback: вернуть исходное дерево prompt/memory files из backup.
- Post-check:
  - agent bootstrap
  - чтение правил
  - отсутствие двух расходящихся master-файлов

### Workflow state reconciliation
- Проблема: live `WF11` и `WF8 Watchdog` inactive, хотя snapshot docs говорят обратное.
- Риск: включение или отключение не тех workflow, рассинхрон между n8n live state и operational expectations.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`.
- Минимальное исправление: сначала owner decision по intended state, потом менять только нужные `active` flags, не опираясь на snapshot docs.
- Rollback: restore предыдущих workflow states из DB snapshot/export.
- Post-check:
  - SQL по `workflow_entity`
  - n8n executions
  - watchdog/error logs

## 5. Postponed

### Миграция okdesk-pipeline между S2 и S1
- Проблема: есть docs drift по placement, но нет доказательства, что текущий S2 runtime неисправен.
- Риск: ненужная миграция работающего сервиса с большим blast radius по cron, routes и integration chain.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`.
- Минимальное исправление: отложить до отдельного архитектурного решения; не трогать placement только ради соответствия `HANDOFF`.
- Rollback: если миграция когда-то начнется, rollback = возврат unit, cron и routes на исходный сервер.
- Post-check:
  - pipeline health
  - Caddy/nginx routes
  - cron endpoints
  - `DRY_RUN` behavior

### Восстановление `.openclaw/SOUL.md` как compatibility file
- Проблема: файл отсутствует, но по аудиту нет доказанного runtime failure.
- Риск: создание лишнего compatibility path, который будет принят за обязательный source of truth без реальной потребности.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`, `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`.
- Минимальное исправление: не делать, пока не появится подтверждение, что конкретный loader реально требует этот path.
- Rollback: удалить compatibility file или symlink.
- Post-check:
  - bootstrap/prompts load
  - отсутствие duplicate-source drift
