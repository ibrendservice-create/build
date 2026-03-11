# CONFIG WRITERS AND ENFORCERS

Read-only audit of server-side writers / enforcers / restorers that can rewrite or restore Boris and related configs/state.

Audit basis:
- repo canon in `docs/ai/*`;
- dated audit docs as of `2026-03-10` and `2026-03-11`;
- live read-only checks on `S1` and `S2` on `2026-03-11`.

Это audit helper, а не новый live master. Его задача: перед любым server-side apply быстро показать:
- где master;
- где derived/runtime;
- кто именно это переписывает;
- по какому trigger;
- почему прямую правку runtime нельзя считать устойчивой.

## Что проверено

- `S1`:
  - root `crontab`;
  - `docker inspect` для internal/external OpenClaw containers;
  - `systemd` units: `infra-monitor.service`, `boris-doctor.service`, `monitor-safe.service`, bridge-related units;
  - live scripts: startup hooks, fixers, watchdogs, sync scripts, doctor/monitor/self-heal scripts.
- `S2`:
  - root `crontab`;
  - `systemd` units: `infra-monitor.service`, `monitor-safe.service`, `n8n-doctor.service`, `okdesk-pipeline.service`;
  - live scripts: `service-guard.py`, `watchdog-meta.sh`, `n8n-doctor`, okdesk sync/export/backfill scripts.
- Repo canon and audit docs:
  - model-routing layering;
  - prompt/memory source of truth;
  - `okdesk-pipeline` placement;
  - cron/timer housekeeping;
  - `bridge-ha`, PG sync, gateway/health assumptions.

## Найденные writers/enforcers

### Active on S1

- Startup writers:
  - internal `startup-cleanup.sh`
  - external `startup-external.sh`
- Periodic config writers:
  - internal `fix-model-strategy.py` at startup
  - external `fix-model-strategy.py` every minute
  - `circuit-breaker-internal.py` every minute
- Prompt/memory writers:
  - `memory-watchdog.py`
  - `promise-watchdog.py`
  - `startup-cleanup.sh` / `startup-external.sh` init for `commitments.json`
- ACL / restore / repair layer:
  - `boris-doctor.service` -> `memory-doctor.py`, `fix-openclaw-acl.sh`, `workspace-validator.py`
  - `infra-monitor.service` -> `monitor.sh` -> `service-guard.py`
  - root cron `watchdog-meta.sh`
- Sync writers:
  - `sync-executors-from-s2.sh`
  - `sync-pg-from-s2.sh`
- Auth-state writer:
  - `refresh-fallback.sh` for Claude Bridge credentials fallback refresh

### Active on S2

- Config baseline / rollback layer:
  - `infra-monitor.service` -> `service-guard.py`
  - root cron `watchdog-meta.sh`
- Workflow/state writer:
  - `n8n-doctor.service` -> state/task/payload/recipe files, conditional recipe apply, payload replay
- Data sync writers:
  - `sync-executor-db.sh`
  - `export-feedback-to-xlsx.py`
  - okdesk cron POSTs to `localhost:3200`

### Potential / conditional, but not confirmed as currently active writer

- `memory-watchdog.py::switch_primary_model()` on `S1` can rewrite internal `openclaw.json`, but current live path keeps model switch disabled.
- `memory-doctor.py repair-sessions-store` can rewrite `sessions.json`, but current `boris-doctor` call-path uses only lock cleanup, permission fix and oversized scan.
- `monitor-safe.service` exists on both servers but is `inactive`; it becomes relevant only if `watchdog-meta.sh` switches monitor into safe mode.

## Matrix

