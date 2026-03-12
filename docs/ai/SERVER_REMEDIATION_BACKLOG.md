# SERVER REMEDIATION BACKLOG

Сводный backlog собран по итогам:
- `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`
- `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`
- `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`
- `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_OKDESK_PIPELINE.md`
- `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_MODEL_ROUTING.md`
- `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_PG_TUNNEL.md`
- `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BRIDGE_HA.md`
- `docs/ai/DOCTOR_AND_SELFHEAL_AUDIT_2026-03-11.md`
- `docs/ai/DOCTOR_AGENT_DECISION.md`
- `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_TENDER_SPECIALIST.md`
- `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BORIS_CHAT_HARDENING.md`
- `docs/ai/SERVER_CHANGELOG_2026-03-11_bridge2_subscription_fix.md`
- `docs/ai/SERVER_CHANGELOG_2026-03-11_tg_helper_token_hardening.md`
- `docs/ai/SERVER_CHANGELOG_2026-03-11_boris_wave0_chat_hardstop.md`
- `docs/ai/SERVER_CHANGELOG_2026-03-12_boris_group_selfmod_deny_and_route_closure.md`
- `docs/ai/SERVER_CHANGELOG_2026-03-12_cron_split_off_main.md`
- `docs/ai/SERVER_CHANGELOG_2026-03-12_main_per_agent_hardening_wave.md`
- `docs/ai/SERVER_CHANGELOG_2026-03-12_boris_inbound_staging_wave.md`
- `docs/ai/SERVER_CHANGELOG_2026-03-11_HQ_REQUIRE_MENTION_FAILED.md`
- `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`

## 1. Already fixed

### S1 -> S2 alias `s2` on S1
- Проблема: исходный сетевой `FAIL` был вызван отсутствием alias `s2` на S1, хотя маршрут, TCP и SSH по IP были рабочими.
- Риск: ложные `FAIL` в аудитах, сломанные runbook-команды и неверная диагностика связности между S1 и S2.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`.
- Минимальное исправление: на S1 в `/root/.ssh/config` добавлен минимальный block `Host s2 -> HostName 72.56.98.52 -> User root`.
- Rollback: восстановить `/root/.ssh/config` из backup `/root/.ssh/config.bak-20260310-194511` или удалить только block `Host s2`.
- Post-check:
  - `ssh -G s2 | egrep "^(hostname|user) "`
  - `ssh -o BatchMode=yes s2 "hostname -f"`

### S1 stale timers disabled
- Проблема: `boris-email-router.timer` и `chief-doctor.timer` на `S1` были подтверждены как `enabled + active(elapsed) + no next trigger`, то есть real stale timer state.
- Риск: silent failure двух periodic contours и ложное ощущение, что background automation всё ещё работает.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_CRON_TIMERS.md`, `docs/ai/SERVER_CHANGELOG_2026-03-10_DISABLE_STALE_TIMERS.md`.
- Минимальное исправление: по owner decision `legacy candidate, not repair` выполнен только safe disable двух timers на `S1`; related services, `crontab`, `jobs.json` и `S2` не менялись.
- Rollback: `systemctl enable` + `systemctl start` для двух timers или file-level restore из backup `/root/backup/timer-disable-20260310-234654`.
- Post-check:
  - `systemctl is-enabled boris-email-router.timer chief-doctor.timer`
  - `systemctl is-active boris-email-router.timer chief-doctor.timer`
  - `systemctl status boris-email-router.service chief-doctor.service`

### S1 cron delivery contour normalized for scoped text jobs
- Проблема: `Timur Morning Digest` уже подтвердил live false-`ok` из-за failed Telegram send, а remaining text-sending cron jobs всё ещё использовали старый inline delivery tail с positional `"$TEXT"`.
- Риск: missed digests/alerts при misleading success status, plus future reintroduction of helper-path / quoting drift.
- Source of truth:
  - `docs/ai/SERVER_CHANGELOG_2026-03-11_CRON_DELIVERY_PHASE_B.md`
  - Phase A live post-check on `2026-03-11`
- Минимальное исправление: canary-first rollout завершён.
  - Phase A:
    - `okdesk-comment-monitor` -> explicit `tz=Europe/Moscow`
    - `Timur Morning Digest` -> canonical stdin delivery tail
  - Phase B:
    - remaining 7 approved text-sending jobs -> canonical stdin delivery tails
- Rollback: restore только scoped jobs из backups:
  - `/var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json.bak-20260311-070126`
  - `/var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json.bak-20260311-073333`
  - или per-job restore из scoped backups `phaseA-scope-*` / `phaseB-scope-*`
- Post-check:
  - Phase A canary session содержит real `OK: sent to -1002799098412`
  - scoped Phase B jobs больше не содержат old actionable inline send lines
  - `Commitment Checker` и `Дайджест развития — Штаб` отдельно проверены как multi-send jobs
  - out-of-scope jobs не изменялись

### S1 stale exact-match webhook routes removed
- Проблема: на `S1` в `/etc/nginx/sites-enabled/n8n-public-edge` 3 stale exact-match webhook routes указывали на `127.0.0.1:3200`, хотя listener на `S1 :3200` отсутствовал.
- Риск: webhook paths `executor-search`, `boris-memory-read` и `boris-mention` уходили в wrong backend path вместо canonical generic `/webhook/` contour.
- Source of truth: `docs/ai/SERVER_CHANGELOG_2026-03-11_block9_webhook_routes_fix.md`.
- Минимальное исправление: удалены только 3 stale exact-match `location` blocks:
  - `/webhook/executor-search`
  - `/webhook/boris-memory-read`
  - `/webhook/boris-mention`
