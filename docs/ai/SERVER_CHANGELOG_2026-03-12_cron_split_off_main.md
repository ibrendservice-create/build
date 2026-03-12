# SERVER CHANGELOG 2026-03-12: CRON SPLIT OFF MAIN

## Layer
- `S1` internal OpenClaw cron agent ownership

## Scope
- only `/var/lib/apps-data/openclaw/data/model-strategy.json`
- one materialization run:
  - `docker exec openclaw-kbxr-openclaw-1 python3 /data/fix-model-strategy.py`

## Source of truth
- master:
  - `/var/lib/apps-data/openclaw/data/model-strategy.json`
- materialized runtime:
  - `/var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json`
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
- materialization path:
  - existing `/var/lib/apps-data/openclaw/data/fix-model-strategy.py`

## What was wrong
- stronger per-agent hardening of `main` was still blocked because enabled cron jobs were still using `main`
- latest live pre-state before apply:
  - `13` enabled jobs total
  - `2` dedicated digest jobs
  - `10` enabled jobs on `main`
  - `1` enabled implicit/default job:
    - `okdesk-comment-monitor`
- this kept cron ownership mixed with the shared `main` agent contour

## What changed
- added `11` exact `cron_job_routes` in `model-strategy.json` for the remaining jobs off `main`
- preserved without changes:
  - existing morning/evening digest routes
  - their fallback chains
- manual edit was only in `model-strategy.json`
- then executed one materialization run:
  - `docker exec openclaw-kbxr-openclaw-1 python3 /data/fix-model-strategy.py`
- derived effect:
  - `jobs.json`: updated `agentId` for `11` target jobs
  - `openclaw.json`: materialized `11` new cron agents in `agents.list`

## Jobs moved off main
- `Commitment Checker`
- `okdesk-supabase-sync`
- `gdrive-index-sync`
- `HH Monitor v3`
- `Email morning digest`
- `Email evening digest`
- `Weekly Self-Audit`
- `Price List Sync + Contract Check`
- `Дайджест развития — Штаб`
- `Дайджест развития — Канал мастеров`
- `okdesk-comment-monitor` moved off implicit/default path

## Backup
- backup dir:
  - `/root/cron-split-main-20260312T094923Z`
- files:
  - `/root/cron-split-main-20260312T094923Z/model-strategy.json.bak`
  - `/root/cron-split-main-20260312T094923Z/jobs.json.pre`
  - `/root/cron-split-main-20260312T094923Z/openclaw.json.pre`

## Pre-check
- `enabled_total=13`
- current split still = `2 dedicated + 10 main + 1 implicit`
- `model-strategy.json` still had exactly `2` `cron_job_routes`
- `fix-model-strategy.py` semantics unchanged:
  - exact-route bind branch still present
  - no shared-agent dedup in `agents.list` builder
- `circuit-breaker-internal.py` still did not touch `jobs.json` / `agentId`
- `openclaw.json -> agents.list` still only had `main + 2 digest agents`
- all `11` target jobs still kept:
  - `payload.model`
  - `schedule`
  - `delivery`
  - `sessionTarget`
  - `wakeMode`
- no new live script blocker was found beyond known main-session maintenance assumptions
- `Timur Morning Digest` still had isolated:
  - `lastStatus=error`
  - `consecutiveErrors=1`
  - but no broader cron incident was confirmed

## Post-check
- structural:
  - `model-strategy.json` now has `13` exact `cron_job_routes`
  - `jobs.json` now has `0` enabled jobs on `main`
  - `jobs.json` now has `0` implicit jobs
  - `openclaw.json -> agents.list` now has `14` entries = `main + 13 cron agents`
  - duplicate ids: none
- behavioral invariants unchanged for all `13` jobs:
  - `payload.model` unchanged
  - schedules unchanged
  - delivery unchanged
  - `sessionTarget` unchanged
  - `wakeMode` unchanged
- existing morning/evening digest routes unchanged
- no drift in provider config or global model routing
- near-term runtime proof:
  - `okdesk-comment-monitor` natural run observed on `cron-okdesk-comment-monitor` with `lastStatus=ok`
  - `HH Monitor v3` natural run observed on `cron-hh-monitor-v3` with `lastStatus=ok`
  - observed by `2026-03-12 10:04:04 UTC`

## Rollback
- not required

## Result
- `successful`
- enabled jobs on `main` = `0`
- main cron blocker removed
- stronger per-agent hardening of `main` is now unblocked
