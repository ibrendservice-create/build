# OPERATING CONSENSUS

## Purpose
Этот файл задает общий канон памяти и общий safety contour для Claude и Codex внутри этого репозитория.

## Scope
- Только repo docs и project instruction files.
- Runtime, server-side truth, live workflows и secrets находятся вне этого repo.
- `docs/ai/HANDOFF_2026-03-10.md` и внешний `Boris-Detail-Schema.txt` используются для аудита, а не как live master.
- `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_OKDESK_PIPELINE.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_MODEL_ROUTING.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_CRON_TIMERS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_PG_TUNNEL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BRIDGE_HA.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCKS_5_6_7_8.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCK_10_MONITORING.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCK_11_CRON_SKILLS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCK_12_TOOLS_PLUGINS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BORIS_CHAT_HARDENING.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_TG_RUNTIME_BLOCKER_CONTEXT.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_TG_HEALTH_PATH_CONTRADICTION.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_BORIS_EMPLOYEE_ARCHITECTURE.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_S1_GATEWAY_RESTART_AUTHORIZATION_PATH.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_XLSX_DETERMINISTIC_PROOF_PATH.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_XLSX_PERMISSION_AUTHENTIC_STEP1_PROOF_PATH.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-13_RAW_INBOUND_GUARD_PATCH_LOCATION_MISS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-13_DUAL_INSTALL_CLI_PROOF_PATH.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-13_REAL_DM_RUNTIME_NPM_GLOBAL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-13_XLSX_PROOF_CHAIN_COMPLETE.md` и `docs/ai/DOCTOR_AND_SELFHEAL_AUDIT_2026-03-11.md` это dated audit docs: они фиксируют проверенные live-факты и accepted architecture/security analysis на дату документа, но не заменяют live master после этой даты.

## Canonical read order
1. `docs/ai/OPERATING_CONSENSUS.md`
2. `docs/ai/PROJECT_MEMORY.md`
3. `docs/ai/SOURCE_OF_TRUTH.md`
4. `docs/ai/CHANGE_POLICY.md`
5. `docs/ai/VERIFICATION_MATRIX.md`
6. `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`
7. `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`
8. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`
9. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`
10. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_OKDESK_PIPELINE.md`
11. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_MODEL_ROUTING.md`
12. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_CRON_TIMERS.md`
13. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCKS_5_6_7_8.md`
14. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCK_10_MONITORING.md`
15. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCK_11_CRON_SKILLS.md`
16. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCK_12_TOOLS_PLUGINS.md`
17. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BORIS_CHAT_HARDENING.md`
18. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_TG_RUNTIME_BLOCKER_CONTEXT.md`
19. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_TG_HEALTH_PATH_CONTRADICTION.md`
20. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_BORIS_EMPLOYEE_ARCHITECTURE.md`
21. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_S1_GATEWAY_RESTART_AUTHORIZATION_PATH.md`
22. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_XLSX_DETERMINISTIC_PROOF_PATH.md`
23. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_XLSX_PERMISSION_AUTHENTIC_STEP1_PROOF_PATH.md`
24. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-13_RAW_INBOUND_GUARD_PATCH_LOCATION_MISS.md`
25. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-13_DUAL_INSTALL_CLI_PROOF_PATH.md`
26. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-13_REAL_DM_RUNTIME_NPM_GLOBAL.md`
27. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-13_XLSX_PROOF_CHAIN_COMPLETE.md`
28. `docs/ai/DOCTOR_AND_SELFHEAL_AUDIT_2026-03-11.md`
28. `docs/ai/HANDOFF_2026-03-10.md`
29. `Boris-Detail-Schema.txt` только если файл явно дан для аудита; сырой файл не копировать в repo.

