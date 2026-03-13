# MASTER HANDOFF — OPENCLAW / BORIS — 2026-03-13

> **Snapshot date**: 2026-03-13
> **For**: next AI agent or human engineer
> **Canon authority**: this is a snapshot for context transfer. If it conflicts with canon docs, canon docs win. See `docs/ai/WORKFLOW_CANON_AND_HANDOFF_POLICY.md`.

---

## Docs actually read

| # | File | Status |
|---|------|--------|
| 1 | `CLAUDE.md` | read |
| 2 | `AGENTS.md` | read |
| 3 | `docs/ai/OPERATING_CONSENSUS.md` | read |
| 4 | `docs/ai/PROJECT_MEMORY.md` | read |
| 5 | `docs/ai/SOURCE_OF_TRUTH.md` | read |
| 6 | `docs/ai/CHANGE_POLICY.md` | read |
| 7 | `docs/ai/DEFAULT_APPROVALS.md` | read |
| 8 | `docs/ai/VERIFICATION_MATRIX.md` | read |
| 9 | `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md` | read |
| 10 | `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md` | read |
| 11 | `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md` | read |
| 12 | `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md` | read |
| 13 | `docs/ai/HANDOFF_2026-03-10.md` | read (snapshot only) |
| 14 | `docs/ai/CODEX_PLAYBOOK.md` | read |
| 15 | `docs/ai/CHANGE_RUNBOOK.md` | read |
| 16 | `docs/ai/CHANGE_WINDOWS.md` | read |
| 17 | `docs/ai/BASELINE_2026-03-10.md` | read |
| 18 | `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md` | read |
| 19 | `docs/ai/FINAL_REMAINING_ACTIONS.md` | read |
| 20 | `docs/ai/SERVER_REMEDIATION_BACKLOG.md` | read |
| 21 | `docs/ai/BORIS_DETAIL_SCHEMA_CHECKLIST_v2.md` | read |
| 22 | `docs/ai/WORKFLOW_CANON_AND_HANDOFF_POLICY.md` | read (created this session) |

---

## Dated docs actually used

| Date | Doc type | Key docs |
|------|----------|----------|
| 2026-03-10 | Full audit | `SERVER_AUDIT_RESULT_2026-03-10_FULL.md` |
| 2026-03-10 | Addenda | `S1_S2_ALIAS`, `PROMPT_MEMORY`, `OKDESK_PIPELINE`, `MODEL_ROUTING`, `CRON_TIMERS` |
| 2026-03-10 | Snapshot | `HANDOFF_2026-03-10.md` |
| 2026-03-10 | Baseline | `BASELINE_2026-03-10.md` |
| 2026-03-11 | Addenda | `PG_TUNNEL`, `BRIDGE_HA`, `BLOCKS_5_6_7_8`, `BLOCK_10_MONITORING`, `BLOCK_11_CRON_SKILLS`, `BLOCK_12_TOOLS_PLUGINS`, `BORIS_CHAT_HARDENING`, `TG_RUNTIME_BLOCKER_CONTEXT`, `TENDER_SPECIALIST` |
| 2026-03-11 | Audits | `DOCTOR_AND_SELFHEAL_AUDIT` |
| 2026-03-12 | Addenda | `TG_HEALTH_PATH_CONTRADICTION`, `BORIS_EMPLOYEE_ARCHITECTURE`, `S1_GATEWAY_RESTART_AUTHORIZATION_PATH`, `XLSX_DETERMINISTIC_PROOF_PATH`, `XLSX_PERMISSION_AUTHENTIC_STEP1_PROOF_PATH` |
| 2026-03-13 | Addenda | `RAW_INBOUND_GUARD_PATCH_LOCATION_MISS`, `DUAL_INSTALL_CLI_PROOF_PATH`, `REAL_DM_RUNTIME_NPM_GLOBAL`, `CRON_MASTER_FIELD_OWNERSHIP_DECISION_PREP`, `XLSX_PROOF_CHAIN_COMPLETE` |
| 2026-03-13 | Changelogs | `gdrive_index_recovery`, `search_closeout`, `gog_closeout`, `raw_inbound_guard_patch_location_correction`, `npm_global_raw_inbound_guard_correction`, `b2_workspaceonly_apply`, `cron_master_slice1`, `cron_master_cleanup_waveA`, `cron_master_cleanup_waveB`, `cron_master_def_slice_enabled_schedule`, `cron_master_def_slice2_delivery_sessionTarget_wakeMode`, `cron_master_def_slice3_message`, `rules_soul_hash_integrity`, `exec_deny_alias_fix_and_parse_file_patch` |