- Что не менялось:
  - `/hooks/`
  - generic `location /webhook/`
  - `/webhook/email-att-parse`
  - `S2 Caddy`
  - workflow flags
- Rollback: восстановить `/etc/nginx/sites-enabled/n8n-public-edge` из backup `/etc/nginx/sites-enabled/n8n-public-edge.bak-20260311-092148`, затем `nginx -t` и reload.
- Post-check:
  - 3 stale exact-match blocks отсутствуют
  - `location = /webhook/email-att-parse`, generic `location /webhook/` и `/hooks/` block сохранены
  - `nginx -t` successful
  - `systemctl is-active nginx` = `active`

### S1 Bridge 2 subscription contour fixed
- Проблема: internal Boris Bridge 2 contour на `S1` ходил в `POST /openai/chat/completions` и ловил `HTTP 404`; runtime advertising для Bridge 2 был неполным; `gpt-5.4-codex` не имел live-supported exact id.
- Риск: Boris получал live routing failure по Bridge 2 contour и мог рекламировать неполный/ошибочный набор Bridge 2 paths.
- Source of truth: `docs/ai/SERVER_CHANGELOG_2026-03-11_bridge2_subscription_fix.md`.
- Минимальное исправление:
  - в `model-strategy.json` `providers.openai-bridge2.baseUrl` исправлен с `http://172.18.0.1:8443/openai` на `http://172.18.0.1:8443/openai/v1`
  - в `providers.openai-bridge2.models` оставлены только live-supported ids:
    - `gpt-5`
    - `gpt-5.2`
    - `gpt-5.3-codex`
    - `gpt-5.4`
  - в `model_aliases` оставлены только:
    - `openai-bridge2/gpt-5`
    - `openai-bridge2/gpt-5.2`
    - `openai-bridge2/gpt-5.3-codex`
    - `openai-bridge2/gpt-5.4`
  - internal `fix-model-strategy.py` прогнан один раз
- Что не менялось:
  - `jobs.json` вручную
  - `circuit-breaker-internal.py`
  - `startup-cleanup.sh`
  - `nginx`
  - `openai-bridge.service`
  - auth
  - workflows
  - monitoring
  - external contour
- Rollback: восстановить backup из `/root/bridge2-apply-20260311T133425Z` и повторно прогнать internal `fix-model-strategy.py`.
- Post-check:
  - `openai-bridge.service` = `active`
  - runtime `openclaw.json` содержит `openai-bridge2.baseUrl = http://172.18.0.1:8443/openai/v1`
  - runtime alias keys есть для:
    - `openai-bridge2/gpt-5`
    - `openai-bridge2/gpt-5.2`
    - `openai-bridge2/gpt-5.3-codex`
    - `openai-bridge2/gpt-5.4`
  - после apply новые запросы идут только на `POST /openai/v1/chat/completions`
  - live probes успешны для `gpt-5`, `gpt-5.2`, `gpt-5.3-codex`, `gpt-5.4`
  - `gpt-5.4-codex` не добавлялся и остаётся unsupported

### S1 digest fallback chains isolated for exact morning and evening jobs
- Проблема: `Timur Evening Digest` и `Timur Morning Digest` не имели exact fallback chain и сидели на shared contour через `agentId=main`, поэтому при деградации primary модели не было узкого per-job failover только для этих jobs.
- Риск: shared fallback changes затрагивали бы лишние cron jobs, а per-job failover для двух важных digest contours оставался недоказанно невыделенным.
- Source of truth: `docs/ai/SERVER_CHANGELOG_2026-03-11_digest_fallback_chain_morning_evening.md`.
- Минимальное исправление:
  - в `model-strategy.json` добавлены exact `cron_job_routes` для:
    - `879abd47-d390-4a77-84ba-0e4631130278` `Timur Evening Digest`
    - `e5dff9f8-49ea-4623-8427-58ba62499a3b` `Timur Morning Digest`
  - runtime materialized dedicated non-default agents:
    - `cron-timur-evening-digest`
    - `cron-timur-morning-digest`
  - exact fallback chain для обоих:
    - `bridge/claude-opus-4-6`
    - `openai-bridge2/gpt-5`
    - `openai/gpt-5`
    - `nvidia/moonshotai/kimi-k2.5`
- Что не менялось:
  - delivery blocks
  - old positional send
  - raw numeric target fallback
  - unrelated cron jobs
  - `HQ requireMention`
  - `telegram-config`
  - `workspace-validator`
  - `bridge / monitoring / workflows`
  - OpenClaw core runtime
- Rollback:
  - `/root/timur-evening-fallback-20260311T164648Z`
  - `/root/timur-morning-fallback-20260311T165436Z`
  - после restore повторно прогнать internal `fix-model-strategy.py`
- Post-check:
  - evening job = `agentId=cron-timur-evening-digest`
  - morning job = `agentId=cron-timur-morning-digest`
  - `agents.list` содержит `main`, `cron-timur-evening-digest`, `cron-timur-morning-digest`
  - `payload.model` unchanged for both
  - delivery hash unchanged for both
  - `changed_non_target_count=0`
  - structural apply successful
  - natural run verification ещё впереди
  - forced canary / forced-fallback test не выполнялся