## Document priority
- `AGENTS.md` и `CLAUDE.md` это agent entry points; они должны ссылаться на один и тот же канон и не расходиться по правилам проекта.
- Канон repo: этот файл плюс `docs/ai/PROJECT_MEMORY.md`, `docs/ai/SOURCE_OF_TRUTH.md`, `docs/ai/CHANGE_POLICY.md`, `docs/ai/VERIFICATION_MATRIX.md`, `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`, `docs/ai/SKILL_AUTHORING_POLICY.md`.
- Dated audit docs: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_OKDESK_PIPELINE.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_MODEL_ROUTING.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_CRON_TIMERS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_PG_TUNNEL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BRIDGE_HA.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCKS_5_6_7_8.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCK_10_MONITORING.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCK_11_CRON_SKILLS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCK_12_TOOLS_PLUGINS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BORIS_CHAT_HARDENING.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_TG_RUNTIME_BLOCKER_CONTEXT.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_TG_HEALTH_PATH_CONTRADICTION.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_BORIS_EMPLOYEE_ARCHITECTURE.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_S1_GATEWAY_RESTART_AUTHORIZATION_PATH.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_XLSX_DETERMINISTIC_PROOF_PATH.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_XLSX_PERMISSION_AUTHENTIC_STEP1_PROOF_PATH.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-13_RAW_INBOUND_GUARD_PATCH_LOCATION_MISS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-13_DUAL_INSTALL_CLI_PROOF_PATH.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-13_REAL_DM_RUNTIME_NPM_GLOBAL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-13_XLSX_PROOF_CHAIN_COMPLETE.md` и `docs/ai/DOCTOR_AND_SELFHEAL_AUDIT_2026-03-11.md`.
- Snapshot docs: `docs/ai/HANDOFF_2026-03-10.md` и внешний `Boris-Detail-Schema.txt`.
- `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md` = read-only audit helper по writer/enforcer chains; это не новый live master, а карта overwrite/restore контуров.
- Live server-side truth проверяется только вне repo.

## Canon vs snapshots
- Канон определяет правила работы, safety contour и способ чтения памяти.
- Snapshot docs нужны для аудита, инвентаризации и фиксации состояния на дату снимка.
- Snapshot docs нельзя автоматически повышать до source of truth для live-системы.

## Conflict handling
- Если канон и snapshot docs расходятся, не угадывать.
- Если факта нет в repo и он относится к live-системе, не додумывать.
- В таких случаях помечать `SERVER_AUDIT_REQUIRED`.
- Не переписывать snapshot-документы в качестве live truth без server-side verification.
- Если dated audit docs и snapshot docs расходятся по уже проверенному факту, фиксировать drift в каноне и не переписывать snapshot docs.

## Shared safety contour
- сначала проверка, потом изменение;
- сначала source of truth, потом runtime;
- сначала master/derived/writer chain, потом apply;
- сначала нижний слой, потом верхний;
- только минимальный change set;
- всегда иметь rollback;
- всегда делать post-change verification;
- не читать и не выводить секреты.
- не расширять auto-repair contour без owner decision и explicit approve.

Before editing any live config, first identify:
- source of truth
- derived/runtime file
- all writers/enforcers
- their triggers
- whether the target will be rewritten after apply

If a writer/enforcer exists, do not patch runtime directly unless the change plan explicitly covers the writer layer too.

## Writer chain rule
- Перед любой server-side правкой сначала искать:
  - master;
  - derived/runtime;
  - writers/enforcers;
  - trigger writers.
- Нельзя править runtime/derived файл, если его потом перезапишет writer/enforcer.
- Если конфиг живёт через layered sync, менять нужно master-слой.
- Если apply нужен в runtime, сначала надо:
  - либо обновить master;
  - либо обновить writer layer;
  - либо отдельно и осознанно отключить enforcer по approved plan.
- Для критичных target files writer chain должен быть зафиксирован заранее; быстрый audit helper для этого = `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md`.

## Forbidden without explicit approve
- auth;
- routing;
- gateway;
- bridge;
- monitoring / self-healing;
- workflows и live workflow state;
- server-side truth вне этого repo;
- runtime/generated files вместо master;
- secrets / tokens / credentials;
- restart критичных сервисов или контейнеров;
- destructive actions;
- широкий refactor вне текущей задачи.
- расширение observer/repair/self-heal прав внутри monitoring / self-healing contour.

## Audit-backed live deltas as of 2026-03-10
- Canonical placement `okdesk-pipeline` = `S2`; `HANDOFF` по этому контуру теперь snapshot drift.
- Live runtime source of truth для `okdesk-pipeline` на дату аудита = `S2 systemd unit + S2 cron calls + S2 listener :3200`.
- `S1` по `okdesk-pipeline` сейчас = stale path/symlink, а не runtime host.
- Competing runtime между `S1` и `S2` по `okdesk-pipeline` аудит не подтвердил; это docs drift с operational risk, а не active runtime split.
- Любые server-side правки placement, unit, cron или path для `okdesk-pipeline` требуют explicit approve.
- Internal cron models live = `bridge/claude-opus-4-6`; internal interactive default-chain live = `bridge/claude-sonnet-4-6` с fallback-цепочкой из `model-strategy.json`.
- External live routing = `anthropic/claude-haiku-4-5 -> openai/gpt-5`.
- Internal default-chain master = `model-strategy.json`; internal `openclaw.json` это effective runtime, а не единственный master.
- Internal cron declarative master = `model-strategy.json`; internal cron effective runtime = `jobs.json`.
- External Boris chain master = external `fix-model-strategy.py`; external `openclaw.json` это effective runtime, а не master.
- Internal cron periodic sync в `jobs.json` подтверждён слабее, чем external fixer layer: startup sync подтверждён, но явный periodic enforcer для `jobs.json` не зафиксирован так же прямо, как для external.
- `circuit-breaker-internal.py` по inspected code не считать source of truth для cron models; он мутирует `openclaw.json`, но не подтверждён как owner/master для `jobs.json`.
- Model routing contour сейчас классифицирован как layered split с operational risk, а не как подтверждённая runtime failure.
- Live prompt/memory paths: `.openclaw/SOUL.md` отсутствует; live rules source of truth на S1 = `/data/.openclaw/workspace/memory/RULES.md`.
- `/data/.openclaw/memory` в live используется как storage/DB path, а не как rules path.
- `CLAUDE.md` в live не является master-источником правил; он только ссылается на `workspace/memory/RULES.md`.
- Для attachment/file skill authoring canonical live rule layer = `RULES.md`; repo authoring canon for this contour = `docs/ai/SKILL_AUTHORING_POLICY.md`.
- Prompt/memory drift сейчас классифицирован как docs drift, а не как подтвержденный runtime failure.
- Live Caddyfile path = `/etc/caddy/Caddyfile`, и active server-side checks уже используют этот path.
- `sites-enabled` на S1 сейчас regular files, не symlink, и active checks не требуют symlink-type для этих nginx files.
- Local health для `8443` проверяется по `http`, не по `https`, и active checks уже используют `http`.
- Docling не публикует host `:5001`, но доступен внутри docker-сети, и active checks не требуют host `:5001`.
- Для этого gateway/health-check контура server-side apply по path/probe assumptions не нужен; это docs drift, закрытый read-only аудитом и locate.
- Live workflow statuses, подтвержденные аудитом по workflow id: WF3 `active`, WF8 relay `active`, WF10 `active`, Telegram Logger `active`, WF Watchdog `active`, WF11 `inactive`, WF8 Watchdog `inactive`, Email Attachment Parser `inactive`.
- Для workflow reconciliation использовать exact workflow id, а не только названия, потому что live labels частично дрейфуют.
- `WF11` и `WF8 Watchdog` сейчас классифицированы как docs drift + owner decision before apply, а не как подтвержденная runtime-авария.
- `Email Attachment Parser inactive` сейчас трактуется как норма, а не как drift.
- S1 -> S2 проблема из первого аудита была alias drift; сеть и SSH по IP рабочие.
- `boris-email-router.timer` на S1 = `enabled + active(elapsed) + Trigger:n/a`; `chief-doctor.timer` на S1 = `enabled + active(elapsed) + Trigger:n/a`.
- Эти два timers сейчас классифицированы как `housekeeping debt` с `operational risk`, а не как docs drift.
- По ним нужен owner decision before apply: это еще нужные periodic contours или уже legacy.
- `Дайджест развития — Канал мастеров` в `jobs.json` = `enabled`, `nextRunAtMs` задан, `lastRunAtMs=null`; это сейчас трактуется как `not yet run`, а не как broken cron.
- Для этого housekeeping-контура на S2 live опирается на `crontab`, а не на `systemd timers`.
- Любые server-side изменения prompt/memory layout требуют explicit approve.

## Weekly addenda 2026-03-11
- `pg-tunnel-s2.service` на `S1` не является current live dependency; current Boris PG mode on `S1` = `local`.
- `pg-tunnel-s2.service` конфликтует с local `boris-emails-pg-1` по `172.18.0.1:15432`.
- Live sync `S2 -> S1` сейчас идёт через `ssh/scp` scripts, а не через `pg-tunnel-s2.service`.
- `pg-tunnel-s2.service` сейчас классифицирован как `legacy noise` с `operational risk`, а не как runtime failure.
- По `pg-tunnel-s2.service` нужен owner decision before apply: оставить contingency contour или выводить из эксплуатации.
- Canonical public `bridge-ha` probe = `https://n8n.brendservice24.ru/bridge-ha/health`.
- `ops.brendservice24.ru/bridge-ha/*` не является canonical route; `ops` domain активен, но path `/bridge-ha/*` на нём не поддерживается.
- Public `bridge-ha` probe считать valid не только по `HTTP 200`, но и по `application/json` / JSON body.
- `bridge-ha` ambiguity сейчас классифицирована как `docs drift / ingress ambiguity`, а не как live outage.
- По `ops` domain owner decision нужен только если владелец хочет supported `/bridge-ha/*` route и на этом домене.
- Boris production control plane = custom multi-layer `doctor / monitor / watchdog / self-heal` stack, а не только official OpenClaw doctor path.
- Official OpenClaw `doctor / cron / heartbeat` docs объясняют Gateway primitives, но не описывают текущий Boris production control plane целиком.
- Repo-visible classification for current control plane:
  - `safe observer`: `chief-doctor` read-only contour, `check-cron-health.sh`
  - `conditional repair`: `memory-watchdog.py`, `ssh-watchdog.sh`
  - `active self-heal`: `boris-doctor`, `monitor-safe`
  - `dangerous auto-repair`: `watchdog-meta`, `service-guard`, `n8n-watchdog`, `n8n-doctor`, `monitor-locks.sh`, `workspace-validator`, `promise-watchdog`