---

## Project canon

**Entry points**: `CLAUDE.md`, `AGENTS.md` — both point to the same canon.

**Canonical read order**: defined in `docs/ai/OPERATING_CONSENSUS.md`.

**Priority**: canon > dated audit docs > changelogs > operational docs > handoffs > snapshots. See `docs/ai/WORKFLOW_CANON_AND_HANDOFF_POLICY.md`.

---

## Prompt map by task type

Canonical prompt map lives in `docs/ai/WORKFLOW_CANON_AND_HANDOFF_POLICY.md`.

| Code | Task type | Description |
|------|-----------|-------------|
| **R** | Read-only inspection | Allowed by default. No approve needed. No changes. |
| **A** | Analyze | Classify contour: skill / cron / heartbeat / workflow / script / config. |
| **B** | Audit block | Read-only server check of one block/contour. Pre-check only, no changes. |
| **B-1** | Narrow sub-audit | Scoped read-only sub-check within an already open audit. |
| **C** | Docs-only update | Only repo docs. Allowed any time. Must not change runtime. |
| **D** | Apply plan | Prepare safe live plan without changes. Identify SoT, master, writers, blast radius. |
| **E** | Apply | Only after approve and only in agreed scope. `pre-check → backup → minimal apply → post-check → rollback on fail`. |
| **F** | Changelog | After apply: record result, update backlog/final actions. |
| **G** | Owner decision request | Present options with risk/pros/cons. Do not assume answer. |
| **H** | Smoke proof | One narrow canary to prove a specific runtime path. Not a broad test. |
| **I** | Source-of-truth audit | Determine master/runtime/writers for one contour. |
| **J** | Weekly audit | Top-down: blocks 1→13 per `BORIS_DETAIL_SCHEMA_CHECKLIST_v2.md`. |
| **K** | Architecture wave | Approve-only multi-step hardening (e.g., employee architecture). |
| **L** | Migration wave | Approve-only phased migration (e.g., cron/master SoT). |

---

## Closed contours

Do not reopen without new explicit evidence.

