# DOCTOR AND SELFHEAL AUDIT 2026-03-11

Read-only аудит контуров `doctor / monitor / watchdog / self-healing` на `S1` и `S2`.
Live изменения не выполнялись.

## Слой

- monitoring / self-healing / doctor contours
- host cron + systemd + service scripts + related writer/enforcer layers

## Source of truth

- Repo canon:
  - `AGENTS.md`
  - `docs/ai/OPERATING_CONSENSUS.md`
  - `docs/ai/PROJECT_MEMORY.md`
  - `docs/ai/SOURCE_OF_TRUTH.md`
  - `docs/ai/CHANGE_POLICY.md`
  - `docs/ai/VERIFICATION_MATRIX.md`
  - `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`
  - `docs/ai/BASELINE_2026-03-10.md`
  - `docs/ai/BORIS_DETAIL_SCHEMA_CHECKLIST_v2.md`
  - `docs/ai/CHANGE_RUNBOOK.md`
  - `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`
  - `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`
  - `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`
  - `docs/ai/HANDOFF_2026-03-10.md`
- User-requested context:
  - `docs/ai/CODEX_PLAYBOOK.md`
  - `docs/ai/BASELINE_2026-03-10.md`
  - `docs/ai/BORIS_DETAIL_SCHEMA_CHECKLIST_v2.md`
  - `docs/ai/CHANGE_RUNBOOK.md`
  - `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`
  - `/Users/timuraripov/Desktop/BS24-MASTER-PLAN-v2.0.md`
- Live read-only checks:
  - `systemctl list-units/list-unit-files/show/cat`
  - `crontab -l`
  - `ps -ef`
  - targeted `sed/grep/find` for doctor/monitor/watchdog scripts and state dirs
  - `python3 /opt/apps/infra-monitor/service-guard.py status`
- Official OpenClaw docs for comparison:
  - `https://docs.openclaw.ai/gateway/doctor`
  - `https://docs.openclaw.ai/automation/cron-jobs`
  - `https://docs.openclaw.ai/gateway/heartbeat`
  - `https://docs.openclaw.ai/automation/troubleshooting`

## Риск

- `HIGH`
- На обоих серверах есть не один, а несколько пересекающихся auto-repair контуров.
- На `S1` один и тот же runtime могут трогать минимум:
  - `boris-doctor`
  - `monitor-locks.sh`
  - `infra-monitor`
  - `monitor-safe`
  - `service-guard`
- На `S2` n8n/runtime могут трогать минимум:
  - `n8n-doctor`
  - `infra-monitor`
  - `service-guard`
  - `watchdog-meta`
- Самые опасные зоны:
  - auto-restart core services/containers;
  - auto-rollback config files;
  - auto-patch `monitor.sh`;
  - workflow mutate/replay on production n8n;
  - product-state writes в `memory`, `commitments.json`, `openclaw.json`, `SKILL.md`, `RULES.md`.

## План

- Прочитать canon и snapshot docs в заданном порядке.
- Собрать live inventory `unit/service/timer/cron/script` на `S1` и `S2`.
- Выделить реальные active contours vs disabled/legacy noise.
- Для каждого active contour определить:
  - trigger;
  - monitored state/files;
  - repair actions;
  - writer/enforcer/restorer side effects.
- Сравнить live с repo canon и official OpenClaw docs.
- Зафиксировать результат docs-only.

## Rollback

- Не нужен для live: аудит был read-only.
- Для repo rollback = удалить этот файл, если вывод окажется неточным после следующего live audit.

## Post-check

- Подтверждены live active units/processes на `S1` и `S2`.
- Подтверждены relevant crontab entries на `S1` и `S2`.
- Подтверждены state/baseline/registry files для `infra-monitor/service-guard`.
- Подтверждено:
  - `openclaw` CLI на `S1` host отсутствует (`openclaw command not found`);
  - repo canon не описывает live self-heal как single official OpenClaw contour;
  - live system опирается на custom host-side doctors/watchdogs больше, чем на builtin Gateway doctor/heartbeat path.

## Какие doctor/monitor контуры есть

### S1 — active Boris-side contours

