# SERVER AUDIT ADDENDUM 2026-03-11: TG RUNTIME BLOCKER CONTEXT

## Scope
- Docs-only фиксация текущего hardening-контекста после live pre-check on `S1`.
- No live apply.
- No backup.
- No post-change verification.
- Focus only:
  - Boris hardening state already completed on `2026-03-11`
  - current `/route` classification
  - Telegram inbound runtime blocker
  - next decision point and next contour

## Update 2026-03-12
- Этот файл сохраняется как historical stop-condition record именно для `2026-03-11`.
- Subsequent sections below keep original `2026-03-11` wording and must be read as historical context, not as current next-step guidance.
- Follow-up correction:
  - `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_TG_HEALTH_PATH_CONTRADICTION.md`
- Follow-up read-only audit on `2026-03-12` showed that the apparent Telegram runtime blocker was a telemetry issue, not a confirmed live outage.
- Telegram restore apply is not required after that correction.
- Next active hardening contour = `/route` closure.
- Do not use `openclaw gateway call health --json` as Telegram runtime proof on `S1`.
- Exact authoritative Telegram inbound check on `S1`:
  - `openclaw channels status --json --probe`
  - only in successful authenticated gateway context
  - without config-only fallback

## Executive summary
- Already applied before this addendum:
  - Wave 0 hard stop:
    - `commands.config=false`
    - `commands.restart=false`
    - `channels.telegram.configWrites=false`
  - Telegram helper token-resolution hardening
  - exact fallback chain isolation for:
    - `Timur Evening Digest`
    - `Timur Morning Digest`
- `/route` is not confirmed as an active live Telegram contour as of the verified follow-up on `2026-03-11`.
- `callback-forward` remains a separate internal hook contour and is not the same thing as `/route`.
- Live authenticated gateway snapshot on `2026-03-11` showed Telegram:
  - `configured=true`
  - `running=false`
  - `mode=null`
  - webhook empty
- Because Telegram inbound runtime was not running, `/route` closure was paused by stop condition and reclassified:
  - from `active contour closure`
  - to `stale-config cleanup candidate until Telegram runtime is restored or intentionally left off`
- Next planned contour is not `/route` closure.
- Historical next planned contour on `2026-03-11` = Telegram inbound runtime restore / audit on `S1`; this was later superseded by the `2026-03-12` telemetry correction.
- Do not mix Telegram runtime restore with `/route` closure.

## What was already completed before this stop

### Wave 0 official chat-admin hard stop
- Applied successfully on `2026-03-11`.
- Exact live keys closed:
  - `commands.config`
  - `commands.restart`
  - `channels.telegram.configWrites`
- Source:
  - `docs/ai/SERVER_CHANGELOG_2026-03-11_boris_wave0_chat_hardstop.md`

### Shared Telegram helper token hardening
- Applied successfully on `2026-03-11`.
- Historical helper token-resolution failure class was closed at helper layer.
- Source:
  - `docs/ai/SERVER_CHANGELOG_2026-03-11_tg_helper_token_hardening.md`

### Exact fallback isolation for Timur digest jobs
- Applied successfully on `2026-03-11`.
- Exact dedicated fallback chains now exist for:
  - `Timur Evening Digest`
  - `Timur Morning Digest`
- Source:
  - `docs/ai/SERVER_CHANGELOG_2026-03-11_digest_fallback_chain_morning_evening.md`

## Verified follow-up state for `/route`

### Repo-visible and live-verified facts from the follow-up pre-check
- Live config extract on `2026-03-11` showed:
  - `plugins.entries["route-command"].enabled=true`
  - `plugins.entries["route-command"].config.mode="bridge"`
  - `plugins.load.paths` contains `/data/route-command`
  - `hooks.internal.entries["callback-forward"].enabled=true`
- `openclaw hooks info callback-forward --json` confirmed:
  - `eligible=true`
  - `disabled=false`
  - `managedByPlugin=false`
  - `handlerPath=/data/.openclaw/hooks/callback-forward/handler.ts`
- `openclaw plugins list --json` reported `/data/route-command` as a blocked stale candidate because of suspicious ownership.
- Raw gateway authentication for read-only hello succeeded, but exact no-delivery `/route` probe through the public gateway API could not be executed with the available shared auth because agent call required missing scope:
  - `operator.write`

### Why `/route` was paused
- `/route` was being treated as the next hardening wave only if it was still an active live Telegram contour.
- The `2026-03-11` gateway snapshot instead showed Telegram inbound runtime not running.
- Because of that, current evidence does not prove that `/route` is active on a live Telegram inbound path right now.
- This is a stop condition for `/route` hardening as an active contour closure.
- Therefore `/route` must not be handled as a live incident or active Telegram delivery fix at this stage.

## Classification after the stop condition
- `/route` is currently classified as:
  - `not confirmed active live Telegram contour`
  - `paused hardening wave`
  - `stale-config cleanup candidate pending Telegram runtime decision`
- `callback-forward` is currently classified as:
  - `separate internal hook contour`
  - `not proof that /route is active`
  - `not to be mixed with Telegram inbound runtime restore`

## What must not be lost
- Do not treat `/route` as the current live incident.
- Do not start `/route` closure before Telegram inbound runtime is resolved.
- Do not mix:
  - Telegram inbound runtime restore / audit
  - `/route` closure or stale cleanup
- If Telegram inbound is restored later, `/route` must be re-checked again as a live contour before any closure plan.
- If Telegram inbound is intentionally off, `/route` should be handled as stale-config cleanup, not as active contour repair.

## Open questions
- Is Telegram inbound on `S1` supposed to be live right now?
- If yes:
  - why did the authenticated gateway snapshot on `2026-03-11` show `configured=true` but `running=false`?
- If no:
  - should `route-command` remain enabled in config at all?
  - should stale `/route` plugin/config residue be cleaned up later as a separate approved cleanup?

## Next decision point
- First owner decision:
  - Telegram inbound should be live
  - or Telegram inbound is intentionally off

## Historical next planned contour on 2026-03-11

### If Telegram inbound should be live
- Historical next contour on `2026-03-11` = Telegram inbound runtime restore / audit on `S1`.
- Only after that:
  - re-check `/route` as a real live contour
  - then decide whether `/route` needs closure as active hardening

### If Telegram inbound is intentionally off
- `/route` moves fully into stale-config cleanup.
- The next Boris chat-hardening contour after that becomes:
  - dangerous tools / `exec` narrowing
  - conversational model-picker narrowing

## Status
- `STOP_CONDITION_TRIGGERED`

## Verdict
- No apply was performed.
- No backup was created.
- No rollback was needed.
- Current preserved context:
  - Wave 0 hard stop already applied
  - helper token hardening already applied
  - morning/evening digest fallback isolation already applied
  - `/route` closure paused by Telegram runtime stop condition
  - historical next task on `2026-03-11` = Telegram inbound runtime restore / audit on `S1`; superseded by the `2026-03-12` telemetry correction
  - `/route` closure must remain a separate later decision