### S1 Telegram helper token-resolution contract hardened
- Проблема: shared `tg-send-helper.py` имел split token contract: host env-file использовал `TG_BOT_TOKEN`, helper file parser искал только `TELEGRAM_BOT_TOKEN`, file read не был safe, и historical failure class уже подтверждалась как `TELEGRAM_BOT_TOKEN not found`.
- Риск: helper мог вести себя по-разному между host/file/runtime contexts и снова ломать delivery contour при отсутствии inherited env или при verifier drift.
- Source of truth: `docs/ai/SERVER_CHANGELOG_2026-03-11_tg_helper_token_hardening.md`.
- Минимальное исправление:
  - в `tg-send-helper.py` зафиксирован deterministic lookup order:
    - env `TELEGRAM_BOT_TOKEN`
    - env `TG_BOT_TOKEN`
    - file `/etc/apps/secrets/openclaw.env` key `TELEGRAM_BOT_TOKEN`
    - file `/etc/apps/secrets/openclaw.env` key `TG_BOT_TOKEN`
  - file read сделан safe через `OSError` fallback
  - miss-error не выводит token value
  - `boris-health-check.py` переведён на boolean helper-resolution check через `resolve_helper_token(...)`
- Что не менялось:
  - jobs
  - model routing
  - bridge
  - monitoring
  - runtime config
  - digest payloads
- Rollback:
  - `/root/tg-helper-token-hardening-20260311T173118Z`
- Post-check:
  - `HOST_HELPER_GET_TOKEN=yes`
  - `CT_HELPER_GET_TOKEN=yes`
  - `RUNUSER_HELPER_GET_TOKEN=yes`
  - helper caller inventory unchanged
  - morning/evening digest hashes unchanged exactly
  - `payload_job_drift=[]`
  - `py_compile` passed for both files
  - `boris-health-check.py` now uses helper-resolution boolean check

### S1 Boris Wave 0 chat-admin hard stop applied
- Проблема: official Boris chat-admin surfaces на `S1` оставались live через:
  - `commands.config=true`
  - `commands.restart=true`
  - `channels.telegram.configWrites` effectively enabled because it was not explicitly disabled
- Риск: persistent config mutation и chat-triggered restart оставались возможными через official Telegram/chat contour.
- Source of truth: `docs/ai/SERVER_CHANGELOG_2026-03-11_boris_wave0_chat_hardstop.md`.
- Минимальное исправление:
  - changed only `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
  - `commands.config: true -> false`
  - `commands.restart: true -> false`
  - `channels.telegram.configWrites: absent -> false`
- Что не менялось:
  - `commands.ownerAllowFrom`
  - `commands.native`
  - `commands.nativeSkills`
  - `channels.telegram.groupPolicy`
  - `channels.telegram.replyToMode`
  - HQ `requireMention`
  - `route-command`
  - `callback-forward`
  - digest jobs
  - model routing
  - bridge / workflows / monitoring
- Rollback: не потребовался; backup = `/root/boris-wave0-chat-hardstop-20260311T191320Z`.
- Post-check:
  - changed path count = `3`
  - exact required values now:
    - `commands.config=false`
    - `commands.restart=false`
    - `channels.telegram.configWrites=false`
  - adjacent fields unchanged
  - `/config show` rejected
  - `/config set` rejected
  - `/restart` rejected
  - `/allowlist add|remove` rejected
  - rejected `/config set` did not change `openclaw.json` hash
- Important limit:
  - this Wave 0 itself did not close custom `/route`
  - separate `/route` closure was later applied successfully on `2026-03-12`; see `docs/ai/SERVER_CHANGELOG_2026-03-12_boris_group_selfmod_deny_and_route_closure.md`

### S1 group-scoped self-mod deny and formal `/route` closure applied
- Проблема: after successful Wave 0, custom `route-command` still remained a separate persistent chat-write contour, and 6 shared Telegram groups still had no group-scoped deny for runtime/self-admin classes.
- Риск: shared groups still kept a live path for `/route`-style config mutation and self-admin surfaces even though official chat-admin keys were already closed.
- Source of truth: `docs/ai/SERVER_CHANGELOG_2026-03-12_boris_group_selfmod_deny_and_route_closure.md`.
- Минимальное исправление:
  - changed only `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
  - `plugins.entries.route-command.enabled: true -> false`
  - added identical `tools.deny` to exact 6 Telegram groups:
    - `-1002799098412`
    - `-1003750223589`
    - `-1001927186400`
    - `-5245442089`
    - `-5091773177`
    - `-4972868360`
  - exact deny list:
    - `group:runtime`
    - `group:automation`
    - `group:nodes`
    - `sessions_spawn`
    - `sessions_send`
- Что не менялось:
  - per-agent `main` policy
  - `jobs.json`
  - plugin files
  - hooks
  - model routing
  - digests
  - DMs
- Rollback: не потребовался; backup = `/root/boris-route-closure-wave-20260312T083545Z`.
- Post-check:
  - `route-command.enabled=false`
  - all 6 groups now contain exact `tools.deny`
  - semantic diff in `openclaw.json` contains only 7 expected paths
  - `/route` formally closed
  - `callback-forward` unchanged:
    - `eligible=true`
    - `disabled=false`
    - `managedByPlugin=false`
  - employee capabilities preserved in the same groups:
    - `browser=true`
    - `web_search=true`
    - `web_fetch=true`
    - `image=true`
  - `group:fs` intentionally remains open
  - file-based self-mod risk reduced, not fully removed