| Контур | Trigger / runtime | Что отслеживает | Что умеет чинить | Класс |
| --- | --- | --- | --- | --- |
| `boris-doctor.service` -> `/opt/apps/boris-doctor/doctor-runtime.py` | systemd service, active | `openclaw` container, sessions locks, memory ownership, oversized sessions, bridge semantic state, gateway state, cron doctor output, doctor heartbeat, restart history, workspace validator output | stale lock cleanup, memory ownership fix, bridge remediation, container restart with lock/cooldown, ACL repair, Opus escalation | `active self-heal` |
| `monitor-locks.sh` | host cron `*/2 * * * *` | container running, `boris-doctor` heartbeat, `claude-bridge/file-extractor/nginx`, bridge health endpoint, container silence, garbage session files | `docker compose up -d`, `systemctl restart`, delete stale `*.bak/*.deleted/*.reset` in sessions | `dangerous auto-repair` |
| `memory-watchdog.py` | host cron `*/30 7-19 * * *` | session transcripts of the day, presence of model memory writes, memory file freshness, container health, bridge health | writes summary to memory when model skipped it; restarts `claude-bridge` if repeated failures + bridge down | `conditional repair` |
| `promise-watchdog.py` | host cron `15,45 4-19 * * *` | session promises, `commitments.json`, overdue commitments, watchdog state | auto-inserts missing commitments into `commitments.json`, sends overdue alerts | `dangerous auto-repair` |
| `infra-monitor.service` -> `/opt/apps/infra-monitor/monitor.sh` | systemd service, active | core services, containers, bridge, disk/RAM, remote monitor heartbeat, config drift, service-guard output, discovery lists, some S2-facing liveness signals | simple restart, KB fix, Opus-generated fix, chmod/chown/symlink repair, service/container restart | `dangerous auto-repair` |
| `watchdog-meta.sh` | host cron `*/5 * * * *` | `infra-monitor` heartbeat freshness, crash-loop state, recent journal errors | starts `monitor-safe`, asks Bridge for patch to `monitor.sh`, applies patch with backup/test/rollback, restarts `infra-monitor` | `dangerous auto-repair` |
| `monitor-safe.service` -> `monitor-safe.sh` | disabled fallback, started by meta-watchdog | minimal service states, Docker health, safe-mode heartbeat | restarts listed services and unhealthy containers | `active self-heal` |
| `guard-webhook.service` + `service-guard.py` | systemd webhook + monitor invocation | baselines, config hashes, tracked service/container health, pending discoveries | auto-accept config changes if healthy, rollback tracked files if unhealthy, restart units/containers | `dangerous auto-repair` |
| `n8n-watchdog.service` -> `/opt/apps/n8n-watchdog/watchdog.py` | systemd service, active | remote n8n workflows, webhook registration, error executions, chain health, chain replay, payload capture, system health | workflow repair tasks via Bridge, auto full webhook re-register, replay live payloads, workflow activate/deactivate flows | `dangerous auto-repair` |
| `ssh-watchdog.sh` | host cron `*/5 * * * *` | SSH port `58536` listening state | writes socket override and restarts `ssh.socket` | `conditional repair` |

### S1 — installed but not active / legacy / platform noise

| Контур | State | Комментарий |
| --- | --- | --- |
| `chief-doctor.service` | inactive | Read-only diagnostic orchestrator, explicitly states it does not repair. |
| `chief-doctor.timer` | disabled / inactive | Legacy timer contour; not active after 2026-03-10 housekeeping decision. |
| `watchdogd` | active kernel/userland watchdog | OS-level, not Boris business logic. |
| `lvm2-monitor.service`, `mdmonitor-oneshot.timer`, `snapd.snap-repair.timer` | platform units | Generic Linux repair/monitoring, not Boris-specific. |

### S2 — active BS24-side contours

