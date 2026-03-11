# SERVER CHANGELOG 2026-03-11: BORIS WAVE 0 CHAT HARD STOP

## Scope
- Live apply on `S1`.
- Only:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
  - `commands.config: true -> false`
  - `commands.restart: true -> false`
  - `channels.telegram.configWrites: absent -> false`
- Out of scope:
  - `/route`
  - tools
  - model routing
  - plugins
  - bridge
  - workflows
  - monitoring
  - digest jobs

## Что было не так
- Boris conversational runtime on `S1` still exposed official chat-admin surfaces.
- Before apply:
  - `commands.config=true`
  - `commands.restart=true`
  - `channels.telegram.configWrites` was not explicitly disabled
- That left official persistent config writes and chat-triggered restart open from Boris Telegram/chat.
- Important architectural limit remained separate:
  - custom `/route` is not part of this contour and was intentionally not changed here.

## Что изменили
- Applied only one live file change:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
- Exact changed paths:
  - `commands.config: true -> false`
  - `commands.restart: true -> false`
  - `channels.telegram.configWrites: absent -> false`
- Nothing else was changed.

## Где backup
- `/root/boris-wave0-chat-hardstop-20260311T191320Z`
- Inside:
  - `openclaw.json.bak`
  - `telegram-config.json.bak`
  - `precheck.json`

## Pre-check
- Live source of truth confirmed:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
- Current values before apply:
  - `commands.config = true`
  - `commands.restart = true`
  - `channels.telegram.configWrites` absent / not disabled
- Unchanged baseline before apply:
  - `commands.ownerAllowFrom = ["telegram:395248122"]`
  - `commands.native = auto`
  - `commands.nativeSkills = auto`
  - `channels.telegram.groupPolicy = allowlist`
  - `channels.telegram.replyToMode = null`
  - `HQ requireMention = true`
  - `groups_count = 6`
  - `route-command.enabled = true`, `mode = bridge`
  - `callback-forward.enabled = true`
  - `Timur Morning Digest = agentId cron-timur-morning-digest, payload.model bridge/claude-opus-4-6`
  - `Timur Evening Digest = agentId cron-timur-evening-digest, payload.model bridge/claude-opus-4-6`
- Pre-apply `openclaw.json` hash:
  - `b65408e4d5d8634914f9b265e06ef9b07b03a9aa749cdc9ca5d5436b8824533c`

## Post-check
- Structural:
  - changed path count = `3`
  - changed paths:
    - `commands.config`
    - `commands.restart`
    - `channels.telegram.configWrites`
- Required values now:
  - `commands.config = false`
  - `commands.restart = false`
  - `channels.telegram.configWrites = false`
- Unchanged after apply:
  - `commands.ownerAllowFrom = ["telegram:395248122"]`
  - `channels.telegram.groupPolicy = allowlist`
  - `channels.telegram.replyToMode = null`
  - `HQ requireMention = true`
  - `groups_count = 6`
  - `route-command.enabled = true`, `mode = bridge`
  - `callback-forward.enabled = true`
  - digest job `agentId / payload.model` unchanged for both morning/evening jobs
- Post-apply `openclaw.json` hash:
  - `5252833fe034880f46b684f78e40cd32bf1e1934a63bee33d691d24f20c3cb15`

## Functional hard-stop proof
- `/config show` rejected:
  - `⚠️ /config is disabled. Set commands.config=true to enable.`
- `/config set ...` rejected:
  - `⚠️ /config is disabled. Set commands.config=true to enable.`
- `/restart` rejected:
  - `⚠️ /restart is disabled. Set commands.restart=true to enable.`
- `/allowlist add ...` rejected:
  - `⚠️ /allowlist edits are disabled. Set commands.config=true to enable.`
- `/allowlist remove ...` rejected:
  - `⚠️ /allowlist edits are disabled. Set commands.config=true to enable.`
- Hash after rejected `/config set` remained unchanged.

## Rollback required or not
- Rollback was not required.
- Immediate structural and functional post-check both passed.

## Important limit
- `/route` intentionally remained open.
- That contour is the next separate hardening wave and was not mixed into this apply.
- `telegram-config.json` may converge later via validator cycle; that is not an immediate failure condition for this Wave 0 apply.

## Итог
- `successful`
- Wave 0 official Boris chat-admin hard stop on `S1` is applied successfully.
