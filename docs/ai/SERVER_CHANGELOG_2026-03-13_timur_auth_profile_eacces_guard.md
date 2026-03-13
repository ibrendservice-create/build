# SERVER CHANGELOG 2026-03-13 — Timur auth-profile EACCES guard

## Contour
Timur Morning/Evening dedicated-agent auth-profile materialization / EACCES

## Classification
Prompt type **E** (Apply). Defensive dist patch via existing patcher pattern.

## What was wrong
- [LIVE] `saveJsonFile()` inside `loadAuthProfileStoreForAgent()` in OpenClaw dist uses `fs.writeFileSync` + `fs.chmodSync` with no try-catch.
- [LIVE] When auth-profiles.json file ownership is root (from `docker exec` / doctor / watchdog writes), the node-uid (1000) gateway process gets EACCES on the write path.
- [LIVE] `loadJsonFile()` swallows all errors (including EACCES on read), but `saveJsonFile()` propagates exceptions.
- [LIVE] This breaks dedicated-agent cron sessions (`cron-timur-morning-digest`, `cron-timur-evening-digest`) when their `auth-profiles.json` has wrong ownership.
- [LIVE] Two separate dist installations exist on S1:
  - `.npm-global` family: `auth-profiles-GYsKiVaE.js` (ACTIVE — gateway resolves through this family)
  - `/usr/local` family: `auth-profiles-DSWJsDjg.js` (INACTIVE — different version, not used by running gateway)
- [LIVE] Both files contained the same unguarded `saveJsonFile(authPath, ...)` calls inside `loadAuthProfileStoreForAgent` (3 calls each).

## What was changed

### Created
| File | Host path | Purpose |
|---|---|---|
| Patcher script | `/var/lib/apps-data/openclaw/data/patch-auth-profiles-fix.sh` (= container `/data/patch-auth-profiles-fix.sh`) | Idempotent marker-based dist patcher following `patch-reasoning-fix.sh` pattern |

### Edited
| File | Host path | Change |
|---|---|---|
| `startup-cleanup.sh` | `/opt/apps/openclaw/startup-cleanup.sh` | Added patcher hook block at lines 69-77, after existing `failover-patcher.py` block, before memory ownership fix. Same `if -f / bash / || WARNING` pattern. |

### Runtime patch targets (applied by patcher on container restart)
| Container path | Change | Calls patched |
|---|---|---|
| `/data/.npm-global/lib/node_modules/openclaw/dist/auth-profiles-GYsKiVaE.js` | Injected `__safeSaveAuthStore` wrapper before `loadAuthProfileStoreForAgent`; replaced 3 `saveJsonFile(authPath,` calls inside function with safe wrapper | 3 |
| `/usr/local/lib/node_modules/openclaw/dist/auth-profiles-DSWJsDjg.js` | Same replacement | 3 |

### Patch semantics
- Wrapper catches only `EACCES`, re-throws everything else.
- On EACCES: logs `[auth-profiles-eacces-guard] EACCES writing <path> -- skipping write` to stderr.
- Calling code continues normally — the store was already loaded in memory, so the function still returns it.
- `saveJsonFile(authPath, ...)` calls OUTSIDE `loadAuthProfileStoreForAgent` (e.g. line 2992 in npm-global) remain untouched.
- Marker: `auth-profiles-eacces-guard v1`.

### Container restart
- `docker restart openclaw-kbxr-openclaw-1` executed.
- New gateway PID: 9489 (previously 9461).

## Backup locations

| Backup | Path | Host-accessible |
|---|---|---|
| startup-cleanup.sh | `/opt/apps/openclaw/startup-cleanup.sh.bak-auth-fix` | Yes |
| auth-profiles (npm-global) | `/data/.npm-global/lib/node_modules/openclaw/dist/auth-profiles-GYsKiVaE.js.bak-auth-fix` | Yes (via `/var/lib/apps-data/openclaw/data/...`) |
| auth-profiles (usr-local) | `/usr/local/lib/node_modules/openclaw/dist/auth-profiles-DSWJsDjg.js.bak-auth-fix` | Container writable layer only (lost on `docker compose up --force-recreate`; patcher re-applies) |