| Контур | Trigger / runtime | Что отслеживает | Что умеет чинить | Класс |
| --- | --- | --- | --- | --- |
| `n8n-doctor.service` -> `/opt/apps/n8n-doctor/doctor.py` | systemd service, active | n8n error executions, configured chain workflows, webhook registration, payload capture, system health (`bridge1`, `bridge2`, `openclaw_s1`, n8n container) | creates Opus repair tasks, applies pending recipes, updates workflows via API/tooling, replays payload after repair | `dangerous auto-repair` |
| `infra-monitor.service` -> `/opt/apps/infra-monitor/monitor.sh` | systemd service, active | `claude-bridge/caddy/n8n-doctor`, `n8n/db/cache/docling` containers, `okdesk-pipeline`, OpenClaw gateway on S1, sessions store, OAuth, cron heartbeats, email freshness, `mem_events`, Supabase sync, Okdesk API, TG bot access, remote S1 heartbeat | restarts services/containers, sessions-store repair, KB/Opus fixes, alerting, config/service-guard orchestration | `dangerous auto-repair` |
| `watchdog-meta.sh` | host cron `*/5 * * * *` | same as S1 but for S2 `infra-monitor` | same patch/rollback safe-mode logic as on S1 | `dangerous auto-repair` |
| `monitor-safe.service` -> `monitor-safe.sh` | disabled fallback, started by meta-watchdog | minimal service states, Docker health, safe-mode heartbeat | restarts listed services/containers | `active self-heal` |
| `guard-webhook.service` + `service-guard.py` | systemd webhook + monitor invocation | baselines, config hashes, tracked service/container health on S2 | auto-accept config changes if healthy, rollback tracked files if unhealthy, restart units/containers | `dangerous auto-repair` |
| `check-cron-health.sh` | host cron `*/15 * * * *` | heartbeat freshness for `sla-check`, `nudge-send`, `followup-scan`, `followup-send`, `dispatch-reminders` | alerts only, no repair | `safe observer` |

### S2 — platform noise

| Контур | State | Комментарий |
| --- | --- | --- |
| `watchdogd` | active | OS-level only. |
| `lvm2-monitor.service`, `mdmonitor-oneshot.timer` | active/enabled platform units | Not Boris/BS24 logic. |

## Что каждый из них отслеживает

### Core files, state and health objects observed on S1

- `boris-doctor`:
  - `/var/lib/apps-data/boris-doctor/heartbeat`
  - `/var/lib/apps-data/boris-doctor/last-health-check.ts`
  - `/var/lib/apps-data/boris-doctor/restart-history`
  - `/var/lib/apps-data/boris-doctor/actions.jsonl`
  - `/var/lib/apps-data/openclaw/data/.openclaw/agents/main/sessions/*`
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/memory/*`
  - bridge/gateway/cron specialist probe output
- `workspace-validator` inside `boris-doctor`:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
  - `/var/lib/apps-data/openclaw/data/model-strategy.json`
  - `/var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json`
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/memory/RULES.md`
  - `/var/lib/apps-data/openclaw/data/CLAUDE.md`
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/skills/*/SKILL.md`
  - `/var/lib/apps-data/openclaw/data/.openclaw/watchdog/startup-cleanup.log`
- `monitor-locks.sh`:
  - `openclaw-kbxr-openclaw-1`
  - `/var/lib/apps-data/boris-doctor/heartbeat`
  - `claude-bridge`, `file-extractor`, `nginx`
  - `http://187.77.74.126:8443/health`
  - session garbage files
- `memory-watchdog.py`:
  - session transcripts for today
  - marker that model used `write` into `memory/`
  - today's memory file
  - container health + bridge health
- `promise-watchdog.py`:
  - session assistant messages with promise patterns
  - `/docker/openclaw-kbxr/data/.openclaw/workspace/memory/commitments.json`
  - `/docker/openclaw-kbxr/data/.openclaw/watchdog/promise-watchdog-state.json`
- `infra-monitor` / `service-guard` on S1:
  - services: `nginx`, `claude-bridge`, `boris-doctor`, `file-extractor`, `n8n-watchdog`, `openclaw-agent-bridge`, `claude-mcp-http`, `openai-bridge`
  - containers: `openclaw-kbxr-openclaw-1`, `openclaw-ext-openclaw-1`
  - config registry hashes in `/opt/apps/infra-monitor/config-registry.json`
  - baselines under `/var/lib/apps-data/infra-monitor/baselines/*`
  - pending auto-discovery under `/var/lib/apps-data/infra-monitor/state/pending/*`
  - remote S2 heartbeat / bridge availability
- `n8n-watchdog`:
  - active workflow IDs
  - critical webhook paths
  - recent error executions
  - saved webhook payloads
  - chain replay result

### Core files, state and health objects observed on S2

