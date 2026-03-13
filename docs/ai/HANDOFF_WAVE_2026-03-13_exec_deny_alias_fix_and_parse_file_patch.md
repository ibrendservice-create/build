# HANDOFF WAVE 2026-03-13 — exec deny alias fix + parse-file exec-first/staging-first patch

> **Snapshot date**: 2026-03-13
> **Canon authority**: this is a wave-level snapshot. If it conflicts with canon docs, canon docs win. See `docs/ai/WORKFLOW_CANON_AND_HANDOFF_POLICY.md`.

---

## Contours closed

1. **exec denied via bash→exec alias in per-group tools.deny** — CLOSED
2. **parse-file exec-first / staging-first instruction gap** — CLOSED

## What was applied

- Removed `bash` from `channels.telegram.groups.*.tools.deny` in all 6 groups in `openclaw.json`.
- Added exec-first, staging-first, and workspace-constraint instructions to `parse-file/SKILL.md`.
- No restart. No system prompt changes. No model/routing changes.

## Root cause

OpenClaw `TOOL_NAME_ALIASES` in `pi-embedded-helpers-BrFJjKm3.js` maps `bash` to `exec`. The deny fix that added `bash` to per-group deny lists unintentionally blocked the custom `exec` tool via this alias. Standard `bash` is already stripped from codingTools in runtime, so `bash` in deny was redundant and harmful.

Separately, `parse-file/SKILL.md` lacked explicit exec-first and staging-first instructions, causing the model to not call `exec` even when available.

## Canary result (session `a9339b83`, 2026-03-13T12:18:30Z)

- TENDER group, fresh session after both fixes.
- exec called: YES (5 calls, zero process calls).
- stage-inbound-media.py called: YES (first exec call).
- Staged path used for all operations: YES.
- XLSX parsed successfully: YES (sheet "Расценки", 397 rows).
- Result delivered to user: YES.
- Rollback needed: NO.

## Known pre-existing concern (not part of this closure)

- parse-file webhook (`http://172.18.0.1:8443/webhook/parse-file`) returned `{"error":"not found"}` during canary.
- Boris correctly fell back to direct exec+openpyxl on staged path.
- No new contour opened. Documented for future reference only.

## Guardrail added

`bash` must NOT be added to per-group `tools.deny`. The alias `bash` → `exec` means denying `bash` also denies `exec`.

## Source doc references

- Changelog: `docs/ai/SERVER_CHANGELOG_2026-03-13_exec_deny_alias_fix_and_parse_file_patch.md`
- Master handoff: `docs/ai/HANDOFF_MASTER_OPENCLAW_2026-03-13.md`