### S1 cron split off main applied
- Проблема: stronger per-agent hardening of `main` was still blocked because enabled cron jobs still used shared `agentId=main`, plus `okdesk-comment-monitor` still used the implicit/default path.
- Риск: cron ownership remained mixed with the shared `main` agent contour, so any stronger `main` hardening still carried collateral cron risk.
- Source of truth: `docs/ai/SERVER_CHANGELOG_2026-03-12_cron_split_off_main.md`.
- Минимальное исправление:
  - manual edit only in `/var/lib/apps-data/openclaw/data/model-strategy.json`
  - added `11` exact `cron_job_routes` for the remaining jobs off `main`
  - preserved without changes:
    - existing morning/evening digest routes
    - their fallback chains
  - executed one materialization run:
    - `docker exec openclaw-kbxr-openclaw-1 python3 /data/fix-model-strategy.py`
- Derived effect:
  - `jobs.json` updated `agentId` for `11` target jobs
  - `openclaw.json` materialized `11` new cron agents in `agents.list`
- Rollback: не потребовался; backup = `/root/cron-split-main-20260312T094923Z`.
- Post-check:
  - `model-strategy.json` now has `13` exact `cron_job_routes`
  - `jobs.json` now has `0` enabled jobs on `main`
  - `jobs.json` now has `0` implicit jobs
  - `openclaw.json -> agents.list` now has `14` entries = `main + 13 cron agents`
  - duplicate ids = none
  - all `13` jobs kept unchanged:
    - `payload.model`
    - schedules
    - delivery
    - `sessionTarget`
    - `wakeMode`
  - natural runtime proof confirmed:
    - `okdesk-comment-monitor` ran on `cron-okdesk-comment-monitor` with `lastStatus=ok`
    - `HH Monitor v3` ran on `cron-hh-monitor-v3` with `lastStatus=ok`
  - main cron blocker removed

