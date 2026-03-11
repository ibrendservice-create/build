# DOCTOR AGENT DECISION

Дата: 2026-03-11
Статус: accepted docs-only decision

Основание:
- `docs/ai/DOCTOR_AND_SELFHEAL_AUDIT_2026-03-11.md`
- `docs/ai/DOCTOR_OWNER_DECISIONS_REQUIRED.md`
- `docs/ai/BORIS_DETAIL_SCHEMA_CHECKLIST_v2.md`
- `/Users/timuraripov/Desktop/BS24-MASTER-PLAN-v2.0.md`

## Chosen architecture

- Chosen architecture = `skill + script`.
- `skill` = orchestration / analyst entrypoint inside Boris.
- `script` = strict read-only collector with allowlist probes and structured report output.
- MVP is:
  - `manual only`
  - `read-only`
  - `report only`
  - `no auto-repair`
- For MVP do not use:
  - `cron`
  - `heartbeat`
  - `workflow`

## Why not cron / heartbeat / workflow for MVP

- `cron` would immediately create a new background monitoring contour.
- `heartbeat` in official OpenClaw is an agent check-in primitive, not the right shape for host/business observer analysis.
- `workflow` would place MVP inside the live BS24 automation plane on `S2`, increasing blast radius.
- `skill + script` keeps the contour local, explicit, and manually invoked.

## What it observes

### Infrastructure

- audited core services on `S1` and `S2`:
  - `boris-doctor`
  - `infra-monitor`
  - `claude-bridge`
  - `nginx`
  - `caddy`
  - `n8n-doctor`
  - `okdesk-pipeline`
- critical containers and their health-level state
- freshness of already existing heartbeat/state signals:
  - `infra-monitor`
  - `boris-doctor`
  - business `.hb` files
- canonical public `bridge-ha` probe with JSON/body validation, not only `HTTP 200`
- `S2` pipeline liveness as:
  - `okdesk-pipeline.service`
  - listener `:3200`

### BS24 business-liveness

- expected workflow state by exact IDs:
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
- dispatch contour only in liveness terms:
  - pipeline up
  - n8n up
  - workflow state matches canon
  - heartbeats fresh
- partial steps `6-10` only as liveness/support signal, not as semantic product correctness

### Explicitly not covered

- classification quality
- matching quality
- QC quality
- rating / XP correctness
- promise correctness
- semantic business truth

## What it does not touch

- no restart
- no rollback
- no re-register
- no payload replay
- no activate/deactivate workflow
- no writes to:
  - `openclaw.json`
  - `jobs.json`
  - `RULES.md`
  - `CLAUDE.md`
  - `SKILL.md`
  - `commitments.json`
- no mutations of:
  - `watchdog-meta`
  - `service-guard`
  - `workspace-validator`
  - `promise-watchdog`
  - `n8n-watchdog`
  - `n8n-doctor`
- no changes to:
  - model routing
  - bridge
  - auth
  - gateway
  - prompt/memory layout
- no writes to existing heartbeat/state files
- never acts as writer / enforcer / restorer

## Why this is safe

- This is a single observer, not another self-heal controller.
- It remains outside dangerous auto-repair rights already identified in the `2026-03-11` audit.
- It separates:
  - infrastructure liveness
  - BS24 business-liveness
  - semantic business correctness
- `skill + script` keeps the MVP narrow:
  - manual invocation
  - fixed allowlist probes
  - report-only output
  - no background loop

## MVP scope

- one skill: `observer-doctor`
- one script: read-only collector with modes:
  - `infra`
  - `business`
  - `full`
- output only report entries:
  - `OK`
  - `WARN`
  - `FAIL`
  - `UNKNOWN`
- each report row must include:
  - observed fact
  - evidence/source
  - suggested human follow-up

## MVP boundaries

- Do not turn MVP into auto-repair.
- Do not add `cron` or `heartbeat` scheduling for MVP.
- Do not place MVP inside `n8n` workflow execution.
- Do not widen scope from liveness to semantic business correctness.
- Any future periodic mode or server-side implementation remains:
  - owner decision first
  - explicit approve second
