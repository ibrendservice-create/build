# SERVER AUDIT ADDENDUM 2026-03-11: BORIS CHAT HARDENING

## Scope
- Docs-only audit addendum and apply plan.
- No live apply was performed by this document.
- Focus only: Boris / OpenClaw chat self-modification risk on `S1`.

## Executive summary
- Conversational Boris on `S1` is currently combined with operator/control surfaces.
- Confirmed high-risk live surfaces:
  - `commands.config=true`
  - `commands.restart=true`
  - `channels.telegram.configWrites` is not explicitly disabled and is therefore effectively enabled
  - custom `route-command` writes `openclaw.json` from chat
  - main Boris still exposes a broad conversational model picker
  - main Boris still has host-side dangerous tools
- Safe target state is narrower:
  - persistent changes only server-side via master-first apply
  - no persistent chat path for config, model, rules, plugin or restart changes
  - HQ `requireMention` remains only a chatter gate, not a self-protection mechanism
- Wave 0 should be a narrow hard stop for official chat-admin surfaces only:
  - `commands.config=false`
  - `commands.restart=false`
  - `channels.telegram.configWrites=false`
- Important limit:
  - Wave 0 does not fully close chat-admin
  - custom `/route` remains a separate open contour and must be handled in a later wave

## Current risk map

### Official operator surfaces currently live
- `commands.config=true` keeps official `/config*` chat mutation surface open.
- `commands.restart=true` keeps chat-triggered `/restart` open.
- `channels.telegram.configWrites` is absent in live config and therefore not explicitly disabled.
- These three fields currently live in:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`

### Custom operator surface currently live
- `route-command` remains enabled and writes `openclaw.json` from chat.
- This is not the same contour as official `/config`.
- Closing official `/config` and Telegram `configWrites` will not close custom `/route`.

### Additional dangerous but out-of-scope contours
- Main Boris still has a broad conversational model picker.
- Main Boris still has host-side dangerous tools.
- Those contours raise prompt-injection and self-modification risk, but they are not part of Wave 0.

### HQ gating is not a self-protection control
- HQ / Штаб `requireMention` is useful only as a chatter gate.
- It does not prevent operator-style mutations once Boris is explicitly addressed.
- It must not be treated as a substitute for hardening chat-admin surfaces.

## Target policy
- Persistent changes to config, models, rules, plugins, prompts, memory and restart behavior must go only through server-side master-first apply.
- Conversational Boris must not have a persistent chat path that can write `openclaw.json`, change routing, change fallbacks, change prompts/rules or restart the runtime.
- Group gating and prompt wording are not security controls.
- Operator/admin contours must be separated from conversational contours.
- Every future live change in this area must keep:
  - source of truth
  - writer/enforcer chain
  - rollback
  - post-check
  explicitly documented before apply.

## Wave 0 hard stop

### Scope
- Only these three changes:
  - `commands.config=false`
  - `commands.restart=false`
  - `channels.telegram.configWrites=false`
- Nothing else.

### Source of truth
- Current source of truth for Wave 0:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
- Important adjacent layer:
  - `/var/lib/apps-data/boris-doctor/backups/telegram-config.json`
  - this file is a periodic restore snapshot/cache, not the master for this wave

### Current live state confirmed by audit
- `commands.config=true`
- `commands.restart=true`
- `channels.telegram.configWrites` is absent and therefore not disabled
- `HQ requireMention=true`
- digest and cron contours do not depend on these three fields

### Writer / enforcer summary for this wave
- Current live canonical file for these exact fields is `openclaw.json`.
- No higher declarative master for these three keys was confirmed.
- `workspace-validator.py` refreshes `telegram-config.json` from current runtime Telegram config on its validator cycle, but that backup file is not master.
- `fix-model-strategy.py` and `circuit-breaker-internal.py` do not currently appear to own these exact keys.

### Acceptable impact
- The following chat-admin behaviors should stop working from chat:
  - `/config*`
  - `/restart`
  - Telegram `/allowlist add`
  - Telegram `/allowlist remove`
  - Telegram config writes and related chat-side config mutation flows
- The following remain outside Wave 0 scope and should keep working as before:
  - normal conversational Boris
  - digest delivery
  - cron jobs
  - tools
  - bridge
  - workflows

### Why this impact is acceptable
- These are operator/admin surfaces, not normal conversational behavior.
- The goal of Wave 0 is to close the easiest persistent self-modification surfaces first, with the smallest safe change set.

### Minimal apply plan
- Edit only:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
- Change only:
  - `commands.config: true -> false`
  - `commands.restart: true -> false`
  - `channels.telegram.configWrites: false` as an explicit new key
- Do not change:
  - tools / exec
  - `route-command`
  - `callback-forward`
  - model picker
  - model routing
  - bridge
  - workflows
  - monitoring
  - digest jobs

### Minimal post-check plan
- Immediate:
  - `commands.config=false`
  - `commands.restart=false`
  - `channels.telegram.configWrites=false`
  - no adjacent drift in `commands`, Telegram group config or digest-related config
- Functional:
  - `/config*` rejected from chat
  - `/restart` rejected from chat
  - Telegram `/allowlist add|remove` rejected from chat
  - attempted `/config set` does not mutate `openclaw.json`
- Important limitation:
  - even after a successful Wave 0 apply, custom `/route` remains open and is still a persistent chat write path until a separate fix closes it

## Remaining open risk
- `route-command` remains a separate persistent chat-routing/config contour.
- Broad conversational model-picker exposure remains open.
- Host-side dangerous tools on main Boris remain open.
- Conversational runtime is still not fully separated from operator/control-plane behavior.

## Next wave
- Separate `/route` from conversational Boris and remove persistent chat writes to `openclaw.json`.
- Narrow main Boris tool access and host-side execution surfaces.
- Narrow conversational model picker to the approved production subset.
- Keep prompt/rules/memory mutation on server-side only paths.

## Status
- Hardening analysis: documented.
- Wave 0 hard stop: planned, not applied by this document.
- Remaining open contour `/route`: explicitly documented as separate and still open.