| target file | master | derived/runtime | who rewrites it | trigger | server | risk |
|---|---|---|---|---|---|---|
| internal `.openclaw/openclaw.json` | `model-strategy.json` | live runtime config | `startup-cleanup.sh` -> internal `fix-model-strategy.py`; `circuit-breaker-internal.py`; `workspace-validator.py`; `fix-openclaw-acl.sh` | startup; cron; `boris-doctor` periodic/event | S1 | direct edit is unstable and can be overwritten by startup, cron or doctor repair |
| internal `agents/main/agent/models.json` | `model-strategy.json` provider block | runtime model provider file | internal `fix-model-strategy.py` | startup; manual script run | S1 | direct edit can drift from strategy and be rewritten |
| internal `.openclaw/cron/jobs.json` model fields | `model-strategy.json` (`cron_default_model`, `cron_models`) | `jobs.json.payload.model` | internal `fix-model-strategy.py` | startup post-K; manual fixer run | S1 | runtime model edits can be reset from strategy |
| internal `.openclaw/cron/jobs.json` execution state | OpenClaw scheduler runtime | `lastRunAtMs`, `nextRunAtMs`, status fields | OpenClaw runtime / cron store | job execution | S1 | state edits are ephemeral and not master-backed |
| external `.openclaw/openclaw.json` | external `fix-model-strategy.py` code constants and circuit-breaker state | live runtime config | `startup-external.sh`; external `fix-model-strategy.py`; `infra-monitor/monitor.sh` can re-run fixer | startup; cron `* * * * *`; monitor/self-heal | S1 | runtime file is not master and is actively enforced |
| external `agents/main/agent/models.json` | external `fix-model-strategy.py` | runtime model provider file | external `fix-model-strategy.py` | startup; cron `* * * * *` | S1 | direct edit can be reverted by next enforcer cycle |
| `workspace/memory/RULES.md`, `CLAUDE.md`, `workspace/skills/*/SKILL.md` | live rules SoT = `workspace/memory/RULES.md`; boris-doctor backups become restore source | same live files | `workspace-validator.py` | `boris-doctor` health check every 6h | S1 | validator can auto-restore from backup if file is missing or degraded |
| `workspace/memory/commitments.json` and daily memory files | live file itself | same live files and watchdog state | `startup-cleanup.sh`; `startup-external.sh`; `promise-watchdog.py`; `memory-watchdog.py` | startup; cron | S1 | direct edits can be appended over or normalized by watchdogs |
| session locks, session store, memory ownership/ACL | runtime state only | lock files, `sessions.json`, file ownership, ACLs | `startup-cleanup.sh`; `startup-external.sh`; `monitor-locks.sh`; `memory-doctor.py`; `fix-openclaw-acl.sh` | startup; cron; `boris-doctor` event/periodic | S1 | manual cleanup or permission changes are not stable |
| `model-strategy.json`, internal `fix-model-strategy.py`, tracked config files under monitor | intended live file plus infra-monitor backup/baseline copy | live file plus `/var/lib/apps-data/infra-monitor/{backups,baselines}` | `monitor.sh`; `service-guard.py` | active self-heal loop | S1 | direct edit can be silently baseline-accepted or rolled back |
| `/opt/apps/infra-monitor/monitor.sh` | live file plus `watchdog-meta` backup chain | same file plus safe-mode state and backups | `watchdog-meta.sh` | cron `*/5 * * * *` | S1,S2 | direct edit can be overwritten or rolled back by meta-watchdog |
| Claude Bridge credentials file | Mac push path is intended master; fallback refresh is secondary | runtime credential state | `refresh-fallback.sh` -> `refresh-token.py` | cron `0 */3 * * *`, conditional | S1 | auth runtime state; do not hand-edit |
| `/etc/caddy/Caddyfile`, `okdesk-pipeline.service`, `n8n` compose, monitored unit/code files | intended live file plus `service-guard` baselines | live tracked file plus `/var/lib/apps-data/infra-monitor/baselines/*` | `service-guard.py` | self-heal check/rollback | S2 | direct edit can auto-accept or rollback depending health |
| `/opt/n8n-doctor/state/state.json`, `task-queue.json`, `payloads/*.json`, `recipes/*.json` | live doctor state / queued repair recipe | same files | `n8n-doctor.service`; `apply_pending_recipes()`; `replay_payload()` | continuous loop; manual replay; pending recipe | S2 | direct edit is not durable; pending recipe can mutate external state |
| `OpenClaw_Executor_Scoring_DB.xlsx`, `executors.json`, nginx copy, PG `technicians`, `.xlsx-hash` | Google Drive XLSX | local XLSX, JSON, nginx copy, PG rows, hash file | `sync-executor-db.sh`; `export-feedback-to-xlsx.py`; okdesk PG sync helpers | cron `*/30`; cron `5,35 * * * *` | S2 | local edit is overwritten by next sync/export |
| S1 copies of executors and PG tables | S2 `executors.json` and S2 PG tables | `/var/lib/apps-data/openclaw/data/executors.json`, local PG rows | `sync-executors-from-s2.sh`; `sync-pg-from-s2.sh` | cron | S1 | local direct edit is overwritten by next S2 -> S1 sync |

## Какие файлы нельзя править напрямую

- `S1`:
  - internal/external `openclaw.json`
  - internal/external `models.json`
  - internal `jobs.json`
  - `model-strategy.json`
  - `workspace/memory/RULES.md`
  - `CLAUDE.md`
  - `workspace/memory/commitments.json`
  - `.openclaw` ACL-sensitive runtime paths
- `S1` and `S2`:
  - `infra-monitor/monitor.sh`
  - любой `service-guard` tracked config
- `S2`:
  - `executors.json`, local XLSX copy, PG-derived rows for okdesk sync contour
  - `n8n-doctor` state, recipes and payload files
- Auth runtime state:
  - Claude Bridge credential runtime file

## Что надо сначала синхронизировать перед любым apply

- Internal model routing:
  - `model-strategy.json`
  - internal `fix-model-strategy.py`
  - startup path
  - post-check of `openclaw.json`, `jobs.json`, `models.json`
  - `infra-monitor` backup/baseline layer
- External model routing:
  - external `fix-model-strategy.py`
  - `startup-external.sh`
  - minutely cron enforcer
  - post-check of external `openclaw.json` and `models.json`
- Prompt / memory:
  - live `workspace/memory/RULES.md`
  - boris-doctor backups for `RULES.md`, `CLAUDE.md`, skill files
- Monitored configs:
  - live target file
  - `service-guard` baseline on the same server
  - for `monitor.sh` also `watchdog-meta` backup chain
- S2 -> S1 sync contours:
  - first S2 master (`XLSX`, PG, `executors.json`)
  - only then S1 derived copies

## Вердикт

- `WARN`
- Main risk is not a single broken writer, but dense layered rewrite/restore behavior.
- Before any server-side apply first determine:
  - master
  - derived/runtime
  - writers/enforcers
  - their triggers
- Do not patch runtime/derived in isolation if an active startup/cron/doctor/monitor/sync layer will overwrite it.
- If config lives through layered sync, change the master layer.
- If runtime apply is truly required, first do one of:
  - update master
  - update writer layer
  - disable enforcer explicitly by approved plan