- Repo-visible coverage profile:
  - strong infrastructure coverage
  - partial BS24 business-liveness coverage
  - weak semantic business correctness coverage
- Block 10 monitoring result on `2026-03-11`:
  - core monitoring contour is alive on both servers
  - active outage is not confirmed
  - current issue class = working control plane with legacy monitoring drift on `S1`, not pure docs drift
- `monitor-safe.service` on both servers is `disabled/inactive`; stale `heartbeat-safe.json` by itself is not a standalone incident.
- Stale monitored contours currently visible in `S1` monitoring-space:
  - `pg-tunnel-s2`
  - `okdesk-pipeline`
- Block 11 cron/skills result on `2026-03-11`:
  - internal cron model layer matches canon
  - `jobs.json` has `13` enabled jobs and all enabled jobs use `bridge/claude-opus-4-6`
  - `Дайджест развития — Канал мастеров` remains `not yet run`, not broken
  - current issue class = mainly docs / mental-model drift, not live outage
- Block 12 Boris tools/plugins result on `2026-03-11`:
  - live tooling contour is confirmed
  - sampled traces directly confirm real `exec` and `process` tool events
  - live plugin entrypoints `route-command` and `callback-forward` are present
  - current issue class = docs / mental-model / inspection-method drift, not live outage
