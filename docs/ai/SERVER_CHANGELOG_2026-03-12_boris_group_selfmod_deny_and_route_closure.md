# SERVER CHANGELOG 2026-03-12: BORIS GROUP SELF-MOD DENY AND /ROUTE CLOSURE

## Scope
- Live apply on `S1`.
- Only:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
- Exact changes:
  - `plugins.entries.route-command.enabled: true -> false`
  - added identical `tools.deny` to 6 Telegram groups:
    - `-1002799098412`
    - `-1003750223589`
    - `-1001927186400`
    - `-5245442089`
    - `-5091773177`
    - `-4972868360`
  - exact deny list:
    - `group:runtime`
    - `group:automation`
    - `group:nodes`
    - `sessions_spawn`
    - `sessions_send`
- Out of scope:
  - `jobs.json`
  - per-agent `main` policy
  - plugin files
  - hooks
  - model changes
  - digests
  - DMs
  - cron/main migration

## Что было не так
- After Wave 0, custom `/route` still remained as a separate persistent chat-write contour.
- The 6 shared Telegram groups still had no group-scoped tool deny layer for runtime/self-admin classes.
- Boris employee capabilities had to be preserved while denying self-modification and self-admin in shared groups.
- One mandatory pre-check baseline was re-baselined as acceptable drift:
  - enabled jobs total = `13`
  - enabled jobs on `main` = `10`
  - `okdesk-comment-monitor` is enabled with `agentId=null`
- Why that drift did not change the chosen strategy:
  - `main` still carries live jobs
  - stronger per-agent hardening of `main` remains unsafe
  - therefore group-scoped hardening remained the correct wave

## Что изменили
- Applied only one live file change:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
- Exact changed paths:
  - `plugins.entries.route-command.enabled: true -> false`
  - `channels.telegram.groups.-1002799098412.tools.deny`
  - `channels.telegram.groups.-1003750223589.tools.deny`
  - `channels.telegram.groups.-1001927186400.tools.deny`
  - `channels.telegram.groups.-5245442089.tools.deny`
  - `channels.telegram.groups.-5091773177.tools.deny`
  - `channels.telegram.groups.-4972868360.tools.deny`
- Nothing else was changed.

## Где backup
- Backup dir:
  - `/root/boris-route-closure-wave-20260312T083545Z`
- Backup file:
  - `/root/boris-route-closure-wave-20260312T083545Z/openclaw.json.bak`
- Additional apply artifacts:
  - `/root/boris-route-closure-wave-20260312T083545Z/precheck.json`
  - `/root/boris-route-closure-wave-20260312T083545Z/ROLLBACK.txt`

## Pre-check
- Wave 0 still live:
  - `commands.config=false`
  - `commands.restart=false`
  - `channels.telegram.configWrites=false`
- All 6 target groups existed.
- All 6 target groups had no `tools` overrides before apply.
- `plugins.entries.route-command.enabled=true` before apply.
- `openclaw plugins list --json` still showed `route-command` as a blocked stale candidate.
- `callback-forward` remained separate and `eligible=true`.
- Accepted re-baseline for this run:
  - enabled jobs total = `13`
  - enabled jobs on `main` = `10`
  - `okdesk-comment-monitor` enabled with `agentId=null`
- Strategy unchanged because:
  - `main` still carries live jobs
  - per-agent `main` hardening remains unsafe
  - this wave stayed group-scoped only

## Post-check

### Structural
- `plugins.entries.route-command.enabled=false`
- All 6 target groups now contain exact `tools.deny`:
  - `group:runtime`
  - `group:automation`
  - `group:nodes`
  - `sessions_spawn`
  - `sessions_send`
- Semantic diff in `openclaw.json` contains only 7 expected paths:
  - `plugins.entries.route-command.enabled`
  - the 6 exact `channels.telegram.groups.*.tools` paths above

### Functional
- `/route` is formally closed:
  - `route-command.enabled=false`
  - `route-command` is not present as a loaded plugin
  - live CLI warnings continue to classify it as stale config / blocked candidate, not active loaded contour
- Live OpenClaw resolver proof for all 6 groups shows denied:
  - `exec`
  - `process`
  - `bash`
  - `gateway`
  - `cron`
  - `nodes`
  - `sessions_spawn`
  - `sessions_send`
- Preserved employee capabilities in those same groups:
  - `browser=true`
  - `web_search=true`
  - `web_fetch=true`
  - `image=true`

### Adjacent
- `callback-forward` unchanged:
  - `eligible=true`
  - `disabled=false`
  - `managedByPlugin=false`
- Model routing unchanged.
- Per-agent `main` policy unchanged.
- Plugin files / hooks / jobs / digests / DMs were not edited.

### Adjacent note for jobs
- `jobs.json` raw hash moved during the post-check window.
- Treat this as runtime scheduler churn, not apply drift.
- Semantic invariants remained:
  - enabled total = `13`
  - enabled on `main` = `10`
  - `okdesk-comment-monitor` still `agentId=null`
  - morning/evening digests still use dedicated agents and `bridge/claude-opus-4-6`

## Rollback required or not
- Rollback was not required.

## Important limit
- `group:fs` intentionally remains open in this wave.
- File-based self-modification risk is reduced but not fully removed yet.

## Итог
- `successful`
