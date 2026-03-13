# SERVER_CHANGELOG_2026-03-13_exec_deny_alias_fix_and_parse_file_patch

## Purpose

- [LIVE] Fix `exec` tool blocked in all 6 Telegram groups due to `bash` to `exec` alias in OpenClaw tool policy.
- [LIVE] Add exec-first and staging-first instructions to `parse-file/SKILL.md`.
- [LIVE] Two contours closed in one wave, both canary-verified end-to-end.

## Root cause

- [LIVE] OpenClaw `TOOL_NAME_ALIASES` in `pi-embedded-helpers-BrFJjKm3.js` maps `bash` to `exec`.
- [LIVE] `normalizeToolName("bash")` returns `"exec"`.
- [LIVE] `makeToolPolicyMatcher` normalizes deny entries before matching.
- [LIVE] Per-group `tools.deny` included `"bash"`, which after normalization blocked `"exec"`.
- [LIVE] Standard `bash` tool is already stripped from codingTools in OpenClaw runtime (replaced by custom `exec`), so `"bash"` in deny was both redundant and harmful.
- [LIVE] The deny fix that originally added `bash` to prevent raw bash tool usage unintentionally killed the custom OpenClaw `exec` tool via this alias.
- [LIVE] `process` tool remained available but useless without `exec` (can only manage existing exec sessions, not start new ones).
- [LIVE] Separately, `parse-file/SKILL.md` lacked explicit exec-first and staging-first instructions, causing model to not call `exec` even when available.

## What changed on S1

### Patched file 1: `openclaw.json` (per-group tools.deny)

- [LIVE] Removed `bash` from `channels.telegram.groups.*.tools.deny` in all 6 groups.
- [LIVE] Pre-apply hash: `b88ecbd8ce19232c3f9cda3f4b63a5cb`.
- [LIVE] Post-apply hash: `602d2356c287cc34a2f9cdc14ca14c77`.
- [LIVE] Before (all 6 groups): `["group:automation", "group:nodes", "sessions_spawn", "sessions_send", "bash", "gateway", "cron"]`
- [LIVE] After (all 6 groups): `["group:automation", "group:nodes", "sessions_spawn", "sessions_send", "gateway", "cron"]`
- [LIVE] All other deny entries preserved.
- [LIVE] Agent main tools unchanged.
- [LIVE] Top-level tools.exec unchanged.
- [LIVE] No restart performed (config hot-reload on next API call).

### Patched file 2: `parse-file/SKILL.md`

- [LIVE] Path: `/data/.openclaw/workspace/skills/parse-file/SKILL.md`.
- [LIVE] Added "Important: How to Execute Commands" section (exec-first instruction).
- [LIVE] Added "Important: Staging Inbound Files" section (staging-first instruction with `stage-inbound-media.py` path and workspace constraint).
- [LIVE] Added "Local file (after staging)" input mode to Input Modes section.
- [LIVE] Added "Remember: run this curl command using the `exec` tool" reminder at Endpoint section.
- [LIVE] Pre-apply hash: `f966c93f4079199729d66889f806132c`.
- [LIVE] Post-apply hash: `49fa7d04c4697cbff414329d40ae7792`.

## What was NOT changed

- [LIVE] No restart performed.
- [LIVE] No system prompt changes.
- [LIVE] No model or routing changes.
- [LIVE] No changes to `tender-specialist/SKILL.md` or other skills.
- [LIVE] No changes to `stage-inbound-media.py`.
- [LIVE] No changes to `RULES.md`.
- [LIVE] No changes to agent-level or top-level tool config.

## Verification

### Pre-fix evidence (session `5c72e46f`, 2026-03-13T11:06:42Z)

- [LIVE] TENDER group, fresh session after deny fix but before bash-alias correction.
- [LIVE] Boris called `process` 15 times, `exec` zero times.
- [LIVE] All `process` results: "No active session" / "No running or recent sessions".
- [LIVE] Boris reported: "Exec полностью недоступен. Тимур, у нас технический сбой."
- [LIVE] This was an accurate report, not hallucination: `exec` was genuinely absent from available tools.

### Historical working evidence (session `291247a9`, 2026-03-09T05:58:03Z)

- [LIVE] TENDER group, before the deny fix added `bash` to deny lists.
- [LIVE] 86 successful `exec` calls. Confirms `exec` worked before `bash` was added to deny.

### Post-fix canary (session `a9339b83`, 2026-03-13T12:18:30Z)

- [LIVE] TENDER group, fresh session after both fixes applied.
- [LIVE] Boris read patched `parse-file/SKILL.md` (L8).
- [LIVE] Boris called `exec` with `stage-inbound-media.py` as first action (L10) — staging-first confirmed.
- [LIVE] Staging succeeded: `/data/.openclaw/workspace/downloads/inbound/file_819...xlsx` (L11).
- [LIVE] Boris called `exec` with curl to parse-file webhook using staged path (L12).
- [LIVE] Webhook returned `{"error":"not found"}` (L13) — see "Known pre-existing concern" below.
- [LIVE] Boris fell back to `exec` with `python3 -c` + `openpyxl` on staged path (L14).
- [LIVE] XLSX parsed successfully: sheet "Расценки", 397 rows, full content extracted (L15-L19).
- [LIVE] Boris delivered complete tender analysis to user (L20).
- [LIVE] Total: 5 `exec` calls, zero `process` calls — complete reversal of pre-fix behavior.

## Known pre-existing concern

- [LIVE] parse-file webhook (`http://172.18.0.1:8443/webhook/parse-file`) returned `{"error":"not found"}` during canary (L13).
- [DOCS] This is a separate pre-existing concern, not part of this closed contour.
- [DOCS] Boris correctly fell back to direct exec+openpyxl parsing on the staged path.
- [DOCS] No new contour opened for this. Documenting for future reference only.

## Backup

- [LIVE] `openclaw.json`: `/tmp/backup-openclaw-json-20260313-bash-deny.json` (hash `b88ecbd8ce19232c3f9cda3f4b63a5cb`).
- [LIVE] `parse-file/SKILL.md`: `/tmp/backup-parse-file-20260313/SKILL.md` (hash `f966c93f4079199729d66889f806132c`).

## Rollback

```bash
# openclaw.json
docker cp /tmp/backup-openclaw-json-20260313-bash-deny.json openclaw-kbxr-openclaw-1:/data/.openclaw/openclaw.json

# parse-file SKILL.md
docker cp /tmp/backup-parse-file-20260313/SKILL.md openclaw-kbxr-openclaw-1:/data/.openclaw/workspace/skills/parse-file/SKILL.md
```

## Contour Status

- [CLOSED] exec denied via bash alias in per-group tools.deny — fixed and canary-verified.
- [CLOSED] parse-file exec-first / staging-first instruction gap — patched and canary-verified.
- [NOTED] parse-file webhook 404 — separate pre-existing concern, not part of this closure.
