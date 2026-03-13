# SERVER CHANGELOG 2026-03-13: RAW INBOUND GUARD PATCH LOCATION CORRECTION

## Scope
- Live apply on `S1`
- Edited only:
  - `/data/patch-reasoning-fix.sh`
  - `/usr/local/lib/node_modules/openclaw/dist/reply-XaR8IPbY.js`
  - `/usr/local/lib/node_modules/openclaw/dist/subagent-registry-eWk4_pdR.js`
- Activation:
  - one `docker restart openclaw-kbxr-openclaw-1`
- No canary
- No `Step 1`
- No `Step 2`
- No `B2`

## What was wrong
- Read-only root-cause audit had already confirmed that the real permission-authentic `Step 1` native `read` used the embedded fallback hook in:
  - `/usr/local/lib/node_modules/openclaw/dist/subagent-registry-eWk4_pdR.js`
- The approved raw-inbound guard patch had previously been prepared only for:
  - `/usr/local/lib/node_modules/openclaw/dist/reply-XaR8IPbY.js`
- Live pre-check on `2026-03-13` then confirmed a broader drift in the active patcher state:
  - current `/data/patch-reasoning-fix.sh` had no `RAW_INBOUND_GUARD`
  - no reply coverage remained
  - no `subagent-registry-eWk4_pdR.js` coverage existed
- Because of that state, repeating the old contour would not have activated the raw-inbound guard in either live target bundle family.

## What changed
- Restored the exact previously approved reply guard block from the saved local artifact:
  - `/tmp/raw-inbound-idempotency-v2.swuPsF/patch-reasoning-fix.sh`
- Added the same raw-inbound guard coverage for:
  - `/usr/local/lib/node_modules/openclaw/dist/subagent-registry-eWk4_pdR.js`
- Kept guard semantics unchanged:
  - same `RAW_INBOUND_GUARD v1` marker
  - same `/data/scripts/stage-inbound-media.py` helper call
  - same staged-path validation under `/data/.openclaw/workspace/downloads/inbound/`
  - same deny behavior for raw inbound `write` and `edit`
- Materialized the corrected runtime targets and activated them only through the approved container restart.

## Backup
- Backup dir:
  - `/tmp/raw-inbound-guard-corrected-20260313T044039Z`
- Backup files:
  - `/tmp/raw-inbound-guard-corrected-20260313T044039Z/patch-reasoning-fix.sh.bak`
  - `/tmp/raw-inbound-guard-corrected-20260313T044039Z/reply-XaR8IPbY.js.bak`
  - `/tmp/raw-inbound-guard-corrected-20260313T044039Z/subagent-registry-eWk4_pdR.js.bak`

## Pre-check
- Confirmed current live `/data/patch-reasoning-fix.sh` had:
  - no `RAW_INBOUND_GUARD`
  - no reply coverage
  - no subagent coverage
- Confirmed saved artifact existed and contained the previously approved reply guard block.
- Confirmed active embedded fallback still resolved to:
  - `register.agent-DDb5dBWx.js -> subagent-registry-eWk4_pdR.js`
- Confirmed `runBeforeToolCallHook` existed in both live targets:
  - `/usr/local/lib/node_modules/openclaw/dist/reply-XaR8IPbY.js`
  - `/usr/local/lib/node_modules/openclaw/dist/subagent-registry-eWk4_pdR.js`
- Confirmed `/startup-cleanup.sh` still invoked `/data/patch-reasoning-fix.sh`.
- Confirmed `commands.restart=false`.
- Confirmed `B2` still blocked in canon.
- Confirmed no canary was run in this contour.

## Post-check
- Live `/data/patch-reasoning-fix.sh` now contains:
  - reply coverage
  - `subagent-registry-eWk4_pdR.js` coverage
- Live `/usr/local/lib/node_modules/openclaw/dist/reply-XaR8IPbY.js` contains `RAW_INBOUND_GUARD v1`.
- Live `/usr/local/lib/node_modules/openclaw/dist/subagent-registry-eWk4_pdR.js` contains `RAW_INBOUND_GUARD v1`.
- `/startup-cleanup.sh` remained unchanged.
- `/data/scripts/stage-inbound-media.py` remained unchanged.
- Container `openclaw-kbxr-openclaw-1` returned to `running healthy` after the restart.
- `commands.restart=false` remained unchanged.
- `B2` remained blocked.
- No non-target drift was detected in the checked scope.

## Rollback required or not
- Rollback was not required.

## Result
- `successful`
