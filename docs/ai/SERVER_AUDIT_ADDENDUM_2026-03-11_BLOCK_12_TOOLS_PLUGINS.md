# SERVER AUDIT ADDENDUM 2026-03-11 BLOCK 12 TOOLS PLUGINS

Docs-only фиксация результата narrow read-only audit по:
- Boris tools / plugin entrypoints / helper scripts contour

Изменения в live не выполнялись.
Это не apply changelog и не live fix.

## Block 12. Boris tools / plugin entrypoints / helper scripts contour

Статус:
- `OK with WARN`
- confirmed live outage not found
- mostly docs / mental-model drift
- live tool inventory must be proven by traces + plugin entrypoints + helper-path evidence

### Что проверено

- Repo canon и dated audit docs:
  - `docs/ai/BORIS_DETAIL_SCHEMA_CHECKLIST_v2.md`
  - `docs/ai/BASELINE_2026-03-10.md`
  - `docs/ai/OPERATING_CONSENSUS.md`
  - `docs/ai/SOURCE_OF_TRUTH.md`
  - `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md`
  - `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`
- Read-only live checks on `S1` for `2026-03-11`:
  - sampled main-agent session traces under `.openclaw/agents/main/sessions`
  - live plugin entrypoints:
    - `/data/route-command/openclaw.plugin.json`
    - `/data/callback-forward/openclaw.plugin.json`
  - referenced helper paths in sampled `exec` calls

### Что ок

- Live tooling contour is confirmed.
- Read-only traces on `S1` for `2026-03-11` confirm real tool events.
- Directly confirmed live tools:
  - `exec`
  - `process`
- `exec` remains the main bridge from Boris to server-side helper scripts.
- `process` is confirmed as the follow-up layer for long-running `exec`.
- Live plugin entrypoints are present:
  - `/data/route-command/openclaw.plugin.json`
  - `/data/callback-forward/openclaw.plugin.json`
- Confirmed helper-path evidence in sampled `exec` calls includes:
  - `/data/scripts/okdesk-comment-poller.py`
  - `/data/.openclaw/workspace/scripts/okdesk-supabase-sync.mjs`

### Что drift

- This is not a live issue.
- Main drift class = docs / mental-model / inspection-method drift.
- Old schema or snapshot assumptions do not prove live tool inventory.
- Rough grep over traces can produce:
  - false negatives
  - noisy false positives
- Plugin file presence alone does not equal business-critical active contour.
- Live inventory must be proven through:
  - traces
  - plugin entrypoints
  - referenced helper paths
- Guessed-from-schema inventory must not be treated as equal to live-observed inventory.

### Что risky

- Main risk = confusing `live-observed tools` with `guessed-from-schema tools`.
- Additional risk = treating plugin presence or helper-path references as sufficient proof of broader business-critical activity.
- `exec` remains the main operational bridge into server-side helper scripts, so a real break there would have high blast radius.
- Current audit does not confirm such a break, but it does confirm that inspection method matters.
- Tooling/plugin layer should not be treated as business master or product truth by itself.

### Что требует owner decision

- Any future redesign of tool/plugin topology.
- Any attempt to simplify or repurpose:
  - `route-command`
  - `callback-forward`
  - the helper-script bridge behind Boris tool calls

### Что требует approve

- Any live changes to:
  - plugin files
  - tool-routing entrypoints
  - helper scripts
  - Boris live tool wiring
- Any production-affecting live tests that would execute real tool actions instead of read-only trace inspection.

### Вердикт

- `OK with WARN`
- confirmed live outage not found
- current contour is mostly healthy
- current issue class is mainly docs / mental-model drift, not runtime failure
- live tool inventory must be proven by traces + plugin entrypoints + helper-path evidence
- live repair is not required for the current contour
