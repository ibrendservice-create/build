# SERVER AUDIT ADDENDUM 2026-03-11 BLOCK 11 CRON SKILLS

Docs-only фиксация результата narrow read-only audit по:
- Block 11. `Cron, jobs, timers, skills`

Изменения в live не выполнялись.
Это не apply changelog и не live fix.

## Block 11. Cron, jobs, timers, skills, tooling contour

Статус:
- `OK with WARN`
- confirmed live outage not found
- mainly docs / mental-model drift
- `jobs.json` is not runtime truth by itself

### Что проверено

- Repo canon и dated audit docs:
  - `docs/ai/BORIS_DETAIL_SCHEMA_CHECKLIST_v2.md`
  - `docs/ai/BASELINE_2026-03-10.md`
  - `docs/ai/OPERATING_CONSENSUS.md`
  - `docs/ai/SOURCE_OF_TRUTH.md`
  - `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md`
  - `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`
  - `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`
- Read-only live checks on `S1`:
  - `/var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json`
  - `crontab -l`
  - exact timer states for:
    - `boris-email-router.timer`
    - `chief-doctor.timer`
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/skills`
  - `/var/lib/apps-data/openclaw/data/scripts`
  - sampled main-agent session traces for `toolCall.name`
  - plugin manifests under `/var/lib/apps-data/openclaw/data/**/openclaw.plugin.json`

### Что ок

- Internal cron model layer matches canon.
- `enabled_jobs=13`
- `total_jobs=13`
- all enabled jobs use `bridge/claude-opus-4-6`
- Weekly digest for masters currently looks like `not yet run`, not broken:
  - `enabled=true`
  - `expr=0 8 * * 1`
  - `tz=Europe/Moscow`
  - `lastRunAtMs=null`
  - `nextRunAtMs` is set
  - `consecutiveErrors=0`
- `S1` host `crontab` count matches expected contour:
  - `21` active entries
- Stale timers are already safe-disabled:
  - `boris-email-router.timer = disabled + inactive`
  - `chief-doctor.timer = disabled + inactive`
- Critical live entrypoints are present:
  - `email-handler`
  - `okdesk`
  - `find-executor`
  - `parse-file`
  - `tender-specialist`
- Skills workspace shape matches expected live inventory:
  - `24` top-level dirs
  - `22` real skills
  - service dirs:
    - `scripts`
    - `snippets`
- Tooling layer is confirmed by live evidence, not by snapshot-only assumptions:
  - plugin manifests are present
  - sampled session traces confirm live tool usage

### Что drift

- This is not an active live issue.
- Main drift class = docs / mental-model drift.
- Old snapshot name `parse-attachment` is obsolete; live skill is `parse-file`.
- `scripts/` and `snippets/` should not be treated as real skills.
- `jobs.json` is file-level schedule/config layer; runtime result state still needs separate verification.
- Raw trace or plugin presence alone does not equal business-critical active contour.

### Что risky

- Main risk = confusing schedule/config layer with runtime truth.
- Additional risk = treating skills/tooling layer as business master.
- `jobs.json` by itself is not proof of runtime success/failure.
- Skills are repo/runtime tooling and orchestration layer, not live business master by themselves.
- Raw trace sampling can contain noise and should not be treated as sole source of truth for tool topology.
- Plugin file presence confirms available entrypoints, but does not by itself prove business-critical routing or current business authority.

### Что требует owner decision

- Any cron redesign or consolidation.
- Any future decision around legacy timer contours.
- Any attempt to redefine the role of skills/tooling layer beyond current operational contour.

### Что требует approve

- Any live changes to:
  - cron payload models
  - `jobs.json` master/effective layers
  - host `crontab`
  - timers/services
  - helper scripts
  - plugin files
  - tool-routing entrypoints
  - server-side skill files outside a separately approved narrow scope

### Вердикт

- `OK with WARN`
- confirmed live outage not found
- current contour is mostly healthy
- current issue class is mainly docs / mental-model drift
- `jobs.json` is not runtime truth by itself
- live repair is not required for the current contour