| Contour | Closed by | Status |
|---------|-----------|--------|
| S1→S2 alias `s2` | `SERVER_CHANGELOG_2026-03-10_ALIAS_S2.md` | [LIVE] CLOSED |
| S1 stale timers | `SERVER_CHANGELOG_2026-03-10_DISABLE_STALE_TIMERS.md` | [LIVE] CLOSED |
| Cron delivery normalization | `SERVER_CHANGELOG_2026-03-11_CRON_DELIVERY_PHASE_B.md` | [LIVE] CLOSED |
| S1 stale webhook routes | `SERVER_CHANGELOG_2026-03-11_block9_webhook_routes_fix.md` | [LIVE] CLOSED |
| Bridge 2 subscription 404 | `SERVER_CHANGELOG_2026-03-11_bridge2_subscription_fix.md` | [LIVE] CLOSED |
| Digest fallback chains (morning/evening) | `SERVER_CHANGELOG_2026-03-11_digest_fallback_chain_morning_evening.md` | [LIVE] CLOSED |
| Telegram helper token hardening | `SERVER_CHANGELOG_2026-03-11_tg_helper_token_hardening.md` | [LIVE] CLOSED |
| HQ requireMention convergence | `SERVER_CHANGELOG_2026-03-11_HQ_REQUIRE_MENTION_REAPPLY.md` | [LIVE] CLOSED |
| Wave 0 chat-admin hard stop | `SERVER_CHANGELOG_2026-03-11_boris_wave0_chat_hardstop.md` | [LIVE] CLOSED |
| `/route` closure + group self-mod deny | `SERVER_CHANGELOG_2026-03-12_boris_group_selfmod_deny_and_route_closure.md` | [LIVE] CLOSED |
| Cron split off `main` | `SERVER_CHANGELOG_2026-03-12_cron_split_off_main.md` | [LIVE] CLOSED |
| `main` per-agent hardening | `SERVER_CHANGELOG_2026-03-12_main_per_agent_hardening_wave.md` | [LIVE] CLOSED |
| Inbound staging wave (B1) | `SERVER_CHANGELOG_2026-03-12_boris_inbound_staging_wave.md` | [LIVE] CLOSED |
| Raw inbound guard — `/usr/local` family | `SERVER_CHANGELOG_2026-03-13_raw_inbound_guard_patch_location_correction.md` | [LIVE] CLOSED |
| Raw inbound guard — `.npm-global` family | `SERVER_CHANGELOG_2026-03-13_npm_global_raw_inbound_guard_correction.md` | [LIVE] CLOSED |
| Telegram restore contour | `SERVER_AUDIT_ADDENDUM_2026-03-12_TG_HEALTH_PATH_CONTRADICTION.md` | [DOCS] CLOSED |
| `gdrive-index` recovery | `SERVER_CHANGELOG_2026-03-13_gdrive_index_recovery.md` | [LIVE] CLOSED |
| `search` contour | `SERVER_CHANGELOG_2026-03-13_search_closeout.md` | [LIVE] CLOSED |
| `gog` contour | `SERVER_CHANGELOG_2026-03-13_gog_closeout.md` | [LIVE] CLOSED |
| XLSX Step 1 (ingress/staging proof) | `SERVER_AUDIT_ADDENDUM_2026-03-13_XLSX_PROOF_CHAIN_COMPLETE.md` | [LIVE] CLOSED |
| XLSX Step 2 (workbook semantic proof) | `SERVER_AUDIT_ADDENDUM_2026-03-13_XLSX_PROOF_CHAIN_COMPLETE.md` | [LIVE] CLOSED |
| B2 workspaceOnly apply | `SERVER_CHANGELOG_2026-03-13_b2_workspaceonly_apply.md` | [LIVE] CLOSED |
| RULES.md + SOUL.md content-hash integrity (Option A) | `SERVER_CHANGELOG_2026-03-13_rules_soul_hash_integrity.md` | [LIVE] CLOSED |
| Canon/docs alignment | `FINAL_REMAINING_ACTIONS.md` §2 | [DOCS] CLOSED |
| Observer doctor-agent MVP | `OBSERVER_DOCTOR_MVP.md` | [DOCS] CLOSED |
| exec denied via bash→exec alias in per-group tools.deny | `SERVER_CHANGELOG_2026-03-13_exec_deny_alias_fix_and_parse_file_patch.md` | [LIVE] CLOSED |
| parse-file exec-first / staging-first instruction gap | `SERVER_CHANGELOG_2026-03-13_exec_deny_alias_fix_and_parse_file_patch.md` | [LIVE] CLOSED |

---

## Active/open contours

| # | Contour | Classification | Current stage | Next expected prompt type |
|---|---------|---------------|---------------|--------------------------|
| 1 | **Boris employee architecture — owner policy / business memory separation** | approve-only architecture | not started; prerequisites B2 + Option A (hash integrity) now completed | **D** (apply plan) |
| 2 | **Cron/master SoT migration program** | approved migration track | Phase 1 Slice 1 + cleanup Wave A + Wave B + definition-field snapshot slices 1+2+3 verified + `notify` skipped as vestigial; route/model subset enforced; all meaningful definition fields snapshot-only in `cron-master.json` (`enabled`, `schedule`, `delivery`, `sessionTarget`, `wakeMode`, `message`); no enforcement for snapshot-only fields; contour open | **G** (post-definition-field stage decision) |
| 3 | **Tender specialist skill hygiene** | low-risk server-side patch | not applied yet | **E** (apply) in low-risk window |
| 4 | **Timur Morning/Evening dedicated-agent auth-profile materialization / EACCES** | apply plan hardening / normalization | apply plan drafted, not yet approve-ready; see `docs/ai/HANDOFF_WAVE_2026-03-13_timur_auth_profile_eacces.md` | **D** (apply plan normalization), not yet **G** |
| 5 | **pg-tunnel-s2 contingency contour** | optional housekeeping | owner decision pending | **G** (owner decision) |

---

## Source-of-truth map