- `n8n-doctor`:
  - n8n execution API
  - configured chain workflow IDs from env
  - configured webhook paths from env
  - payload archive under `/opt/n8n-doctor/payloads`
  - task queue / state under `/opt/n8n-doctor/state`
  - system health probes: bridge #2 local, bridge #1, `openclaw_s1`, n8n container
- `infra-monitor` on S2:
  - services: `claude-bridge`, `caddy`, `n8n-doctor`
  - containers: `app-n8n-1`, `app-n8n-worker-1`, `app-db-1`, `app-cache-1`, `app-docling-1`, `pdf2img`, `office2pdf`, `img2pdf`
  - `okdesk-pipeline.service` + `http://localhost:3200`
  - OpenClaw gateway/public health on S1
  - sessions store integrity via `memory-doctor`
  - OAuth token expiry and API validity
  - cron/business heartbeat files
  - mail freshness, `mem_events`, Supabase sync summary, Okdesk API, TG bot access
  - remote S1 monitor heartbeat
- `check-cron-health.sh`:
  - `/var/lib/apps-data/infra-monitor/heartbeats/sla-check.hb`
  - `/var/lib/apps-data/infra-monitor/heartbeats/nudge-send.hb`
  - `/var/lib/apps-data/infra-monitor/heartbeats/followup-scan.hb`
  - `/var/lib/apps-data/infra-monitor/heartbeats/followup-send.hb`
  - `/var/lib/apps-data/infra-monitor/heartbeats/dispatch-reminders.hb`
- `service-guard` on S2:
  - baselines for `n8n`, `n8n-db`, `caddy`, `claude-bridge`, `n8n-doctor`, `okdesk-pipeline`, `infra-monitor`
  - config files in registry and baseline dirs
  - `infra-monitor` heartbeat freshness

## Что каждый из них умеет чинить

### S1

- `boris-doctor`:
  - удаляет stale session locks;
  - чинит ownership memory files;
  - по specialist doctor перезапускает bridge/container;
  - по `workspace-validator` может:
    - auto-restore `RULES.md` from backup;
    - auto-restore `CLAUDE.md`;
    - auto-restore `channels.telegram` in `openclaw.json`;
    - auto-restore `messages.groupChat.mentionPatterns`;
    - auto-restore missing/small `SKILL.md`;
    - auto-remove tiny `IDENTITY.md`;
- `monitor-locks.sh`:
  - поднимает `openclaw` контейнер;
  - рестартует `boris-doctor`, `claude-bridge`, `file-extractor`, `nginx`;
  - удаляет garbage session artefacts;
- `memory-watchdog.py`:
  - сам пишет memory summary вместо модели;
  - рестартует `claude-bridge` при повторяющейся деградации и down bridge;
- `promise-watchdog.py`:
  - сам добавляет новые commitments в `commitments.json`;
- `infra-monitor`:
  - `simple_fix`;
  - `KB_FIX`;
  - `Opus`-suggested high-confidence bash fix;
  - restart systemd services / docker containers;
  - chmod/chown for drift;
  - compatibility symlink repair;
  - может трогать S1/S2 liveness-related paths через self-heal logic;
- `watchdog-meta.sh`:
  - активирует safe-mode;
  - патчит `monitor.sh`;
  - делает syntax test и rollback backup;
- `service-guard.py`:
  - делает baseline accept;
  - rollback tracked configs to previous snapshot;
  - restart service/container after rollback;
- `n8n-watchdog`:
  - создаёт auto-repair tasks;
  - full deactivate/activate all active workflows after repeated webhook failures;
  - воспроизводит реальные payloads через production webhook;
- `ssh-watchdog.sh`:
  - восстанавливает SSH socket config и рестартует `ssh.socket`.

### S2

- `n8n-doctor`:
  - создаёт repair tasks with workflow update instructions;
  - может apply pending local recipes;
  - после successful fix делает payload replay в production webhook;
  - reactivates configured chain workflows if workflow-health path enabled in env and missing;
- `infra-monitor`:
  - restart services/containers;
  - okdesk-pipeline restart;
  - sessions store repair via `memory-doctor repair-sessions-store`;
  - OAuth-related simple/KB/Opus fixes;
  - alerts and local corrective actions on infra/business-liveness failures;
- `watchdog-meta.sh`:
  - same self-patching/rollback logic as S1;