## Pre-check result

| Check | Result |
|---|---|
| Both dist targets exist, no marker | PASS |
| startup-cleanup.sh has no auth-profiles hook | PASS |
| auth-profiles.json files exist (node:node 0600) | PASS |
| Container running, gateway PID 9461 | PASS |
| `saveJsonFile(authPath,` calls present in both files | PASS |

## Immediate post-check result

| Check | Result |
|---|---|
| Gateway running (new PID 9489) | PASS |
| Marker `auth-profiles-eacces-guard v1` in npm-global dist | PASS |
| Marker `auth-profiles-eacces-guard v1` in usr-local dist | PASS |
| Patcher log: 3 calls patched in each file | PASS |
| No startup errors (no ERROR/FATAL in log) | PASS |
| Both `.bak-auth-fix` backup files created | PASS |
| Scoped replacement: `saveJsonFile(authPath,` on line 2992 (outside function) untouched | PASS |
| Startup sequence: reasoning → failover → auth-profiles → cleanup done → post-K fixer → model-fix | PASS |

## Deferred post-check — PENDING

Waiting for the next natural Timur morning or evening digest cron run. At that time verify:
1. Cron session completes without EACCES.
2. `auth-profiles.json` mtime for `cron-timur-morning-digest` or `cron-timur-evening-digest` updated after restart time.
3. Either no `[auth-profiles-eacces-guard]` warning in container logs (ownership clean) OR warning present (guard caught EACCES gracefully — not a failure).

## Rollback

Not triggered. All immediate post-checks passed.

Rollback procedure if needed:
1. `cp /opt/apps/openclaw/startup-cleanup.sh.bak-auth-fix /opt/apps/openclaw/startup-cleanup.sh` (host)
2. `cp .../auth-profiles-GYsKiVaE.js.bak-auth-fix .../auth-profiles-GYsKiVaE.js` (host)
3. `docker exec ... cp .../auth-profiles-DSWJsDjg.js.bak-auth-fix .../auth-profiles-DSWJsDjg.js` (container)
4. `docker restart openclaw-kbxr-openclaw-1`
5. Verify gateway running, no patched markers, no startup errors.

## Stop condition

No stop condition triggered. Pre-check matched expectations. Apply stayed within approved scope.

## Result

- **Immediate apply**: successful.
- **Contour closure**: pending deferred post-check on next natural Timur cron run.
- **Contour status**: `applied, awaiting deferred verification`.

## Closure addendum — 2026-03-13

- Owner decision: Option A (closure by applied-live evidence + code inspection).
- Deferred trigger-based proof waived.
- Natural trigger path did not occur: all Timur/Email digest cron jobs have `lastRunAtMs=null`, `nextRunAtMs=null` — never run.
- `auth-profiles.json` does not currently exist on S1 (trigger scenario has not manifested since restart).
- Zero EACCES crashes observed in container logs since patch.
- Patch startup-persistence confirmed across restarts (patcher ran at `11:57:51` container start).
- Both dist families confirmed patched live (4 `__safeSaveAuthStore` refs each).
- Cron scheduler issue (`nextRunAtMs=null`) is a separate pre-existing concern, not part of this closure.
- No new contour opened.
- **Contour status**: `CLOSED`.

## Source doc references

- Wave handoff: `docs/ai/HANDOFF_WAVE_2026-03-13_timur_auth_profile_eacces.md`
- Gateway restart authorization: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_S1_GATEWAY_RESTART_AUTHORIZATION_PATH.md`
- Dedicated agent materialization: `docs/ai/SERVER_CHANGELOG_2026-03-11_digest_fallback_chain_morning_evening.md`
- Writer/enforcer map: `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md`
