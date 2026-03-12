# SERVER CHANGELOG 2026-03-12: BORIS INBOUND STAGING WAVE

## Scope
- Live apply on `S1`
- Created staging dir:
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/downloads/inbound/`
- Added helper:
  - `/var/lib/apps-data/openclaw/data/scripts/stage-inbound-media.py`
- Added one minimal instruction layer:
  - `/var/lib/apps-data/openclaw/data/CLAUDE.md`
  - only inside `File Extractor` block

## What was wrong
- Live business flows still used raw `.openclaw/media/inbound/*`.
- Because of that, the next planned hardening step:
  - `agents.list[id=main].tools.fs.workspaceOnly = true`
  was still blocked.

## What changed
- Created approved staging dir under workspace:
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/downloads/inbound/`
- Added `stage-inbound-media.py` with the agreed constraints:
  - accepts only source paths under `/var/lib/apps-data/openclaw/data/.openclaw/media/inbound/`
  - copies only into `/var/lib/apps-data/openclaw/data/.openclaw/workspace/downloads/inbound/`
  - rejects path traversal
  - rejects symlinks
  - rejects non-inbound sources
  - prints only the staged workspace path
- Added one minimal instruction rule in `CLAUDE.md` so Boris stages inbound attachments before file-tool access.

## Backup
- Backup dir:
  - `/root/boris-inbound-staging-20260312T124503Z`
- Backup files:
  - `/root/boris-inbound-staging-20260312T124503Z/CLAUDE.md.bak`
  - `/root/boris-inbound-staging-20260312T124503Z/pre-downloads-tree.txt`
  - `/root/boris-inbound-staging-20260312T124503Z/pre-sha256.txt`
  - `/root/boris-inbound-staging-20260312T124503Z/pre-memory-fingerprint.txt`
  - `/root/boris-inbound-staging-20260312T124503Z/pre-service-state.txt`

## Pre-check
- blocker still existed
- no safe workspace mirror already existed
- downloads path existed
- no enforcer owned helper path or staging dir
- scope stayed outside:
  - owner policy
  - business memory
  - bridge-model routing
  - digests
  - callback-forward
  - monitoring

## Post-check
- staging dir created correctly
- helper exists and `py_compile` passed
- helper rejects:
  - non-inbound paths
  - path traversal
  - symlinks
- helper returns only staged workspace path
- staged files land only under:
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/downloads/inbound/`
- minimal instruction layer changed only `File Extractor` block in `CLAUDE.md`
- no drift in:
  - routing
  - owner policy
  - business memory
  - digests
  - callback-forward
  - monitoring

## Rollback required or not
- Rollback was not required.

## Important next step
- Collect live evidence that Boris now stages inbound attachments before file-tool access.
- Only after that prepare `B2`:
  - `agents.list[id=main].tools.fs.workspaceOnly = true`

## Result
- `successful`