| What | Master | Effective runtime | Confidence |
|------|--------|-------------------|------------|
| Internal default model chain | [LIVE] `model-strategy.json` | [LIVE] internal `openclaw.json` | high |
| Internal cron models | [LIVE] `cron-master.json` (declarative; migrated from `model-strategy.json` via Slice 1 + Wave B) | [LIVE] `jobs.json.payload.model` | high |
| External Boris chain | [LIVE] external `fix-model-strategy.py` | [LIVE] external `openclaw.json` | high |
| Cron job route/model fields | [LIVE] `cron-master.json.cron_job_routes` (legacy fields removed from `model-strategy.json` in Wave B) | [LIVE] `jobs.json` via `fix-model-strategy.py` | high |
| Cron job definition fields (`enabled`, `schedule`, `delivery`, `sessionTarget`, `wakeMode`, `message`) | [LIVE] `cron-master.json` snapshot/reference (not enforced); Gateway remains sole writer in `jobs.json`; `notify` skipped as vestigial | [LIVE] `jobs.json` | medium |
| Cron job state/meta fields | [LIVE] Gateway scheduler runtime | [LIVE] `jobs.json` | high |
| Prompt/rules on S1 | [LIVE] `/data/.openclaw/workspace/memory/RULES.md` | same | high |
| Telegram group config | [LIVE] internal `openclaw.json` | same | high |
| Boris chat-admin controls | [LIVE] internal `openclaw.json` | same | high |
| okdesk-pipeline placement | [LIVE] S2 unit + S2 cron + S2 :3200 | same | high |
| Workflow states | [LIVE] n8n DB `workflow_entity` by exact ID | same | high |
| Boris PG on S1 | [LIVE] local mode, `boris-emails-pg-1` | same | high |
| Public bridge-ha probe | [LIVE] `https://n8n.brendservice24.ru/bridge-ha/health` | same | high |

---

## Writers/enforcers map

See `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md` for full matrix. Key entries:

| Target | Key writers | Trigger |
|--------|------------|---------|
| internal `openclaw.json` | `startup-cleanup.sh`, `fix-model-strategy.py`, `circuit-breaker-internal.py`, `workspace-validator.py` | startup, cron, boris-doctor |
| internal `jobs.json` model fields | `fix-model-strategy.py` (reads from `cron-master.json` first, fallback `model-strategy.json`) | startup post-K |
| external `openclaw.json` | `startup-external.sh`, external `fix-model-strategy.py` | startup, cron `* * * * *` |
| `RULES.md`, `SOUL.md`, skills | `workspace-validator.py` (hash-based integrity) | boris-doctor 6h |
| tracked configs | `service-guard.py` | self-heal loop |
| `monitor.sh` | `watchdog-meta.sh` | cron `*/5` |
| S1 data copies | `sync-executors-from-s2.sh`, `sync-pg-from-s2.sh` | cron |
| `patch-reasoning-fix.sh` targets | `startup-cleanup.sh` invokes patcher | container start |

---

## Trigger/materializer map

| Materializer | What it produces | Trigger |
|-------------|-----------------|---------|
| internal `fix-model-strategy.py` | `openclaw.json`, `models.json`, `jobs.json` model/agent fields (source: `cron-master.json` first, fallback `model-strategy.json`) | startup + manual |
| external `fix-model-strategy.py` | external `openclaw.json`, `models.json` | cron `* * * * *` |
| `workspace-validator.py` | restored skills/rules/SOUL.md from backup (hash-based integrity for RULES.md + SOUL.md) | boris-doctor 6h |
| `service-guard.py` | baseline acceptance or rollback | continuous |
| `patch-reasoning-fix.sh` | RAW_INBOUND_GUARD in `/usr/local` + `.npm-global` families | startup |

---

## Permanent guardrails

1. Canon before snapshot. Conflicts → `SERVER_AUDIT_REQUIRED`.
2. SoT before runtime. Never patch derived file if writer will overwrite.
3. Minimal change set. One wave = one contour = one scope.
4. Always rollback-ready.
5. No secrets in output.
6. Approve-only zones: auth, routing, gateway, bridge, monitoring/self-healing, workflows, model files, `jobs.json`, pipeline placement, prompt/memory layout, restart, destructive actions, secrets management.
7. No new ad-hoc cron writers until cron/master SoT migration completes.
8. No blanket-deny of Boris employee capabilities.
9. Direct CLI `openclaw agent` canary is not valid Boris DM/gateway proof for XLSX Step 1.
10. `jobs.json` is not whole-file canonical master.
11. Target C (cron SoT) is not yet live.
12. Do not expand auto-repair without owner decision.
13. `bash` must NOT be added to per-group `tools.deny`: OpenClaw `TOOL_NAME_ALIASES` maps `bash` → `exec`, so denying `bash` also denies `exec`. Standard `bash` tool is already stripped from codingTools in runtime.