- Boris chat hardening result on `2026-03-11`:
  - conversational runtime currently shares operator/control surfaces
  - Wave 0 hard stop target = `commands.config`, `commands.restart`, `channels.telegram.configWrites`
  - this Wave 0 does not close custom `/route`; `/route` remains a separate open contour
- Historical Telegram runtime blocker follow-up on `2026-03-11`:
  - Wave 0 hard stop, helper token hardening and exact morning/evening digest fallback isolation were already applied before the follow-up
  - `/route` was not confirmed as an active live Telegram contour
  - gateway snapshot showed Telegram `configured=true`, but `running=false`
  - `callback-forward` remains a separate internal hook contour
  - `/route` closure is paused by stop condition and reclassified as stale-config cleanup candidate until Telegram inbound runtime is restored or intentionally left off
  - historical next contour on `2026-03-11` = Telegram inbound runtime restore / audit on `S1`
  - do not mix Telegram runtime restore with `/route` closure
- Telegram runtime health-path correction on `2026-03-12`:
  - prior restore blocker was reclassified as telemetry issue, not confirmed live outage
  - exact authoritative Telegram inbound runtime proof on `S1` = `openclaw channels status --json --probe`
  - use that path only in successful authenticated gateway context and without config-only fallback
  - `openclaw gateway call health --json` is not authoritative for Telegram inbound runtime; it uses a coarse cached summary and Telegram runtime fields default to `false/null/none`
  - config-only fallback in `channels status --probe` is not runtime proof
  - CLI auth/device-signature issues can create false incident diagnosis
  - Telegram restore contour closed as not-needed
  - next active hardening contour = `/route` closure
