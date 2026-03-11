# SERVER AUDIT ADDENDUM 2026-03-11 BLOCKS 5 6 7 8

Docs-only фиксация результатов narrow read-only audit по:
- Block 5. `Bridge / OAuth / HA delivery`
- Block 6. `OpenClaw runtime и config protection`
- Block 7. `Model routing и cron model layer`
- Block 8. `Prompt / rules / memory source of truth`

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

## Block 7. Model routing и cron model layer

Статус:
- `OK with WARN`
- live outage not confirmed
- docs/architecture drift + overwrite risk, not confirmed runtime failure

### Что проверено

- Repo canon и dated audit docs:
  - `docs/ai/BORIS_DETAIL_SCHEMA_CHECKLIST_v2.md`
  - `docs/ai/BASELINE_2026-03-10.md`
  - `docs/ai/SOURCE_OF_TRUTH.md`
  - `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`
  - `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_MODEL_ROUTING.md`
  - `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md`
  - `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`
- Read-only live checks on `S1`:
  - internal `model-strategy.json`
  - internal `.openclaw/openclaw.json`
  - internal `.openclaw/cron/jobs.json`
  - internal `fix-model-strategy.py`
  - internal `circuit-breaker-internal.py`
  - `startup-cleanup.sh`
  - host `crontab`
  - external `.openclaw/openclaw.json`
  - external `fix-model-strategy.py`
- Сверены три слоя:
  - internal default-chain
  - internal cron declarative/runtime layer
  - external Boris chain

### Что ок

- internal default-chain master confirmed:
  - `model-strategy.json`
- internal cron declarative master remains tied to:
  - `model-strategy.json`
- internal cron effective runtime confirmed:
  - `jobs.json`
- current live internal cron model confirmed:
  - `bridge/claude-opus-4-6`
- current internal default-chain remains consistent with strategy:
  - primary `bridge/claude-sonnet-4-6`
  - subagents `bridge/claude-opus-4-6`
- external chain master confirmed:
  - external `fix-model-strategy.py`
- external effective runtime remains:
  - `anthropic/claude-haiku-4-5 -> openai/gpt-5`
- fixer ownership is confirmed:
  - internal `fix-model-strategy.py` reads `model-strategy.json` and writes `openclaw.json`, `jobs.json`, `models.json`
  - `startup-cleanup.sh` runs internal `fix-model-strategy.py`
  - `circuit-breaker-internal.py` mutates internal `openclaw.json`, but is not source of truth for cron models
- current contour is not a confirmed live outage

### Что drift

- This contour is not a single-master layout.
- Runtime/effective files are easy to misread as master:
  - internal `.openclaw/openclaw.json`
  - internal `.openclaw/cron/jobs.json`
  - external `.openclaw/openclaw.json`
- Snapshot and mental-model drift remain around routing ownership:
  - internal default-chain and cron model layers are split
  - external chain uses a different master/enforcer model
- Internal and external enforcement are not symmetric:
  - external fixer is explicitly minutely enforced
  - internal cron model enforcement is confirmed via startup fixer and writer chain, but not as a symmetric minute-enforcer for `jobs.json`
- Current drift class here = docs/architecture drift, not confirmed live break.

### Что risky

- Main risk = docs/architecture drift + overwrite risk.
- Direct edits to runtime layer remain unstable:
  - internal `openclaw.json`
  - internal `jobs.json`
  - external `openclaw.json`
- Internal/external enforcement asymmetry increases diagnostic risk:
  - external layer is more explicitly enforced
  - internal cron runtime can be wrongly assumed to have the same enforcement semantics
- `circuit-breaker-internal.py` can temporarily mutate internal default-chain, which increases layering complexity, but it still should not be treated as source of truth for cron models.
- Live repair is not required for the current contour.

### Что требует owner decision

- Only for future simplification or consolidation of routing architecture.
- Possible future action:
  - docs cleanup only
  - architecture simplification only by separate decision

### Что требует approve