- `service-guard.py`:
  - baseline accept;
  - rollback configs to previous snapshot;
  - restart service/container after rollback;
- `check-cron-health.sh`:
  - ничего не чинит, только алертит.

## Writer / enforcer / restorer контуры

### Restorer / rollback contours

- `workspace-validator.py`:
  - restores `RULES.md`, `CLAUDE.md`, Telegram config, mention patterns, `SKILL.md`;
- `memory-doctor.py repair-sessions-store`:
  - backs up corrupted sessions store and writes a fresh `{}`;
- `service-guard.py`:
  - keeps `current` and `previous` baselines;
  - restores tracked config files;
  - restarts owning unit/container after rollback;
- `watchdog-meta.sh`:
  - keeps `monitor.sh.bak.meta-fix-*`;
  - syntax-tests temp copy;
  - rolls back if new patch breaks heartbeat or service state.

### Writer / enforcer contours adjacent to doctor/monitor

- `S1` crontab `docker exec openclaw-ext-openclaw-1 python3 /data/fix-model-strategy.py` every minute:
  - explicit model-routing enforcer for external Boris.
- `S1` crontab `docker exec openclaw-kbxr-openclaw-1 python3 /data/circuit-breaker-internal.py` every minute:
  - internal runtime mutator, not confirmed as `jobs.json` source of truth but still a runtime writer.
- `config-registry.json` on `S1` already marks `model-strategy.json` guardian as `fix-model-strategy.py`.
- `infra-monitor` auto-discovery writes:
  - `auto-services.txt`
  - `auto-containers.txt`
  - `excluded-*.txt`
  - pending discovery json under `state/pending/*`.
- `n8n-doctor` and `n8n-watchdog` both maintain:
  - task queues;
  - payload archives;
  - state files;
  - repair logs / knowledge files.

### Important implication

- Live truth around `doctor/self-heal` is not only observer logic.
- These contours actively write:
  - runtime config;
  - monitoring baselines;
  - workflow state;
  - memory/commitments state;
  - service/container state.

## Что они не покрывают

- Не покрывают semantic correctness AI output:
  - classification quality;
  - object matching quality;
  - contract/legal accuracy;
  - budget estimate correctness;
  - dispatch ranking correctness;
  - reply quality to clients/technicians.
- Не покрывают business KPI truth:
  - revenue/margin;
  - XP/reputation fairness;
  - marketplace economics;
  - technician motivation loop from master plan.
- Не покрывают owner intent:
  - should a workflow exist at all;
  - should a prompt/rule be restored from backup;
  - should an auto-repair still be considered safe.
- Не покрывают docs drift by themselves:
  - several contours still act on runtime assumptions even when canon moved on.
- Не покрывают single-control ownership:
  - same asset is often controlled by multiple actors at once.

## Инфраструктурное покрытие

- `Strong / overlapping`
- Covered well:
  - systemd service liveness;
  - docker container liveness/health;
  - bridge health;
  - cross-server heartbeat;
  - config drift / baseline rollback;
  - SSH port liveness;
  - Caddy/nginx/okdesk-pipeline/n8n/db/docling container health;
  - cron heartbeat freshness on S2;
  - OAuth/token expiry signals.
- Weak spots even at infra layer:
  - too many overlapping restart authorities;
  - monitor self-modification via AI patching;
  - `chief-doctor` exists but is no longer the active orchestration plane;
  - official `openclaw doctor` is not the live primary control loop.

## Покрытие бизнес-логики BS24

- `Partial / liveness-first, not semantics-first`
- What is actually covered:
  - n8n chain execution failures;
  - webhook registration health;
  - chain replay on real payloads;
  - `okdesk-pipeline` endpoint liveness;
  - S2 cron business heartbeat files:
    - SLA monitor
    - nudge engine
    - follow-up scan
    - follow-up send
    - dispatch reminders
  - email freshness;
  - `mem_events` freshness;
  - Supabase sync freshness and doc count drift;
  - Okdesk API reachability;
  - TG bot access to business chats;
  - commitments tracking via `promise-watchdog`;
  - memory write discipline via `memory-watchdog`.
- What is not covered:
  - whether nudge content is correct;
  - whether follow-up logic is business-correct;
  - whether WF outputs are good, only that they run;
  - whether BS24 target architecture from master plan is being fulfilled.