- S1 gateway restart/reload authorization path on `2026-03-12`:
  - current narrow runtime activation path on `S1` is absent
  - current broader valid activation path = Docker restart of container `openclaw-kbxr-openclaw-1`
  - exact blocker is dual:
    - `commands.restart=false`
    - direct gateway RPC from current CLI/operator context fails with `device signature invalid`
  - do not reopen `commands.restart` just to activate a runtime patch
  - `B2` remains blocked until the broader activation contour is approved and completed
- Deterministic XLSX proof path before `B2` on `2026-03-12`:
  - prior one-step canary was nondeterministic and proved only MIME sniffing
  - one-step canary is insufficient
  - deterministic proof before `B2` must be two-step:
    - Step 1 = ingress/staging proof
    - Step 2 = workbook semantic proof
  - pass requires trace/log evidence, not only assistant answer
  - `B2` remains blocked until both proof steps pass
- Permission-authentic Step 1 proof refinement before `B2` on `2026-03-12`:
  - live evidence does not support manual canary artifact mismatch as the reason for the latest failed `Step 1`
  - the failed manual canary artifact matched the normal raw inbound owner/mode/ACL pattern on `S1`
  - one more manual permission-matched raw artifact is not the recommended next proof path
  - safest next proof path is:
    - future separate patch-location correction of the raw-inbound guard patcher
    - then separate re-activation of the corrected guard patch
    - then one real Telegram-uploaded XLSX `Step 1` canary
    - then immediate read-only audit
  - `B2` remains blocked until that correction is applied and then that proof passes
- Raw-inbound guard patch-location root cause before `B2` on `2026-03-13`:
  - the latest real permission-authentic `Step 1` canary on `S1` used the embedded fallback bundle family
  - the active hook path for the real native `read` was in `subagent-registry-eWk4_pdR.js`
  - the approved raw-inbound guard patch had been applied only to `reply-XaR8IPbY.js`
  - therefore the real canary did not execute the patched guard logic
  - that exact patch-location miss is why no `RAW_INBOUND_GUARD` marker appeared
  - that exact patch-location miss is why no staged same-basename file was created
  - before any new activation attempt, patch-location correction is required on the source-of-truth patcher
  - another canary before that correction is operationally useless
  - `B2` remains blocked until the correction is applied and then `Step 1` and `Step 2` both pass
- Dual-install drift and invalid CLI `Step 1` proof path before `B2` on `2026-03-13`:
  - patch-location correction for the `/usr/local` family is already completed successfully; see `docs/ai/SERVER_CHANGELOG_2026-03-13_raw_inbound_guard_patch_location_correction.md`
  - the latest failed `Step 1` did not run through the corrected Boris DM/gateway runtime family
  - exact session `457e5be6-81f5-487f-af88-fb9d602461a2` used the unpatched `.npm-global` CLI path
  - therefore that failure is proof-path drift, not a new miss inside the corrected `/usr/local` family
  - direct `openclaw agent` canary must not be treated as valid Boris DM/gateway proof for `Step 1`
  - dual-install drift exists between the corrected `/usr/local/...` family and the separate unpatched `.npm-global/...` CLI family
  - next valid `Step 1` must run only through the real Boris DM/gateway path
  - `Step 2` remains blocked until that valid `Step 1` passes
  - `B2` remains blocked until valid `Step 1` passes and then `Step 2` passes
