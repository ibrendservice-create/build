# SERVER CHANGELOG 2026-03-13 B2 workspaceOnly apply

## Summary

B2 (`agents.list[id=main].tools.fs.workspaceOnly = true`) applied successfully on S1 internal Boris.

## What changed

- One field added: `agents.list[id=main].tools.fs.workspaceOnly = true` in `/data/.openclaw/openclaw.json`
- No other fields changed

## Pre-check (10/10 PASS)

1. Container healthy
2. `main` agent exists in agents.list
3. `main.tools.deny` = `['group:automation','group:nodes','sessions_spawn','sessions_send']`
4. `main.identity` = `Борис Ионов / AI бизнес-ассистент`
5. `route-command.enabled` = `false`
6. `commands.config` = `false`, `commands.restart` = `false`
7. 6 Telegram group overlays present and intact
8. `jobs.json` = 13 enabled, 0 on `main`
9. `fix-model-strategy.py` preserves entire existing `main` object (does not touch `main.tools`)
10. `main.tools.deny` survived real container restart at `2026-03-13T08:57:51Z` (K() patched via `server-patched.mjs`)

## Apply

- Method: `docker exec openclaw-kbxr-openclaw-1 python3 -c "..."` — JSON load, find `main`, set `tools.fs.workspaceOnly = True`, JSON dump
- Result: `OK: main.tools.fs.workspaceOnly = true`

## Post-check (9/9 PASS)

1. `main.tools.fs.workspaceOnly` = `True`
2. `main.tools.deny` = `['group:automation','group:nodes','sessions_spawn','sessions_send']` — unchanged
3. `main.identity` = `Борис Ионов / AI бизнес-ассистент / 🔧` — unchanged
4. Container = `healthy`
5. `jobs.json` = 13 enabled, 0 on `main` — unchanged
6. `route-command.enabled` = `False` — unchanged
7. 6 Telegram groups with all overlays intact — unchanged
8. `main.tools` keys = `['deny', 'fs']` only, no extra keys — semantic diff confirmed one-field change
9. No non-target drift in checked scope

## Backup

- Location: `S1:/root/b2-workspaceonly-20260313T091815Z/`
- Contents: `openclaw.json.bak` (26930 bytes), `pre-main-agent.json`, `pre-service-state.txt`
- Rollback: `cp "$BDIR/openclaw.json.bak" /var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`

## Rollback needed

No. All post-checks passed.

## Writer chain safety

- `fix-model-strategy.py` preserves entire existing `main` object including `main.tools` — will not overwrite `workspaceOnly`
- K() patched via `server-patched.mjs` bind mount — will not overwrite config
- `main.tools.deny` survived real container restart — same field family proven durable
- `workspace-validator.py` does not own `main.tools`
- `service-guard.py` tracks `openclaw.json` in baseline — potential stale-baseline rollback risk exists but is accepted architecture

## What stayed out of scope

- No restart
- No other `openclaw.json` fields changed
- No `jobs.json` changes
- No model routing changes
- No monitoring/self-healing changes
- No bridge/gateway changes

## Contour status

- B2 = **APPLIED**
- Boris XLSX proof chain = **CLOSED** (Step 1 PASS + Step 2 PASS + B2 APPLIED)
- `/route` closure = remains **CLOSED**
- Next truly open contours: owner policy layer, cron/master SoT migration, tender specialist skill hygiene, auth-profile/EACCES normalization