## Safe observer / conditional repair / active self-heal / dangerous auto-repair

### Safe observer

- `S1 chief-doctor.service` / `chief-doctor.timer`:
  - read-only by design, currently inactive.
- `S2 check-cron-health.sh`:
  - heartbeat freshness + alert only.

### Conditional repair

- `S1 memory-watchdog.py`:
  - repair only after repeated failures and only if bridge is down.
- `S1 ssh-watchdog.sh`:
  - acts only when SSH port disappears.

### Active self-heal

- `S1 boris-doctor.service`
- `S1 monitor-safe.service`
- `S2 monitor-safe.service`

### Dangerous auto-repair

- `S1 monitor-locks.sh`
- `S1 promise-watchdog.py`
- `S1 infra-monitor.service`
- `S1 watchdog-meta.sh`
- `S1 guard-webhook + service-guard.py`
- `S1 n8n-watchdog.service`
- `S2 n8n-doctor.service`
- `S2 infra-monitor.service`
- `S2 watchdog-meta.sh`
- `S2 guard-webhook + service-guard.py`
- `workspace-validator.py` sublayer inside `boris-doctor`

## Риски auto-repair

### 1. Multi-controller risk

- `openclaw` container / bridge on `S1` can be restarted by multiple contours.
- Same `n8n`/workflow surface can be mutated by:
  - `S1 n8n-watchdog`
  - `S2 n8n-doctor`
  - `S2 infra-monitor`

### 2. Runtime-over-master risk

- `workspace-validator` restores runtime files directly:
  - `openclaw.json`
  - `RULES.md`
  - `SKILL.md`
- `service-guard` rollbacks configs by baseline, not by repo master.
- This is operationally useful, but conflicts with strict `master -> runtime` discipline if owner intent changed elsewhere.

### 3. AI-patch risk

- `watchdog-meta.sh` can self-patch `monitor.sh` using Bridge-generated command.
- Even with blocklist/syntax/rollback, this is still production self-modifying monitoring code.

### 4. Workflow mutation risk

- `n8n-watchdog` can full deactivate/activate all active workflows.
- `n8n-doctor` can update workflows and replay saved payloads after repair.
- This is beyond infra repair; it changes business automation state.

### 5. Product-state mutation risk

- `memory-watchdog` writes memory entries.
- `promise-watchdog` writes `commitments.json`.
- `workspace-validator` can restore prompt/rules/skills files from backups.
- These repairs affect business/internal state, not only infrastructure.

## Как это соотносится с официальной документацией OpenClaw doctor / cron / heartbeat

### What official docs say

- Official `doctor`:
  - `openclaw doctor` is the repair + migration tool for OpenClaw;
  - `openclaw doctor --deep` scans extra gateway installs and service wrappers;
  - docs describe an on-demand CLI repair/migration flow, not a resident server watchdog.
- Official `cron`:
  - cron is the Gateway built-in scheduler;
  - jobs persist under `~/.openclaw/cron/jobs.json`;
  - cron runs inside the Gateway, not inside the model;
  - troubleshooting expects `openclaw cron status`, `openclaw cron list`, `openclaw cron runs`.
- Official `heartbeat`:
  - heartbeat is a periodic main-session agent turn;
  - it is about agent check-ins and `HEARTBEAT.md`, not host liveness files;
  - troubleshooting expects `openclaw system heartbeat last`.

### What live Boris actually does

- Host-side primary control plane is custom:
  - `boris-doctor`
  - `infra-monitor`
  - `watchdog-meta`
  - `service-guard`
  - `monitor-locks`
  - `n8n-watchdog`
  - `n8n-doctor`
- Live cron is split across:
  - host `crontab`;
  - OpenClaw `jobs.json`;
  - disabled/legacy timers;
  - S2 business cron endpoints + `.hb` files.
- Live “heartbeat” usually means monitor liveness/state files:
  - `/var/lib/apps-data/infra-monitor/state/heartbeat.json`
  - `heartbeat-safe.json`
  - cron `.hb` files
  - `boris-doctor/heartbeat`
  - not only Gateway heartbeat turns.

### Alignment vs mismatch

