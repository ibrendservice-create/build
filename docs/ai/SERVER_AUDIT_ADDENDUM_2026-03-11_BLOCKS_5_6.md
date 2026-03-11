# SERVER AUDIT ADDENDUM 2026-03-11 BLOCKS 5 6

Docs-only фиксация результатов narrow read-only audit по:
- Block 5. `Bridge / OAuth / HA delivery`
- Block 6. `OpenClaw runtime и config protection`

Изменения в live не выполнялись.
Это не apply changelog и не live fix.

## Block 5. Bridge / OAuth / HA delivery

Статус:
- `OK`
- live issue not confirmed
- `docs/mental-model drift`, not live issue

### Что проверено

- Repo canon и dated audit docs:
  - `docs/ai/BORIS_DETAIL_SCHEMA_CHECKLIST_v2.md`
  - `docs/ai/BASELINE_2026-03-10.md`
  - `docs/ai/OPERATING_CONSENSUS.md`
  - `docs/ai/SOURCE_OF_TRUTH.md`
  - `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BRIDGE_HA.md`
  - `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`
- Read-only live checks:
  - `S1` local health:
    - `http://127.0.0.1:3100/health`
    - `http://127.0.0.1:3102/health`
    - `http://127.0.0.1:8443/health`
  - public probes:
    - `https://n8n.brendservice24.ru/bridge-ha/health`
    - `https://ops.brendservice24.ru/bridge-ha/health`
  - live ingress blocks:
    - `S1 /etc/nginx/sites-enabled/n8n-public-edge`
    - `S1 /etc/nginx/sites-enabled/claude-bridge`
    - `S2 /etc/caddy/Caddyfile`

### Что ок

- local bridge health on `S1` = `OK`:
  - `3100` returns `200 application/json`
  - `3102` returns `200 application/json`
  - `8443` returns `200 application/json`
- canonical public probe is confirmed:
  - `https://n8n.brendservice24.ru/bridge-ha/health`
- valid public probe must include all three conditions:
  - `HTTP 200`
  - `content-type: application/json`
  - JSON body health response
- live ingress mapping matches canon:
  - `S1 nginx` keeps `/bridge-ha/*` on `n8n.brendservice24.ru`
  - `S1 nginx` keeps `/openai/v1/*` on local `3102`
  - `S1 nginx` keeps `/hooks/*` on OpenClaw hooks backend
  - `S2 Caddy` keeps `/bridge-ha/*` with `S1:8443` primary and `127.0.0.1:3100` fallback

### Что drift

- `ops.brendservice24.ru/bridge-ha/health` is not canonical health source.
- `ops` domain itself is alive, but `/bridge-ha/*` on that domain is not a supported canonical health route.
- Probe logic based only on `HTTP 200` remains insufficient and can produce false-positive diagnosis.
- Current drift class here = docs / mental-model ambiguity, not confirmed live outage.

### Что risky

- Remaining risk is false-positive diagnosis:
  - wrong public URL
  - `HTTP 200` without JSON validation
- `Bridge instability under load` remains a known risk class, but this audit did not confirm a current outage.
- Live repair is not required for the current contour.

### Что требует owner decision

- Only if the owner wants supported public `/bridge-ha/*` routing on `ops.brendservice24.ru`.

### Что требует approve

- Any live changes to:
  - OAuth creds
  - bridge config
  - ingress / failover logic
  - public routing around `/bridge-ha/*`
  - monitoring logic that would treat `ops.../bridge-ha/*` as canonical

### Вердикт

- `OK`
- canonical public probe = `https://n8n.brendservice24.ru/bridge-ha/health`
- `ops.brendservice24.ru/bridge-ha/health` is not canonical
- current problem class = `docs/mental-model drift`, not live issue
- live repair not required

## Block 6. OpenClaw runtime и config protection

Статус:
- `OK with WARN`
- live outage not confirmed
- layered runtime, not single-master contour

### Что проверено

- Repo canon и dated audit docs:
  - `docs/ai/BORIS_DETAIL_SCHEMA_CHECKLIST_v2.md`
  - `docs/ai/BASELINE_2026-03-10.md`
  - `docs/ai/SOURCE_OF_TRUTH.md`
  - `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`
  - `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_MODEL_ROUTING.md`
  - `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`
  - `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md`
  - `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`
- Read-only live checks on `S1`:
  - `docker inspect openclaw-kbxr-openclaw-1`
  - mounts and entrypoint
  - runtime files inside container
  - `crontab` references
  - live scripts:
    - `startup-cleanup.sh`
    - `fix-model-strategy.py`
    - `circuit-breaker-internal.py`
  - safe summary checks for:
    - `/data/model-strategy.json`
    - `/data/.openclaw/openclaw.json`
    - `/data/.openclaw/cron/jobs.json`
    - prompt/memory paths
  - `startup-cleanup.log`

### Что ок

- internal runtime is confirmed:
  - `openclaw-kbxr-openclaw-1`
- container is `running` and `healthy`
- config protection is confirmed as layered
- runtime/generated files are not master
- effective/runtime layer includes:
  - `/data/model-strategy.json`
  - `/data/.openclaw/openclaw.json`
  - `/data/.openclaw/cron/jobs.json`
- writer/enforcer contour is confirmed:
  - `startup-cleanup.sh`
  - `fix-model-strategy.py`
  - `circuit-breaker-internal.py`
- current effective runtime remains consistent with canon:
  - internal default-chain in effective config stays on `bridge/claude-sonnet-4-6`
  - cron runtime stays on `bridge/claude-opus-4-6`
- current contour is not a confirmed live outage

### Что drift

- This contour is not a single-master layout.
- Snapshot assumptions that treat runtime files as master remain wrong for current live architecture.
- Additional noise confirmed in startup verification:
  - false-warning around `/data/server.mjs` vs `/hostinger/server.mjs`
  - patched runtime file is mounted at `/hostinger/server.mjs`
  - startup verification logic can still emit warning against `/data/server.mjs`
- This is operational/docs drift and noisy verification, not a confirmed runtime break.

### Что risky

- Main risk = layered source-of-truth confusion + overwrite risk.
- Direct edits to runtime/generated files remain unstable because active writers/enforcers can rewrite them.
- Current contour keeps these overwrite risks:
  - startup post-`K()` repair
  - runtime config rewrite from `fix-model-strategy.py`
  - emergency runtime rewrite from `circuit-breaker-internal.py`
- Additional risk:
  - startup false-warning may mislead future audits into thinking runtime patching is broken when live contour is still working.
- Live repair is not required for the current contour.

### Что требует owner decision

- Only for future architectural simplification of the layered contour.
- Possible future action:
  - docs cleanup only
  - architectural simplification only by separate decision

### Что требует approve

- Any live changes to:
  - generated/runtime config directly
  - startup scripts
  - patchers
  - container entrypoint/mounts
  - prompt/memory live layout
- In practice this includes:
  - `openclaw.json`
  - `jobs.json`
  - `models.json`
  - `startup-cleanup.sh`
  - `fix-model-strategy.py`
  - `circuit-breaker-internal.py`

### Вердикт

- `OK with WARN`
- internal runtime = `openclaw-kbxr-openclaw-1`
- current contour is layered runtime, not single-master
- main problem class = source-of-truth confusion and overwrite risk, not confirmed live outage
- live repair not required