---

## What must not be reopened without new evidence

- gdrive-index, search, gog — CLOSED 2026-03-13
- Telegram restore — CLOSED 2026-03-12
- HQ requireMention — CLOSED 2026-03-12
- Wave 0 chat hard stop — CLOSED 2026-03-11
- `/route` closure — CLOSED 2026-03-12
- All raw-inbound guard corrections (both families) — CLOSED 2026-03-13
- XLSX Step 1 + Step 2 proof chain — CLOSED 2026-03-13
- B2 workspaceOnly apply — CLOSED 2026-03-13
- RULES.md + SOUL.md content-hash integrity (Option A) — CLOSED 2026-03-13
- exec denied via bash→exec alias + parse-file exec-first/staging-first gap — CLOSED 2026-03-13
- Gateway/health-check docs drift — CLOSED
- Bridge-ha canonical probe — CLOSED

---

## Current project-level risks

| Risk | Class | Source |
|------|-------|--------|
| Model routing layered split | [LIVE] operational risk | accepted architecture |
| Internal cron periodic enforcer weaker than external | [LIVE] operational risk | KNOWN_BUGS |
| `pg-tunnel-s2.service` legacy noise | [LIVE] operational noise | needs owner decision |
| Dual-install drift (`/usr/local` vs `.npm-global`) | [LIVE] both patched, but dual families remain | runtime complexity |
| `workspace-validator` 6h auto-restore | [LIVE] can revert intentional changes; now uses SHA-256 hash (not just size) for RULES.md + SOUL.md | writer/enforcer risk (reduced) |
| Multi-writer cron architecture (B-now) | [LIVE] route/model subset enforced via `cron-master.json`; all meaningful definition fields (`enabled`/`schedule`/`delivery`/`sessionTarget`/`wakeMode`/`message`) snapshot-only in `cron-master.json`; `notify` skipped as vestigial; no enforcement for snapshot-only fields | migration in progress, route/model + def snapshot slices 1+2+3 completed |
| `group:fs` restricted by `workspaceOnly=true` on `main` | [LIVE] file-based self-mod risk reduced to workspace scope | B2 applied 2026-03-13 |
| Shared trust boundary | [DOCS] target accepted, not applied | architecture program |
| S2 disk usage trend | [LIVE] 71% at audit date | watch item |
| Bridge instability under load | [LIVE] ~10% fetch-failed | graceful degradation |

---

## Current active contour snapshot

### 1. Boris employee architecture — owner policy / business memory separation

- **Proven** [LIVE]: B2 applied (`workspaceOnly=true`); Step 1 + Step 2 PASS; all prior waves completed (Wave 0, `/route` closure, cron split, per-agent hardening, B1 staging, raw-inbound guard both families); RULES.md + SOUL.md content-hash integrity (Option A) applied — both files now have SHA-256 hash protection + auto-restore via workspace-validator every 6h
- **Not proven**: owner-policy / business-memory separation not started
- **Next step**: apply plan for owner-policy layer separation

### 2. Cron/master SoT migration

- **Proven** [LIVE]: Slice 1 applied (`cron-master.json` created, `fix-model-strategy.py` patched); cleanup Wave A applied (readers migrated to `cron-master.json`-first); cleanup Wave B applied (4 legacy cron fields removed from `model-strategy.json`); definition-field snapshot slice 1 applied (`enabled` + `schedule`); definition-field snapshot slice 2 applied (`delivery` + `sessionTarget` + `wakeMode`); definition-field snapshot slice 3 applied (`message`). All six verified and documented. All meaningful definition fields now have snapshot-only coverage in `cron-master.json`.
- **Proven** [DOCS]: owner approved target C + B-now interim + Phase 1 design + all three definition-field snapshot-only slices + notify skip
- **Not proven**: `notify` skipped as vestigial (3/13 partial, all `false`, zero readers/writers); enforcement for any snapshot-only fields; state/meta formalization; full target C
- **Source docs**: `SERVER_CHANGELOG_2026-03-13_cron_master_slice1.md`, `SERVER_CHANGELOG_2026-03-13_cron_master_cleanup_waveA.md`, `SERVER_CHANGELOG_2026-03-13_cron_master_cleanup_waveB.md`, `SERVER_CHANGELOG_2026-03-13_cron_master_def_slice_enabled_schedule.md`, `SERVER_CHANGELOG_2026-03-13_cron_master_def_slice2_delivery_sessionTarget_wakeMode.md`, `SERVER_CHANGELOG_2026-03-13_cron_master_def_slice3_message.md`, `SERVER_AUDIT_ADDENDUM_2026-03-13_CRON_MASTER_FIELD_OWNERSHIP_DECISION_PREP.md`
- **Next step**: owner/design decision about post-definition-field stage: `_comment_cron_job_routes` cosmetic cleanup, state/meta formalization, or enforcement design (all separate tasks, separate approve)