- Any live changes to:
  - `model-strategy.json`
  - internal/external `openclaw.json`
  - internal `jobs.json`
  - internal/external `fix-model-strategy.py`
  - `circuit-breaker-internal.py`
  - `startup-cleanup.sh`
  - related cron entries

### Вердикт

- `OK with WARN`
- internal default-chain master = `model-strategy.json`
- internal cron declarative master is tied to `model-strategy.json`
- internal cron runtime = `jobs.json`
- live cron model = `bridge/claude-opus-4-6`
- external chain master = external `fix-model-strategy.py`
- direct runtime edits are unstable
- current problem class = docs/architecture drift + overwrite risk, not confirmed live outage
- live repair not required

## Block 8. Prompt / rules / memory source of truth

Статус:
- `OK with WARN`
- live issue not confirmed
- rules path canon confirmed, not live issue

### Что проверено

- Repo canon и dated audit docs:
  - `docs/ai/BORIS_DETAIL_SCHEMA_CHECKLIST_v2.md`
  - `docs/ai/BASELINE_2026-03-10.md`
  - `docs/ai/SOURCE_OF_TRUTH.md`
  - `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`
  - `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`
- Read-only live checks on `S1` / inside internal container:
  - `/data/.openclaw/workspace/memory/RULES.md`
  - `/data/.openclaw/memory/RULES.md`
  - `/data/.openclaw/SOUL.md`
  - `/data/CLAUDE.md`
  - `.openclaw/memory` content
  - `.openclaw/workspace/memory` content
- Read-only scans for loader/bootstrap and competing rule-source assumptions:
  - live refs to `workspace/memory/RULES.md`
  - live refs to `.openclaw/memory/RULES.md`
  - live refs to `.openclaw/SOUL.md`
  - presence scan for `RULES.md` / `SOUL.md` under `.openclaw`

### Что ок

- rules source of truth is confirmed:
  - `/data/.openclaw/workspace/memory/RULES.md`
- `/data/.openclaw/memory` is confirmed as storage path, not rules path
- `/data/.openclaw/SOUL.md` is absent
- `/data/CLAUDE.md` exists, but is not confirmed as master rules source
- competing active rules master is not confirmed
- current contour is not a confirmed live issue

### Что drift

- Snapshot and mental-model drift remain around rules paths:
  - `.openclaw/SOUL.md`
  - `.openclaw/memory/RULES.md`
- These stale paths do not match current canon.
- There is a workspace-level `SOUL.md` artefact under `/data/.openclaw/workspace/SOUL.md`, but current audit did not confirm it as active rules master or canonical rules path.
- Current drift class here = docs / mental-model drift, not confirmed runtime failure.

### Что risky

- Main risk = docs / mental-model drift around rules paths.
- The most likely operator mistake is to confuse:
  - rules source path = `/data/.openclaw/workspace/memory/RULES.md`
  - storage path = `/data/.openclaw/memory`
- Additional risk:
  - `CLAUDE.md` or workspace `SOUL.md` may be misread as master rules source without live verification.
- Live repair is not required for the current contour.

### Что требует owner decision

- Only if intended rules layout is changed in the future.
- Possible future action:
  - compatibility/docs cleanup only
  - intended prompt layout simplification only by separate decision

### Что требует approve

- Any live changes to:
  - prompt / memory layout
  - loader/bootstrap paths
  - compatibility files around rules path
- In practice this includes:
  - `workspace/memory/RULES.md`
  - `.openclaw/memory`
  - `.openclaw/SOUL.md`
  - workspace `SOUL.md`
  - `CLAUDE.md` if it is used to change live prompt/rules behavior

### Вердикт

- `OK with WARN`
- rules SoT = `/data/.openclaw/workspace/memory/RULES.md`
- `/data/.openclaw/memory` = storage path, not rules path
- `/data/.openclaw/SOUL.md` absent
- `/data/CLAUDE.md` exists, but is not master rules source
- competing active rules master not confirmed
- current problem class = docs / mental-model drift around rules paths, not confirmed live issue
- live repair not required