- `Aligned`:
  - Canon repo already says host `crontab`, `jobs.json`, and systemd timers must be treated separately.
  - Canon repo already says heartbeat/state belongs to monitoring contour, not product truth.
  - Live S2 pipeline heartbeat files fit this canon.
- `Mismatch`:
  - Official OpenClaw docs do not describe the real Boris production self-heal stack.
  - Official `doctor` is CLI-centered; live Boris relies on always-on custom daemons and cron scripts.
  - Official `heartbeat` docs describe main-session agent turns, while live Boris heavily uses filesystem heartbeats for infra liveness.
  - Official cron troubleshooting path is not the main live operator path here.

### Practical conclusion

- Boris production monitoring is not “OpenClaw doctor plus a few helpers”.
- It is a custom multi-layer self-heal system wrapped around OpenClaw, n8n and BS24 integrations.
- Therefore:
  - official OpenClaw docs explain the Gateway primitives;
  - they do not explain the current Boris operational control plane end-to-end.

## Что можно улучшить только в docs

- Явно отделить:
  - official OpenClaw `doctor/cron/heartbeat`;
  - Boris custom host-side self-heal.
- Зафиксировать, что `openclaw doctor` не является active resident control loop в проде Бориса.
- Описать dual-control risk:
  - `S1 n8n-watchdog`
  - `S2 n8n-doctor`
  - `S2 infra-monitor`
- Описать sublayers inside `boris-doctor`:
  - `workspace-validator`
  - `memory-doctor`
  - `bridge-doctor`
  - `gateway-doctor`
  - `cron-doctor`
- Явно пометить dangerous contours:
  - `watchdog-meta`
  - `service-guard`
  - `n8n-watchdog`
  - `n8n-doctor`
  - `promise-watchdog`
  - `monitor-locks.sh`
- Отдельно описать:
  - какие heartbeats = infra-only;
  - какие heartbeats = business cron liveness;
  - что heartbeat stale не равен product failure.

## Что требует owner decision

- Нужен ли дальше `S1 n8n-watchdog`, если на `S2` уже есть `n8n-doctor`.
- Нужен ли дальше auto full webhook re-register on S1.
- Допустимо ли, чтобы `workspace-validator` продолжал auto-restore:
  - `RULES.md`
  - `openclaw.json` fragments
  - `SKILL.md`
- Допустимо ли, чтобы `promise-watchdog` автоматически писал в `commitments.json`.
- Должен ли `watchdog-meta` и дальше иметь право AI-патчить `monitor.sh`.
- Какие contours считать canonical:
  - official OpenClaw doctor path;
  - Boris custom doctor path;
  - hybrid.

## Что требует approve

- Любое live изменение в:
  - `boris-doctor`
  - `infra-monitor`
  - `watchdog-meta`
  - `monitor-safe`
  - `service-guard`
  - `guard-webhook`
  - `n8n-watchdog`
  - `n8n-doctor`
  - `monitor-locks.sh`
  - `memory-watchdog.py`
  - `promise-watchdog.py`
  - `ssh-watchdog.sh`
- Любые changes в:
  - `systemd` units/timers;
  - `crontab`;
  - monitored config files;
  - workflow active state / webhook lifecycle;
  - routing writers like `fix-model-strategy.py` / `circuit-breaker-internal.py`;
  - auto-repair rights over `openclaw.json`, `RULES.md`, `SKILL.md`, `commitments.json`.

## Verdict

- `WARN / HIGH OPERATIONAL COMPLEXITY`
- Реальные doctor/monitor/self-heal контуры на `S1` и `S2` существуют в большом количестве и в значительной части активны.
- Это не “safe observer only” стек.
- Current live reality:
  - very strong infrastructure coverage;
  - partial business-process liveness coverage;
  - weak semantic business correctness coverage;
  - high overlap and high blast radius of auto-repair.
- Самые важные выводы:
  - Boris monitoring/self-healing mostly covers infrastructure and process liveness, not BS24 semantic business logic.
  - There is meaningful business-loop liveness coverage on S2, but not business decision correctness.
  - Several contours are already in `dangerous auto-repair` territory.
  - Official OpenClaw doctor/cron/heartbeat docs explain the underlying Gateway primitives, but they do not describe the actual Boris production control plane.
- Next safe step:
  - docs-only normalization of contour ownership and danger classes;
  - no live apply without explicit owner decision and approve.