### 3. Tender specialist skill hygiene

- **Proven** [LIVE]: contour = skill + script; three `SKILL.md` issues identified
- **Not proven**: patch not applied
- **Next step**: low-risk apply in change window

### 4. Timur Morning/Evening dedicated-agent auth-profile materialization / EACCES

- **Status**: apply plan hardening / normalization
- **Detail**: see `docs/ai/HANDOFF_WAVE_2026-03-13_timur_auth_profile_eacces.md`
- **What is proven from prior work** [LIVE]: dedicated cron agents `cron-timur-morning-digest` and `cron-timur-evening-digest` already materialized and running on S1; `model-strategy.json` contains exact `cron_job_routes` for both; structural apply confirmed successful
- **What is indicated by owner** [DOCS]: active dist path pinned; `saveJsonFile` convergence point pinned; restart requirement pinned; apply plan drafted but not yet approve-ready
- **What remains unknown**: no dated audit doc in repo for the auth-profile / EACCES specific issue; exact approve boundary, restart semantics, and patcher scope still need normalization
- **Next step**: final apply plan normalization (**D**), not apply yet; not yet **G**-ready

---

## Current apply-readiness snapshot

| Contour | Apply ready? | Why |
|---------|-------------|-----|
| XLSX Step 1 canary | **PASS** | completed 2026-03-13 |
| XLSX Step 2 | **PASS** | completed 2026-03-13 |
| B2 (workspaceOnly) | **APPLIED** | completed 2026-03-13; see `SERVER_CHANGELOG_2026-03-13_b2_workspaceonly_apply.md` |
| Cron/master migration Phase 1 route/model slice | **APPLIED** | Slice 1 + Wave A + Wave B verified 2026-03-13 |
| Cron/master definition-field snapshot slice 1 (enabled + schedule) | **APPLIED** | snapshot-only, no enforcement |
| Cron/master definition-field snapshot slice 2 (delivery + sessionTarget + wakeMode) | **APPLIED** | snapshot-only, no enforcement |
| Cron/master definition-field snapshot slice 3 (message) | **APPLIED** | snapshot-only, no enforcement; `notify` skipped as vestigial; all meaningful def-field snapshot coverage complete |
| Tender specialist patch | **ready** | needs only low-risk change window + backup |
| Auth-profile / EACCES | **not ready** | plan still needs normalization of approve boundary / restart semantics / patcher scope |
| RULES.md + SOUL.md hash integrity (Option A) | **APPLIED** | completed 2026-03-13; see `SERVER_CHANGELOG_2026-03-13_rules_soul_hash_integrity.md` |
| Owner policy layer | **not ready** | not started; prerequisites B2 + Option A now completed |
| Business memory separation | **not ready** | not started; prerequisite: owner policy |

---

## One-line master summary

Boris/OpenClaw as of 2026-03-13: infrastructure stable with WARN; 20+ hardening waves completed; XLSX proof chain complete + B2 `workspaceOnly=true` applied + RULES.md/SOUL.md content-hash integrity (Option A) applied + exec-denied-via-bash-alias fixed + parse-file exec-first/staging-first patched (both canary-verified end-to-end); cron/master SoT migration route/model slice completed (Slice 1 + Wave A + Wave B verified, `cron-master.json` live, legacy fields removed from `model-strategy.json`) + definition-field snapshot slices 1+2+3 completed (all meaningful definition fields snapshot-only in `cron-master.json`, no enforcement) + `notify` skipped as vestigial; next milestones = owner-policy/business-memory separation, post-definition-field stage decision (cosmetic cleanup / state-meta / enforcement), tender specialist skill hygiene, and auth-profile/EACCES apply plan normalization; shared trust boundary remains the open architecture target.
