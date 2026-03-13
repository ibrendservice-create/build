# HANDOFF WAVE 2026-03-13 — Timur Morning/Evening dedicated-agent auth-profile materialization / EACCES

> **Snapshot date**: 2026-03-13
> **Canon authority**: this is a wave-level snapshot. If it conflicts with canon docs, canon docs win. See `docs/ai/WORKFLOW_CANON_AND_HANDOFF_POLICY.md`.

---

## Contour name

Timur Morning/Evening dedicated-agent auth-profile materialization / EACCES

## Classification

CLOSED by owner decision (Option A: applied-live evidence + code inspection).

---

## Contour closed

1. **auth-profile EACCES guard** — CLOSED

## What was applied

- Patcher script `/data/patch-auth-profiles-fix.sh` created (idempotent, marker-based).
- Startup hook added to `/startup-cleanup.sh` lines 70-76 (calls patcher on each container start after K()).
- Both dist families patched (3 `saveJsonFile` calls each wrapped with `__safeSaveAuthStore` EACCES guard):
  - `.npm-global`: `auth-profiles-GYsKiVaE.js`
  - `/usr/local`: `auth-profiles-DSWJsDjg.js`
- Container restarted; patcher confirmed executed in watchdog log.
- Backups exist for all patched files.

## Closure evidence

- [LIVE] Patcher script present at `/data/patch-auth-profiles-fix.sh`.
- [LIVE] Startup hook present in `/startup-cleanup.sh` lines 70-76.
- [LIVE] Patcher ran at latest container start (`11:57:51`): watchdog log confirms `[auth-profiles-fix] Applied 2 patch(es), 0 already OK`.
- [LIVE] `.npm-global` family patched: 4 `__safeSaveAuthStore` references in `auth-profiles-GYsKiVaE.js`.
- [LIVE] `/usr/local` family patched: 4 `__safeSaveAuthStore` references in `auth-profiles-DSWJsDjg.js`.
- [LIVE] Backup files exist for both dist targets.
- [LIVE] Zero EACCES crashes in container logs since patch.
- [LIVE] Patch survives container restarts via startup hook (confirmed across two restarts: `10:00:28` without hook, `11:57:51` with hook — hook correctly added between these).
- [DOCS] Guard wrapper semantics: catches only EACCES, re-throws everything else, logs warning, calling code continues normally.
- [DOCS] All immediate post-checks passed (8/8) per changelog.

## Deferred proof status

- Natural trigger path (Timur/Email digest cron run) did not occur: all relevant cron jobs have `lastRunAtMs=null`, `nextRunAtMs=null`.
- Deferred proof waived by owner decision (Option A).
- Cron scheduler issue (`nextRunAtMs=null` for all digest jobs) is a separate pre-existing concern, not part of this contour.

## Owner decision

Option A accepted: closure by applied-live evidence + code inspection. Do not wait for natural trigger event.

## Guardrail

`auth-profiles.json` ownership must be `node:node` (UID 1000). If doctor/watchdog/docker-exec writes create root-owned copies, the guard catches EACCES gracefully. But the root cause (root ownership) should still be fixed at the writer layer when possible.

---

## Source doc references

- Changelog: `docs/ai/SERVER_CHANGELOG_2026-03-13_timur_auth_profile_eacces_guard.md`
- Master handoff: `docs/ai/HANDOFF_MASTER_OPENCLAW_2026-03-13.md`
- Dedicated agent materialization: `docs/ai/SERVER_CHANGELOG_2026-03-11_digest_fallback_chain_morning_evening.md`
- Gateway restart authorization: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_S1_GATEWAY_RESTART_AUTHORIZATION_PATH.md`
