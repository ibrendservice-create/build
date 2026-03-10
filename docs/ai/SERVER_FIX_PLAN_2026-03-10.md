# SERVER FIX PLAN 2026-03-10

Ниже `low-risk` означает низкий `blast radius`. Это не отменяет общий порядок `backup -> rollback -> post-check`.

## 1. Low-risk fixes

### S1 -> S2 alias `s2`
- Что не так: ложный сетевой `FAIL` был вызван отсутствием alias `s2` на S1, хотя маршрут, TCP и SSH по IP рабочие.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`, live S1 `/root/.ssh/config`.
- Минимальное исправление: добавить на S1 user-level alias `Host s2 -> 72.56.98.52` в `/root/.ssh/config`, не трогая `/etc/hosts` и DNS.
- Rollback: удалить только этот `Host s2` block из `/root/.ssh/config`.
- Post-check: `ssh -G s2` должен показывать `hostname 72.56.98.52`; `ssh s1 'ssh -o BatchMode=yes s2 hostname -f'` должен работать.

## 2. Fixes Only With Explicit Approve

### okdesk-pipeline canonical placement
- Что не так: live показывает `okdesk-pipeline.service` active на S2, а snapshot docs описывают другой контур.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, S2 `/etc/systemd/system/okdesk-pipeline.service`, `/opt/apps/okdesk-pipeline`, `127.0.0.1:3200`.
- Минимальное исправление: не мигрировать сервис, а сначала формально закрепить S2 как текущий live-runtime и проверить, что на S1 нет competing unit/process.
- Rollback: вернуть прежний unit-state и любые path/service changes на S2; если трогались timers/crons, откатить их отдельно.
- Post-check: `systemctl status okdesk-pipeline`, `ss -ltn | grep :3200`, pipeline health endpoint, S2 cron calls на `localhost:3200`.

### Model routing normalization
- Что не так: live routing split между `model-strategy.json`, internal `openclaw.json`, `jobs.json` и external `openclaw.json`; snapshot docs устарели по cron и External Boris.
- Source of truth: `docs/ai/SOURCE_OF_TRUTH.md`, `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, live S1 `model-strategy.json`, internal/external `openclaw.json`, `jobs.json`.
- Минимальное исправление: не менять interactive default-chain; отдельно зафиксировать intended cron override в `jobs.json` и intended external chain, затем только при необходимости править один master-слой за раз.
- Rollback: timestamped backup всех четырёх файлов и возврат исходных версий.
- Post-check: `jq` на все model files, сравнение providers/fallbacks, один controlled cron/manual invocation для internal и external.

### Prompt / memory source-of-truth cleanup
- Что не так: `.openclaw/SOUL.md` отсутствует, `RULES.md` живёт только в `workspace/memory`, а snapshot docs описывают другой layout.
- Source of truth: `docs/ai/PROJECT_MEMORY.md`, `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, live S1 `.openclaw/workspace/memory/RULES.md`.
- Минимальное исправление: выбрать один master-path для правил и только потом решать, нужен ли compatibility file/symlink или правка loader-path.
- Rollback: вернуть исходное дерево prompt/memory files из backup.
- Post-check: agent bootstrap, чтение правил, отсутствие двух расходящихся master-файлов.

### Gateway / health-check normalization
- Что не так: live использует `/etc/caddy/Caddyfile`, local `8443` health по `http`, а `sites-enabled` на S1 regular files; часть operational assumptions устарела.
- Source of truth: `docs/ai/OPERATING_CONSENSUS.md`, `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, live `/etc/caddy/Caddyfile`, `/etc/nginx/sites-enabled/*`.
- Минимальное исправление: сначала привести health-check scripts и ops assumptions к реальным path/protocol, не меняя routing logic.
- Rollback: вернуть прежние health scripts/config references.
- Post-check: `http://127.0.0.1:8443/health`, `http://127.0.0.1:3100/health`, `http://127.0.0.1:3102/health`, `https://n8n.brendservice24.ru/bridge-ha/health`.

### Workflow state reconciliation
- Что не так: live `WF11` и `WF8 Watchdog` inactive, хотя snapshot docs говорят обратное.
- Source of truth: `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`, `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, live `n8n.workflow_entity`.
- Минимальное исправление: сначала owner decision по intended state, потом менять только нужные `active` flags, не опираясь на snapshot docs.
- Rollback: restore предыдущих workflow states из DB snapshot/export.
- Post-check: SQL по `workflow_entity`, n8n executions, watchdog/error logs.

### Cron / timer housekeeping
- Что не так: `boris-email-router.timer` и `chief-doctor.timer` выглядят stale, а один cron job в `jobs.json` ещё ни разу не запускался.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, live `crontab -l`, `systemctl list-timers`, S1 `jobs.json`.
- Минимальное исправление: отдельно разобрать intended timers и intended weekly digest state; включать или удалять только после подтверждения, что это не legacy.
- Rollback: restore previous crontab, timer state и `jobs.json`.
- Post-check: `systemctl list-timers`, `jq` state fields в `jobs.json`, отсутствие новых ошибок в cron/service logs.

## 3. Things To Postpone

### Возврат nginx `sites-enabled` к symlink convention
- Что не так: сейчас это regular files, но runtime healthy.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, live `/etc/nginx/sites-enabled/*`.
- Минимальное исправление: если вообще делать, то только как отдельный housekeeping task после сравнения содержимого и с `nginx -t`.
- Rollback: вернуть original files на место.
- Post-check: `nginx -t`, сравнение effective config до/после.

### Публикация Docling на host `:5001`
- Что не так: host-port отсутствует, но интеграция внутри docker-сети рабочая; это не live-failure.
- Source of truth: `docs/ai/OPERATING_CONSENSUS.md`, `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`.
- Минимальное исправление: не делать сейчас; возвращаться только если появится реальная потребность во внешнем host-access.
- Rollback: убрать published port / reverse-proxy mapping.
- Post-check: OCR workflow health и отсутствие regressions в n8n-docling chain.

### Миграция okdesk-pipeline между S2 и S1
- Что не так: есть docs drift, но нет доказательства, что текущий S2 runtime неисправен.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`.
- Минимальное исправление: отложить до отдельного архитектурного решения; не трогать placement только ради соответствия `HANDOFF`.
- Rollback: если когда-то миграция будет начата, rollback = возврат unit/cron/routes на исходный сервер.
- Post-check: pipeline health, Caddy/nginx routes, cron endpoints, `DRY_RUN` behavior.

### Восстановление `.openclaw/SOUL.md` как compatibility file
- Что не так: файл отсутствует, но по аудиту нет доказанного runtime-failure.
- Source of truth: `docs/ai/PROJECT_MEMORY.md`, `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`.
- Минимальное исправление: отложить, пока не будет подтверждено, что какой-то loader реально требует этот path.
- Rollback: удалить compatibility file/symlink.
- Post-check: bootstrap/prompts load без duplicate-source drift.