- Real Boris DM runtime family root cause before `B2` on `2026-03-13`:
  - the latest failed real Boris DM `Step 1` also did not go through the corrected `/usr/local` family
  - exact session `6a152919-5d0c-47f0-a3ee-30b0252d789b` logged the real DM `read` from `/data/.npm-global/lib/node_modules/openclaw/dist/entry.js`
  - real Boris DM/gateway runtime currently resolves through the active unpatched `.npm-global` family
  - this is why no `RAW_INBOUND_GUARD` marker appeared and no staged same-basename file was created
  - `/usr/local` patch-location correction remains accepted, but it is not sufficient for `Step 1` proof while the real DM runtime is still bound to `.npm-global`
  - another canary before correcting the active `.npm-global` family is operationally useless
  - `Step 2` remains blocked until `.npm-global` correction is completed and then a valid Boris DM `Step 1` passes
  - `B2` remains blocked until that corrected-valid `Step 1` passes and then `Step 2` passes
- XLSX proof chain completion on `2026-03-13`:
  - `.npm-global` guard correction was applied on `2026-03-13`; see `docs/ai/SERVER_CHANGELOG_2026-03-13_npm_global_raw_inbound_guard_correction.md`
  - Step 1 (ingress/staging proof) passed on real Boris DM/gateway path through `.npm-global` runtime
  - RAW_INBOUND_GUARD v1 fired, staged file created, `XLSX_READ_PROOF_OK` confirmed
  - original Step 2 proof model (read-only, no exec) was invalid: binary XLSX requires a parser
  - replacement Staged Semantic Parse Proof used `exec` + `openpyxl` on staged path only
  - Step 2 (workbook semantic proof) passed: exact cell values extracted, staged path used, raw inbound avoided
  - both steps trace-verified in session `6a152919-5d0c-47f0-a3ee-30b0252d789b`
  - `B2` (`workspaceOnly=true`) was unblocked and then applied successfully on `2026-03-13`
  - B2 apply: `agents.list[id=main].tools.fs.workspaceOnly = true`; pre-check 10/10 PASS, post-check 9/9 PASS, no rollback needed
  - see `docs/ai/SERVER_CHANGELOG_2026-03-13_b2_workspaceonly_apply.md`
  - Boris XLSX proof chain + B2 apply is now CLOSED
  - next truly open contours: owner policy layer, cron/master SoT migration, tender specialist skill hygiene, auth-profile/EACCES normalization
- Boris employee architecture/security analysis on `2026-03-12`:
  - Boris must be treated as a full employee agent, not a simple chat bot
  - employee capabilities must be preserved while self-modification and self-admin are denied
  - target architecture is a 4-layer split: system core, owner policy, business memory, session/task memory
  - owner authority must persist through a separate owner-policy layer, not by rewriting system core
  - business memory must be separated from system core
  - `cron split off main` is required before stronger per-agent hardening of `main`
  - shared trust boundary remains until business workspace and control-plane separation are completed
- `scripts/` and `snippets/` under skills workspace are service dirs, not real skills.
- Old snapshot name `parse-attachment` is obsolete; live skill entrypoint is `parse-file`.
- `jobs.json` is schedule/config layer, not runtime truth by itself.
- Live tool inventory must be proven by traces + plugin entrypoints + helper-path evidence, not by old schema alone.
- Любое расширение auto-repair поверх текущего control plane требует сначала owner decision, затем explicit approve.

## Remaining unresolved contradictions
- Эти audit-backed facts корректны только на даты аудитов `2026-03-10`, `2026-03-11` и `2026-03-12`; если задача зависит от их текущего live-состояния позже, требуется `SERVER_AUDIT_REQUIRED`.
- Все неаудированные live-факты из `HANDOFF` и внешней схемы по-прежнему нельзя повышать до master без отдельной проверки.
