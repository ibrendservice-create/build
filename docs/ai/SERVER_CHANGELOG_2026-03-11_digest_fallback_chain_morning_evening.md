# SERVER CHANGELOG 2026-03-11 DIGEST FALLBACK CHAIN MORNING EVENING

## Что было не так

- У `Timur Evening Digest` и `Timur Morning Digest` не было exact fallback chain.
- Оба digest jobs изначально сидели на shared contour через `agentId=main`.
- При лимитах или недоступности primary модели не было узкого per-job failover только для этих двух jobs.

## Что изменили

- В `model-strategy.json` добавлены exact `cron_job_routes` для двух jobs:
  - `879abd47-d390-4a77-84ba-0e4631130278` `Timur Evening Digest`
  - `e5dff9f8-49ea-4623-8427-58ba62499a3b` `Timur Morning Digest`
- Runtime materialized dedicated non-default agents:
  - `cron-timur-evening-digest`
  - `cron-timur-morning-digest`
- Exact fallback chain для обоих jobs теперь:
  - primary = `bridge/claude-opus-4-6`
  - fallback 1 = `openai-bridge2/gpt-5`
  - fallback 2 = `openai/gpt-5`
  - fallback 3 = `nvidia/moonshotai/kimi-k2.5`
- `payload.model` у обоих jobs оставлен `bridge/claude-opus-4-6`.
- Delivery contour не менялся.
- Unrelated cron jobs не менялись.

## Что не меняли

- delivery blocks
- old positional send
- raw numeric target fallback
- HQ requireMention
- telegram-config
- workspace-validator
- bridge / monitoring / workflows
- OpenClaw core runtime

## Где backup

- `Timur Evening Digest`:
  - job id = `879abd47-d390-4a77-84ba-0e4631130278`
  - dedicated agent = `cron-timur-evening-digest`
  - backup = `/root/timur-evening-fallback-20260311T164648Z`
- `Timur Morning Digest`:
  - job id = `e5dff9f8-49ea-4623-8427-58ba62499a3b`
  - dedicated agent = `cron-timur-morning-digest`
  - backup = `/root/timur-morning-fallback-20260311T165436Z`

## Pre-check

Подтверждено до apply:

- exact live job ids:
  - evening = `879abd47-d390-4a77-84ba-0e4631130278`
  - morning = `e5dff9f8-49ea-4623-8427-58ba62499a3b`
- before rollout оба digest jobs были на shared contour через `agentId=main`
- current `payload.model` for both = `bridge/claude-opus-4-6`
- current delivery contour for both был зафиксирован и не входил в scope apply
- live allowlist уже содержал:
  - `bridge/claude-opus-4-6`
  - `openai-bridge2/gpt-5`
  - `openai/gpt-5`
  - `nvidia/moonshotai/kimi-k2.5`
- before morning apply отдельно подтверждено, что evening job уже имеет свой dedicated agent profile и не должен быть изменён second apply

## Post-check

Подтверждено после apply:

- `Timur Evening Digest` -> `agentId = cron-timur-evening-digest`
- `Timur Morning Digest` -> `agentId = cron-timur-morning-digest`
- `agents.list` содержит:
  - `main`
  - `cron-timur-evening-digest`
  - `cron-timur-morning-digest`
- `payload.model` unchanged for both = `bridge/claude-opus-4-6`
- delivery hash unchanged for both
- message hash unchanged for both
- `changed_non_target_count = 0`
- shared `agents.defaults.model.fallbacks` не менялся

Важно:

- structural apply = successful
- natural run verification ещё впереди
- forced canary / forced-fallback test отдельно не выполнялся
- next operational validation should rely on real sent markers from morning/evening natural runs

## Rollback required or not

- `Rollback required` = `no`
- Причина: оба apply прошли в согласованном scope, structural post-check подтвердил exact target bindings и отсутствие drift вне scope

## Итог

- `successful`