### S1 main per-agent hardening wave applied
- Проблема: after `/route` closure, group-scoped deny and cron split off `main`, shared `main` still had no per-agent deny layer for control-plane and session-orchestration surfaces.
- Риск: `main` remained broader than needed even though enabled cron jobs on `main` were already `0`; wrong hardening here still risked killing Boris employee capabilities.
- Source of truth: `docs/ai/SERVER_CHANGELOG_2026-03-12_main_per_agent_hardening_wave.md`.
- Минимальное исправление:
  - changed only `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
  - added only `agents.list[id=main].tools.deny`
  - exact value:
    - `group:automation`
    - `group:nodes`
    - `sessions_spawn`
    - `sessions_send`
- Что не менялось:
  - `group:runtime`
  - `group:fs`
  - global `tools.*`
  - Telegram group overlays
  - `model-strategy.json`
  - `jobs.json`
  - `models.json`
  - plugins
  - hooks
  - `callback-forward`
  - owner policy
  - memory layout
  - business workspace
  - model picker
  - monitoring
  - stale cleanup contours
- Rollback: не потребовался; backup = `/root/main-per-agent-hardening-20260312T115001Z`.
- Post-check:
  - semantic diff limited to `agents.list[id=main].tools.deny`
  - `main` identity unchanged
  - `jobs.json` unchanged:
    - `enabled_total=13`
    - `enabled_on_main=0`
    - `enabled_implicit=0`
  - `route-command.enabled=false` unchanged
  - `callback-forward.enabled=true` unchanged
  - all 6 Telegram group overlays unchanged
  - exact `main.tools.deny` value confirmed
  - structural compare against backup matched outside `main.tools`
  - exact gateway-side runtime resolver proof was not re-run in current safe operator context
- Employee capabilities preserved:
  - `browser`
  - `web_search`
  - `web_fetch`
  - `image`
  - `group:runtime` and `group:fs` were not touched

### S1 Boris inbound staging wave applied
- Проблема: live business flows still used raw `.openclaw/media/inbound/*`, so `main.tools.fs.workspaceOnly = true` was still blocked.
- Риск: direct `workspaceOnly=true` apply would break current business attachment flows on `main`.
- Source of truth: `docs/ai/SERVER_CHANGELOG_2026-03-12_boris_inbound_staging_wave.md`.
- Минимальное исправление:
  - created only `/var/lib/apps-data/openclaw/data/.openclaw/workspace/downloads/inbound/`
  - added only `/var/lib/apps-data/openclaw/data/scripts/stage-inbound-media.py`
  - added one minimal instruction layer only inside `File Extractor` block in `/var/lib/apps-data/openclaw/data/CLAUDE.md`
- Что не менялось:
  - `openclaw.json`
  - `main.tools.fs.workspaceOnly`
  - `group:runtime`
  - `group:fs`
  - owner policy
  - business memory
  - bridge-model routing
  - digests
  - `callback-forward`
  - monitoring
  - plugins / hooks
  - `jobs.json`
  - `model-strategy.json`
- Rollback: не потребовался; backup = `/root/boris-inbound-staging-20260312T124503Z`.
- Post-check:
  - staging dir created correctly
  - helper exists and `py_compile` passed
  - helper rejects:
    - non-inbound paths
    - path traversal
    - symlinks
  - helper returns only staged workspace path
  - staged files land only under `/var/lib/apps-data/openclaw/data/.openclaw/workspace/downloads/inbound/`
  - minimal instruction layer changed only `File Extractor` block in `CLAUDE.md`
  - no drift in routing / owner policy / business memory / digests / callback-forward / monitoring

## 2. Docs-only resolved

### Canon aligned with audited live drift
- Проблема: snapshot docs расходились с live-аудитом по `okdesk-pipeline`, model routing, gateway/file paths и workflow statuses.
- Риск: планирование серверных изменений по устаревшему snapshot, а не по проверенному live-состоянию.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`.
- Минимальное исправление: audited drift отражён только в canonical docs repo без переписывания `HANDOFF_2026-03-10.md` как live master.
- Rollback: откатить docs-only commits, в которых drift был перенесён в канон.
- Post-check:
  - `AGENTS.md` и `CLAUDE.md` читают один и тот же канон;
  - canonical docs отделяют audited facts от snapshot docs;
  - `HANDOFF_2026-03-10.md` не использован как live source of truth.

### okdesk-pipeline placement normalized in canon
- Проблема: snapshot docs описывали другой runtime-контур `okdesk-pipeline`, хотя live-аудит однозначно подтвердил runtime на `S2`.
- Риск: работа не с тем host при audit/deploy/rollback и ложное предположение о runtime split между `S1` и `S2`.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_OKDESK_PIPELINE.md`, `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`.
- Минимальное исправление: в canonical docs закреплено, что placement `okdesk-pipeline` = `S2`, live runtime source of truth = `S2 unit + S2 cron calls + S2 :3200`, а `S1` = stale path/symlink, не runtime host.
- Rollback: откатить docs-only updates, которые переносят placement drift в канон.
- Post-check:
  - canonical docs больше не описывают `S1` как runtime host `okdesk-pipeline`;
  - competing runtime между `S1` и `S2` не заявляется без live-аудита;
  - server-side placement changes помечены как approve-only.

### Prompt / memory source-of-truth aligned in canon
- Проблема: snapshot docs описывали `.openclaw/SOUL.md` и `.openclaw/memory/RULES.md`, но live-аудит подтвердил другой rules path и отсутствие `SOUL.md`.
- Риск: неверные server-side правки prompt/memory layout и ложные предположения о runtime bootstrap.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`.
- Минимальное исправление: в canonical docs зафиксировано, что live rules source of truth на S1 = `/data/.openclaw/workspace/memory/RULES.md`, `/data/.openclaw/memory` это storage/DB path, а `CLAUDE.md` не master-источник правил.
- Rollback: откатить docs-only commit, который переносит prompt/memory drift в канон.
- Post-check:
  - canonical docs больше не описывают `CLAUDE.md` как master-источник правил;
  - отсутствие `.openclaw/SOUL.md` помечено как docs drift, а не как runtime failure;
  - server-side prompt/memory changes помечены как approve-only.

### Network diagnosis normalized in docs
- Проблема: первый полный аудит трактовал проблему `S1 -> S2` как network issue, хотя это был alias drift.
- Риск: ненужная эскалация в DNS/firewall/routing и ложные выводы о деградации сети.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`, `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`.
- Минимальное исправление: в audit docs и каноне сетевой вопрос помечен как resolved alias drift, а не как активная network problem.
- Rollback: откатить docs-only обновления audit result/addendum.
- Post-check:
  - full audit больше не содержит active network `FAIL` по `S1 -> S2`;
  - alias issue отражён как resolved;
  - runbook не смешивает alias problem и real network problem.

### Gateway / health-check assumptions resolved by audit
- Проблема: snapshot docs и ранние выводы аудита создавали впечатление, что по gateway/health assumptions нужен server-side fix.
- Риск: ненужные server-side изменения в `gateway` и `monitoring`, хотя active checks уже соответствуют live.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, read-only locate active files `/opt/infra-monitor/service-guard.py`, `/opt/infra-monitor/monitor.sh`, `/opt/n8n-doctor/doctor.py`, `/opt/app/docker-compose.yml`, `/etc/systemd/system/multi-user.target.wants/caddy.service`.
- Минимальное исправление: server-side apply не делать; держать в каноне только audited facts:
  - `Caddyfile=/etc/caddy/Caddyfile`
  - local `8443` health uses `http`
  - active checks не требуют symlink для `nginx sites-enabled`
  - active checks не требуют host `:5001` для Docling
- Rollback: откатить только docs-only updates, если потребуется вернуть backlog к состоянию до locate.
- Post-check:
  - canonical docs не требуют server-side fix для этого контура
  - gateway/Docling assumptions описаны как docs drift, не как live defect
  - backlog больше не держит этот contour в pending server-side fixes

### Public bridge-ha canonical probe normalized in docs
- Проблема: weekly read-only audit подтвердил ambiguity между `n8n.brendservice24.ru/bridge-ha/health` и `ops.brendservice24.ru/bridge-ha/health`.
- Риск: false-positive health, если смотреть только на `HTTP 200`, и неверный ingress mental model при future changes.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BRIDGE_HA.md`.
- Минимальное исправление: в canonical docs закрепить, что canonical public probe = `https://n8n.brendservice24.ru/bridge-ha/health`; `ops.brendservice24.ru/bridge-ha/*` не считать canonical route; public probe валидировать по `application/json` / JSON body, а не только по `200`.
- Rollback: откатить docs-only updates, которые нормализуют `bridge-ha` public probe в каноне.
- Post-check:
  - canonical docs больше не описывают `ops.brendservice24.ru/bridge-ha/*` как canonical route;
  - public health probe в docs проверяется по JSON/application/json, а не только по `200`;
  - drift помечен как docs ambiguity, а не как live outage.

### Model routing layering documented in canon
- Проблема: snapshot docs и часть канона раньше описывали модели по значениям, но не раскладывали source of truth по слоям для internal defaults, internal cron и External Boris.
- Риск: принять effective runtime file за master и вносить server-side изменения не в тот слой.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_MODEL_ROUTING.md`, `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`.
- Минимальное исправление: в canonical docs зафиксировано, что internal default-chain master = `model-strategy.json`, internal cron declarative master = `model-strategy.json` и effective runtime = `jobs.json`, external chain master = external `fix-model-strategy.py`, а external `openclaw.json` = effective runtime.
- Rollback: откатить docs-only updates, которые добавляют model routing layering в канон.
- Post-check:
  - canonical docs больше не описывают internal `openclaw.json`, `jobs.json` или external `openclaw.json` как единственный master;
  - `circuit-breaker-internal.py` не описан как source of truth для cron models;
  - model routing layering описан как operational risk, а не как runtime failure.

### Doctor / self-heal control plane normalized in canon
- Проблема: old mental model легко сводил Boris control plane к official OpenClaw `doctor / cron / heartbeat`, хотя read-only audit подтвердил другой live reality.
- Риск: ошибочно считать monitoring/self-healing single-layer contour, недооценить dangerous auto-repair и расширить его без owner decision.
- Source of truth: `docs/ai/DOCTOR_AND_SELFHEAL_AUDIT_2026-03-11.md`.
- Минимальное исправление: в canonical docs и planning docs зафиксировать, что Boris production control plane = custom multi-layer `doctor / monitor / watchdog / self-heal` stack; разделить contours на `safe observer`, `conditional repair`, `active self-heal`, `dangerous auto-repair`; отдельно зафиксировать current coverage profile = strong infra / partial BS24 business-liveness / weak semantic business correctness.
- Rollback: откатить docs-only updates, которые переносят эту normalization в канон и backlog.
- Post-check:
  - canonical docs больше не описывают official OpenClaw doctor как полный prod control plane Бориса;
  - dangerous contours перечислены явно: `watchdog-meta`, `service-guard`, `n8n-watchdog`, `n8n-doctor`, `monitor-locks.sh`, `workspace-validator`, `promise-watchdog`;
  - docs требуют owner decision до любого расширения auto-repair.

### Observer doctor-agent MVP implemented in repo and documented
- Проблема: без явной docs-фиксации и file-layout record safe observer MVP легко спутать с новым self-heal contour или с ещё одним resident doctor loop.
- Риск: accidental expansion в `cron`, `heartbeat`, `workflow` или auto-repair, несмотря на уже зафиксированный dangerous control plane.
- Source of truth: `docs/ai/DOCTOR_AGENT_DECISION.md`, `docs/ai/OBSERVER_DOCTOR_MVP.md`.
- Минимальное исправление: в docs закрепить, что observer doctor-agent MVP уже реализован в repo как:
  - `.openclaw/workspace/skills/observer-doctor/SKILL.md`
  - `scripts/observer_doctor.py`
  - `docs/ai/OBSERVER_DOCTOR_MVP.md`
  и что его contour остаётся `manual only`, `read-only`, `report only`, `no auto-repair`, `no cron / heartbeat / workflow`.
- Rollback: откатить docs-only updates, если owner позже выберет другой MVP contour.
- Post-check:
  - backlog не трактует observer doctor-agent как pending server-side self-heal implementation;
  - docs явно отделяют observer-only MVP от semantic business correctness;
  - file layout и safe runbook задокументированы отдельно;
  - любые periodic/background variants остаются owner-decision + approve-only.

### Telegram runtime health-path contradiction on S1 corrected in docs
- Проблема: old planning treated `openclaw gateway call health --json` as proof that Telegram inbound runtime was down on `S1`, which created a false next-fix contour.
- Риск: false incident diagnosis and wrong next-step selection inside Boris chat hardening.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_TG_HEALTH_PATH_CONTRADICTION.md`.
- Минимальное исправление:
  - classify the contradiction as telemetry issue, not confirmed live outage
  - set authoritative Telegram inbound runtime proof on `S1` to `openclaw channels status --json --probe`
  - require successful authenticated gateway context and no config-only fallback
  - forbid using `openclaw gateway call health --json` as Telegram runtime proof on `S1`
- Rollback: откатить docs-only correction, если более поздний live audit покажет иную reality.
- Post-check:
  - backlog no longer keeps a separate Telegram restore apply contour
  - historical next Boris hardening contour `/route` is now closed by `docs/ai/SERVER_CHANGELOG_2026-03-12_boris_group_selfmod_deny_and_route_closure.md`

## 3. Next server-side fixes by priority

### HQ Telegram requireMention stabilization on S1
- Проблема: у Штаба live chat id = `-1002799098412`; first attempt от `2026-03-11` был откатан, потому что delayed backup check window был выбран слишком коротким относительно real validator refresh contour.
- Current state: reapply от `2026-03-11` уже выполнен, и current live runtime state now = `.channels.telegram.groups["-1002799098412"].requireMention = true`.
- Риск: до следующего eligible validator cycle `telegram-config.json` ещё может оставаться stale на `false`; это само по себе не ошибка, но final stability verdict до convergence давать нельзя.
- Source of truth:
  - `docs/ai/SERVER_CHANGELOG_2026-03-11_HQ_REQUIRE_MENTION_REAPPLY.md`
  - `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md`
- Минимальное исправление:
  - already applied as one-field runtime change:
    - `.channels.telegram.groups["-1002799098412"].requireMention: false -> true`
- Что не менять в этом contour:
  - `mentionPatterns`
  - `replyToMode`
  - `topic overrides`
  - `workspace-validator.py`
  - routing
  - workflows
  - bridge
  - monitoring
- Apply status: current status = `runtime success, pending validator convergence`.
- Exact next validator refresh window:
  - `2026-03-12 04:02:37 UTC` to `2026-03-12 04:04:37 UTC`
  - `2026-03-12 07:02:37 MSK` to `2026-03-12 07:04:37 MSK`
- Rollback: current apply did not require rollback; future rollback is needed only if later validator convergence goes wrong.
- Post-check:
  - immediate field flip in runtime = passed
  - `mentionPatterns`, `replyToMode`, topic overrides unchanged = passed
  - stale `telegram-config.json` before the window above = not an error
  - delayed convergence validator backup к `requireMention=true`
  - only then считать contour stable

### Tender specialist skill hygiene on S1
- Проблема: weekly narrow audit подтвердил, что `tender-specialist` живёт на `S1` как server-side Boris skill, и его contour уже фактически = `skill + script`, но в `SKILL.md` остались три узкие проблемы orchestration-layer.
- Риск: неверный tool reference внутри skill, слишком широкая формулировка scope и отсутствие явной do-not-touch boundary рядом с критичными contours Бориса.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_TENDER_SPECIALIST.md`.
- Минимальное исправление:
  - `parse-attachment -> parse-file`
  - убрать опасную формулировку про "видишь все сообщения пользователей и сам решаешь"
  - явно прописать do-not-touch boundary для `routing/workflows/bridge/monitoring/model files/jobs`
- Почему это low-risk: это точечный server-side patch только в одном file `tender-specialist/SKILL.md`, без правок scripts, `jobs.json`, model files, workflows, bridge или monitoring.
- Apply status: пока не делался.
- Change window: отложено до `low-risk change window` (`будни 12:00–15:00 MSK`).
- Rollback: backup текущего `tender-specialist/SKILL.md` и file-level restore.
- Post-check:
  - `sed -n`/diff по `tender-specialist/SKILL.md`
  - убедиться, что ссылка идёт на `parse-file`
  - убедиться, что boundary и trigger wording стали уже, а соседние contours не затронуты

На текущий момент других подтвержденных next server-side fixes по этому backlog больше нет.

- `boris-email-router.timer` и `chief-doctor.timer` уже выведены из remaining actions через safe disable.
- `Дайджест развития — Канал мастеров` оставлен без apply и не считается broken cron.

## 4. Approve-only fixes

### Boris employee architecture hardening program on S1
- Проблема: Boris must remain a full employee agent, but current shared-trust contour still mixes employee capabilities with self-modification / self-admin / owner-policy and system-core boundaries.
- Риск:
  - wrong hardening can kill Boris employee capabilities
  - wrong separation can mix business work, owner policy, business memory, session memory and system core
  - even after successful per-agent hardening of `main` and successful inbound staging `B1`, the remaining architecture waves still must not be mixed with owner-policy / business-memory separation
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_BORIS_EMPLOYEE_ARCHITECTURE.md`.
- Минимальное исправление:
  - no direct live fix in this backlog item
  - preserve as approve-only architecture wave stack
- Exact next waves:
  - collect live evidence that Boris now stages inbound attachments before file-tool access
  - `B2: agents.list[id=main].tools.fs.workspaceOnly = true`
  - `owner policy layer`
  - `business memory writer`
  - self-modification deny without killing employee capabilities
  - later model exposure narrowing
- Guardrails:
  - no blanket-deny of browser/web/file business work
  - no direct rewrite of system core for owner-policy persistence
  - no mixing of business memory with system core
- Rollback:
  - not applicable until a specific approved wave is applied
- Post-check:
  - backlog keeps the architecture wave order explicit
  - docs preserve the employee-capability boundary separately from self-admin denial

### pg-tunnel-s2 contingency contour on S1
- Проблема: на `S1` остаётся `pg-tunnel-s2.service`, но weekly narrow audit подтвердил, что current Boris PG mode = `local`, current backend = `boris-emails-pg-1`, а tunnel конфликтует с local PG по `172.18.0.1:15432`.
- Риск: operational noise, ложная диагностика PostgreSQL contour и accidental fix не того data plane.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_PG_TUNNEL.md`.
- Минимальное исправление: server-side apply по умолчанию не нужен; сначала owner decision, считать ли contour contingency-слоем или выводить его из эксплуатации; только потом approve-only apply по unit/monitoring/local PG contour.
- Rollback: для любого будущего apply откатывать пофайлово unit, auto-services / monitoring logic и local PG routing из backup на `S1`.
- Post-check:
  - `/var/lib/apps-data/infra-monitor/state/boris-pg-mode` = `local`
  - `boris-emails-pg-1` healthy и слушает `172.18.0.1:15432`
  - `sync-pg-from-s2.sh` / `sync-executors-from-s2.sh` продолжают работать через `ssh/scp`
  - `pg-tunnel-s2.service` не трактуется как current live dependency без нового live-аудита

### okdesk-pipeline server-side placement changes
- Проблема: live placement уже однозначно подтвержден на `S2`, но на `S1` остаётся stale path/symlink, который может провоцировать неверные server-side действия.
- Риск: accidental deploy/restart/migration не на том host или разрушение рабочего pipeline-контура на `S2`.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_OKDESK_PIPELINE.md`, `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`.
- Минимальное исправление: server-side apply сейчас не нужен; если потребуется cleanup `S1` path, перенос placement, правка unit или cron, делать это только после explicit approve.
- Rollback: для любого такого apply откатывать unit/crontab/path changes пофайлово из backup на затронутом сервере.
- Post-check:
  - `systemctl status okdesk-pipeline` на `S2`
  - `ss -ltn | grep :3200` на `S2`
  - отсутствие competing unit/process на `S1`
  - рабочие `S2` cron calls на `localhost:3200`

### Prompt / memory source-of-truth cleanup on S1
- Проблема: `.openclaw/SOUL.md` отсутствует, `RULES.md` живёт только в `workspace/memory`, а snapshot docs описывают другой layout.
- Риск: появление двух расходящихся master-paths, сломанный bootstrap или лишний compatibility layer без подтвержденной необходимости.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`, `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`.
- Минимальное исправление: сначала выбрать один server-side master-path для правил и только потом решать, нужен ли compatibility file/symlink или правка loader-path.
- Rollback: вернуть исходное дерево prompt/memory files из backup.
- Post-check:
  - agent bootstrap
  - чтение правил
  - отсутствие двух расходящихся master-файлов

### Workflow state reconciliation
- Проблема: live `WF11` и `WF8 Watchdog` inactive, хотя snapshot docs говорят обратное.
- Риск: включение или отключение не тех workflow, рассинхрон между n8n live state и operational expectations.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_WORKFLOWS.md`, `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`.
- Минимальное исправление: сначала owner decision по intended state для `WF11` и `WF8 Watchdog`, потом менять только нужные `active` flags, не опираясь на snapshot docs; сверку делать по workflow id, не только по названию.
- Rollback: restore предыдущих workflow states из DB snapshot/export.
- Post-check:
  - SQL по `workflow_entity` для exact workflow IDs
  - n8n executions
  - watchdog/error logs

### Email Attachment Parser state
- Проблема: workflow выглядит `inactive`, но это не конфликт между snapshot docs и live.
- Риск: ложная активация on-demand workflow только потому, что inactive ошибочно принят за drift.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_WORKFLOWS.md`, `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`.
- Минимальное исправление: server-side apply не делать; считать `Email Attachment Parser inactive` текущей нормой, пока owner не решит иначе.
- Rollback: не требуется, потому что apply не нужен.
- Post-check:
  - в каноне workflow отражён как `inactive`
  - backlog не требует отдельной активации этого workflow

### Expansion of auto-repair rights inside doctor/self-heal contour
- Проблема: current Boris control plane already has overlapping dangerous auto-repair contours, but docs without an explicit boundary make future widening look safer than it really is.
- Риск: дополнительный blast radius по runtime/config/workflows, особенно при расширении прав у `watchdog-meta`, `service-guard`, `n8n-watchdog`, `n8n-doctor`, `monitor-locks.sh`, `workspace-validator`, `promise-watchdog`.
- Source of truth: `docs/ai/DOCTOR_AND_SELFHEAL_AUDIT_2026-03-11.md`.
- Минимальное исправление: server-side apply по умолчанию не нужен; сначала owner decision, нужно ли вообще расширять auto-repair; только потом approve-only apply для конкретного contour.
- Rollback: restore script/unit/cron/baseline changes и прежние repair boundaries из timestamped backups конкретного contour.
- Post-check:
  - classification observer/repair/self-heal не меняется без owner decision;
  - official OpenClaw docs не используются как единственное обоснование для расширения Boris prod control plane;
  - новые auto-repair rights не затрагивают соседние dangerous contours.

## 5. Postponed

### Миграция okdesk-pipeline между S2 и S1
- Проблема: есть docs drift по placement, но нет доказательства, что текущий S2 runtime неисправен.
- Риск: ненужная миграция работающего сервиса с большим blast radius по cron, routes и integration chain.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`.
- Минимальное исправление: отложить до отдельного архитектурного решения; не трогать placement только ради соответствия `HANDOFF`.
- Rollback: если миграция когда-то начнется, rollback = возврат unit, cron и routes на исходный сервер.
- Post-check:
  - pipeline health
  - Caddy/nginx routes
  - cron endpoints
  - `DRY_RUN` behavior

### Восстановление `.openclaw/SOUL.md` как compatibility file
- Проблема: файл отсутствует, но по аудиту нет доказанного runtime failure.
- Риск: создание лишнего compatibility path, который будет принят за обязательный source of truth без реальной потребности.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`, `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`.
- Минимальное исправление: не делать, пока не появится подтверждение, что конкретный loader реально требует этот path.
- Rollback: удалить compatibility file или symlink.
- Post-check:
  - bootstrap/prompts load
  - отсутствие duplicate-source drift
