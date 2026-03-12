# SERVER CHANGELOG 2026-03-12: MAIN PER-AGENT HARDENING WAVE

## Layer
- `S1` internal OpenClaw per-agent tool policy for `agents.list[id=main]`

## Scope
- Live apply on `S1`
- Only:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
- Exact changed path:
  - `agents.list[id=main].tools.deny`
- Exact value:
  - `["group:automation","group:nodes","sessions_spawn","sessions_send"]`
- Out of scope:
  - `group:runtime`
  - `group:fs`
  - global `tools.*`
  - Telegram group overlays
  - `model-strategy.json`
  - `jobs.json`
  - `models.json`
  - plugins
  - hooks
  - `callback-forward`
  - owner policy
  - memory layout
  - business workspace
  - model picker
  - monitoring
  - stale cleanup contours

## Source of truth
- `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`

## What was wrong
- After successful `/route` closure, group-scoped self-mod deny and cron split off `main`, shared `main` still had no per-agent deny layer for control-plane and session-orchestration surfaces.
- This left `main` broader than needed even though:
  - enabled jobs on `main` were already `0`
  - enabled implicit jobs were already `0`
- A broader deny was still unsafe because Boris must remain a full employee agent and employee capabilities had to be preserved.

## What changed
- Added only `agents.list[id=main].tools.deny` in `openclaw.json`.
- Exact value now:
  - `group:automation`
  - `group:nodes`
  - `sessions_spawn`
  - `sessions_send`
- Nothing else was changed.

## Backup
- Backup dir:
  - `/root/main-per-agent-hardening-20260312T115001Z`
- Backup files:
  - `/root/main-per-agent-hardening-20260312T115001Z/openclaw.json.bak`
  - `/root/main-per-agent-hardening-20260312T115001Z/pre-main-agent.json`
  - `/root/main-per-agent-hardening-20260312T115001Z/pre-groups.json`
  - `/root/main-per-agent-hardening-20260312T115001Z/pre-jobs-summary.json`
  - `/root/main-per-agent-hardening-20260312T115001Z/ROLLBACK.txt`

## Pre-check
- `enabled_on_main=0`
- `enabled_implicit=0`
- `route-command.enabled=false`
- `callback-forward.enabled=true`
- all 6 Telegram group overlays unchanged
- `main.tools before apply = null`
- global `tools.profile/allow/deny = null/null/null`
- `fix-model-strategy.py` still preserves existing `main` entry
- `workspace-validator.py` does not own `main.tools`
- no known live business flow dependency found on:
  - `nodes`
  - `sessions_spawn`
  - `sessions_send`

## Post-check
- semantic diff limited to:
  - `agents.list[id=main].tools.deny`
- `main` identity unchanged
- `jobs.json` unchanged:
  - `enabled_total=13`
  - `enabled_on_main=0`
  - `enabled_implicit=0`
- `route-command.enabled=false` unchanged
- `callback-forward.enabled=true` unchanged
- all 6 Telegram group overlays unchanged
- new `main.tools.deny` exact value confirmed
- structural compare against backup matched outside `main.tools`
- exact gateway-side runtime resolver proof was not re-run in the current safe operator context

## Rollback required or not
- Rollback was not required.

## Employee capabilities preserved
- Preserved:
  - `browser`
  - `web_search`
  - `web_fetch`
  - `image`
- Not touched:
  - `group:runtime`
  - `group:fs`

## Result
- `successful`
- narrowed only control-plane / session-orchestration surface on `main`
- next contour:
  - `employee workspace / safe business file tooling`
