# FINAL REMAINING ACTIONS

Итоговый документ после:
- полного server read-only аудита;
- узких addendum-аудитов;
- docs-only нормализации канона;
- принятых owner decisions по workflow state, `okdesk-pipeline` placement и model routing architecture.

Цель документа: оставить только реально незакрытые действия и убрать то, что уже исправлено, закрыто docs-only или принято как текущая норма без server-side apply.

## 1. Already fixed

### S1 -> S2 alias `s2` on S1
- Что это: low-risk fix для SSH alias `s2` на `S1`.
- Почему не осталось: проблема была alias drift, а не network failure; alias уже добавлен и post-check пройден.
- Нужен ли apply: нет, apply уже выполнен успешно.
- Риск: повторный ручной rework может только заново внести drift.
- Rollback: восстановить `/root/.ssh/config` из backup `/root/.ssh/config.bak-20260310-194511` или удалить только block `Host s2`.
- Post-check:
  - `ssh -G s2 | egrep "^(hostname|user) "`
  - `ssh -o BatchMode=yes s2 "hostname -f"`

### S1 stale timers disabled safely
- Что это: safe disable для двух stale timers на `S1`:
  - `boris-email-router.timer`
  - `chief-doctor.timer`
- Почему не осталось: owner принял решение `legacy candidate, not repair`; apply уже выполнен, timers переведены в `disabled + inactive`, связанные services не тронуты.
- Нужен ли apply: нет, apply уже выполнен успешно.
- Риск: повторное вмешательство может только случайно re-enable legacy contour или затронуть соседние services.
- Rollback: `systemctl enable ...timer` + `systemctl start ...timer` или file-level restore из backup `/root/backup/timer-disable-20260310-234654`.
- Post-check:
  - `systemctl is-enabled boris-email-router.timer chief-doctor.timer`
  - `systemctl is-active boris-email-router.timer chief-doctor.timer`
  - `systemctl status boris-email-router.service chief-doctor.service`

### Cron delivery contour normalized for text-sending Boris jobs
- Что это: canary-first live apply по cron delivery contour на `S1`.
- Почему не осталось: false-`ok` на `Timur Morning Digest` закрыт в Phase A, `okdesk-comment-monitor` получил explicit `tz=Europe/Moscow`, а remaining scoped text-sending jobs в Phase B переведены на canonical stdin delivery tail.
- Нужен ли apply: нет, apply уже выполнен успешно.
- Риск: будущая ручная правка prompt tail может снова вернуть inline `"$TEXT"` delivery, `~/scripts` drift или ложный textual `ok`.
- Rollback: пофайлово восстановить scoped jobs из backups:
  - `/var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json.bak-20260311-070126`
  - `/var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json.bak-20260311-073333`
  - или из scoped backups `phaseA-scope-*` / `phaseB-scope-*`
- Post-check:
  - `Timur Morning Digest` canary session зафиксировал `OK: sent to -1002799098412`
  - `okdesk-comment-monitor` live имеет explicit `tz=Europe/Moscow`
  - scoped Phase B jobs live содержат canonical stdin send blocks
  - `Timur Morning Digest`, `okdesk-comment-monitor` и `Дайджест развития — Канал мастеров` не были затронуты в Phase B

### S1 stale exact-match webhook exceptions removed
- Что это: narrow live routing fix для `S1 /etc/nginx/sites-enabled/n8n-public-edge`.
- Почему не осталось: подтвержденный Block 9 live issue закрыт; 3 stale exact-match webhook routes больше не перехватывают трафик в несуществующий `S1 :3200`.
- Нужен ли apply: нет, apply уже выполнен успешно.
- Риск: future ручная правка `n8n-public-edge` может вернуть stale exceptions и снова увести эти webhook paths мимо canonical generic `/webhook/` contour.
- Rollback: восстановить `/etc/nginx/sites-enabled/n8n-public-edge` из backup `/etc/nginx/sites-enabled/n8n-public-edge.bak-20260311-092148` и повторить `nginx -t` + reload.
- Post-check:
  - удалены только `location = /webhook/executor-search`, `location = /webhook/boris-memory-read`, `location = /webhook/boris-mention`
  - сохранены `location = /webhook/email-att-parse`, generic `location /webhook/` и `/hooks/` contour
  - `nginx -t` successful, `systemctl is-active nginx` = `active`

### S1 Bridge 2 subscription contour fixed
- Что это: narrow live apply для internal Boris model routing -> Bridge 2 subscription contour на `S1`.
- Почему не осталось: confirmed live `404` на `POST /openai/chat/completions` устранён; runtime переведён на `POST /openai/v1/chat/completions`; Boris-facing Bridge 2 paths теперь заведены только для подтверждённых live ids.
- Нужен ли apply: нет, apply уже выполнен успешно.
- Риск: будущая ручная правка runtime вместо master или добавление unsupported alias/id может снова вернуть `404` или ложное advertising.
- Rollback: восстановить `model-strategy.json`, `openclaw.json`, `models.json`, `jobs.json` из backup `/root/bridge2-apply-20260311T133425Z` и повторно прогнать internal `fix-model-strategy.py`.
- Post-check:
  - `openai-bridge.service` остался `active`
  - runtime `openclaw.json` содержит `openai-bridge2.baseUrl = http://172.18.0.1:8443/openai/v1`
  - runtime alias keys есть для:
    - `openai-bridge2/gpt-5`
    - `openai-bridge2/gpt-5.2`
    - `openai-bridge2/gpt-5.3-codex`
    - `openai-bridge2/gpt-5.4`
  - `jobs.json` по enabled models остался `bridge/claude-opus-4-6`
  - после apply новые запросы идут только на `POST /openai/v1/chat/completions`
  - live probes успешны для `gpt-5`, `gpt-5.2`, `gpt-5.3-codex`, `gpt-5.4`
  - `gpt-5.4-codex` не добавлялся и остаётся unsupported

### Exact digest fallback chains isolated for morning and evening jobs
- Что это: narrow live apply для two exact digest cron jobs на `S1`:
  - `879abd47-d390-4a77-84ba-0e4631130278` `Timur Evening Digest`
  - `e5dff9f8-49ea-4623-8427-58ba62499a3b` `Timur Morning Digest`
- Почему не осталось: exact per-job fallback chain уже добавлен и materialized через dedicated non-default agents; оба jobs больше не сидят на shared `agentId=main` contour.
- Нужен ли apply: нет, apply уже выполнен успешно.
- Риск: future ручная правка runtime вместо `model-strategy.json` или broad change shared fallback contour может случайно убрать per-job isolation или задеть unrelated cron jobs.
- Rollback: восстановить backup соответствующего apply и повторно прогнать internal `fix-model-strategy.py`:
  - `/root/timur-evening-fallback-20260311T164648Z`
  - `/root/timur-morning-fallback-20260311T165436Z`
- Post-check:
  - `Timur Evening Digest` = `agentId=cron-timur-evening-digest`
  - `Timur Morning Digest` = `agentId=cron-timur-morning-digest`
  - `agents.list` содержит `main`, `cron-timur-evening-digest`, `cron-timur-morning-digest`
  - `payload.model` для обоих остался `bridge/claude-opus-4-6`
  - delivery hash для обоих не изменился
  - `changed_non_target_count=0`
  - structural apply успешен, но natural run verification ещё впереди; forced fallback canary отдельно не запускался

### Telegram helper token-resolution contract hardened globally
- Что это: narrow live apply для shared Telegram helper token-resolution contour на `S1`.
- Почему не осталось: `tg-send-helper.py` больше не зависит от split contract между host env-file key и runtime env; historical class `TELEGRAM_BOT_TOKEN not found` закрыт на helper layer.
- Нужен ли apply: нет, apply уже выполнен успешно.
- Риск: future ручная правка helper lookup order или verifier drift может снова вернуть host/container mismatch и ложные проверки.
- Rollback: восстановить backup `/root/tg-helper-token-hardening-20260311T173118Z`.
- Post-check:
  - `HOST_HELPER_GET_TOKEN=yes`
  - `CT_HELPER_GET_TOKEN=yes`
  - `RUNUSER_HELPER_GET_TOKEN=yes`
  - helper caller inventory unchanged
  - morning/evening digest hashes unchanged exactly
  - `payload_job_drift=[]`
  - `boris-health-check.py` использует boolean helper-resolution check

### Wave 0 Boris chat self-modification hard stop on S1
- Что это: narrow live hard stop по official Boris chat-admin surfaces на `S1`.
- Почему не осталось: apply уже выполнен успешно и закрыл exact official chat-admin keys:
  - `commands.config: true -> false`
  - `commands.restart: true -> false`
  - `channels.telegram.configWrites: absent -> false`
- Source of truth:
  - `docs/ai/SERVER_CHANGELOG_2026-03-11_boris_wave0_chat_hardstop.md`
  - `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BORIS_CHAT_HARDENING.md`
- Что это остановило:
  - `/config*` from chat
  - `/restart` from chat
  - Telegram `/allowlist add|remove`
  - Telegram config writes from chat
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
- Rollback: не потребовался; backup лежит в `/root/boris-wave0-chat-hardstop-20260311T191320Z`.
- Post-check:
  - changed path count = `3`
  - only exact approved key paths changed
  - `/config show` and `/config set` rejected
  - `/restart` rejected
  - `/allowlist add|remove` rejected
  - `openclaw.json` hash remained unchanged after rejected `/config set`
- Important limit:
  - этот Wave 0 сам по себе не закрывал custom `/route`
  - separate `/route` closure was applied later on `2026-03-12`; see `docs/ai/SERVER_CHANGELOG_2026-03-12_boris_group_selfmod_deny_and_route_closure.md`

### Group-scoped self-mod deny and formal `/route` closure on S1
- Что это: narrow live hardening wave for custom `/route` plus group-scoped self-mod deny on 6 shared Telegram groups on `S1`.
- Почему не осталось: apply уже выполнен успешно и закрыл separate persistent chat-write contour `/route`, while adding identical group-scoped deny policy without touching per-agent `main`.
- Source of truth:
  - `docs/ai/SERVER_CHANGELOG_2026-03-12_boris_group_selfmod_deny_and_route_closure.md`
  - `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_TG_HEALTH_PATH_CONTRADICTION.md`
  - `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BORIS_CHAT_HARDENING.md`
  - `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCK_12_TOOLS_PLUGINS.md`
- Что это закрыло:
  - `plugins.entries.route-command.enabled: true -> false`
  - identical `tools.deny` on exact 6 Telegram groups:
    - `-1002799098412`
    - `-1003750223589`
    - `-1001927186400`
    - `-5245442089`
    - `-5091773177`
    - `-4972868360`
  - exact denied surfaces:
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
- Rollback: не потребовался; backup лежит в `/root/boris-route-closure-wave-20260312T083545Z`.
- Post-check:
  - `route-command.enabled=false`
  - semantic diff in `openclaw.json` = only 7 expected paths
  - `callback-forward` remained `eligible=true`, `disabled=false`, `managedByPlugin=false`
  - employee capabilities preserved in the 6 groups:
    - `browser=true`
    - `web_search=true`
    - `web_fetch=true`
    - `image=true`
  - `group:fs` intentionally remains open in this wave
  - file-based self-mod risk reduced, not fully removed

## 2. Docs-only resolved

### Canon aligned with audited live drift
- Что это: canonical docs приведены к verified live facts без переписывания snapshot docs как live master.
- Почему не осталось: drift уже перенесен в канон repo, поэтому отдельный server-side apply не нужен.
- Нужен ли apply: нет.
- Риск: вернуться к planning по snapshot docs вместо audited canon.
- Rollback: откатить соответствующие docs-only commits, если когда-либо потребуется вернуться к состоянию до аудитов.
- Post-check:
  - canonical docs отделяют audited live facts от snapshot docs;
  - `HANDOFF_2026-03-10.md` не используется как live source of truth.

### Prompt / memory source-of-truth normalized in docs
- Что это: в docs закреплено, что live rules source of truth на `S1` = `/data/.openclaw/workspace/memory/RULES.md`, `/data/.openclaw/memory` это storage/DB path, `.openclaw/SOUL.md` отсутствует.
- Почему не осталось: по аудиту это docs drift, а не runtime failure.
- Нужен ли apply: нет.
- Риск: ошибочно начать server-side cleanup layout без подтвержденной необходимости.
- Rollback: откатить docs-only updates по prompt/memory канону.
- Post-check:
  - docs не называют `CLAUDE.md` master-источником правил;
  - отсутствие `.openclaw/SOUL.md` помечено как docs drift.

### Gateway / health-check assumptions normalized in docs
- Что это: docs обновлены под live facts: `Caddyfile=/etc/caddy/Caddyfile`, local `8443` health по `http`, `sites-enabled` не обязаны быть symlink, Docling не требует host `:5001`.
- Почему не осталось: read-only locate подтвердил, что active server-side checks уже соответствуют live.
- Нужен ли apply: нет.
- Риск: делать лишний apply в `gateway` или `monitoring` по уже закрытому docs drift.
- Rollback: откатить docs-only updates по этому контуру.
- Post-check:
  - backlog больше не держит этот contour как pending server-side fix;
  - gateway assumptions в docs совпадают с live locate.

### Public bridge-ha canonical probe normalized in docs
- Что это: docs приведены к weekly read-only факту, что canonical public `bridge-ha` probe = `https://n8n.brendservice24.ru/bridge-ha/health`, а `ops.brendservice24.ru/bridge-ha/*` не является canonical route.
- Почему не осталось: current live ingress работает; drift был в docs / ingress mental model, а не в самом bridge-ha runtime.
- Нужен ли apply: нет.
- Риск: future checks могут снова получить false-positive, если смотреть только на `HTTP 200` и использовать `ops` path.
- Rollback: откатить docs-only updates по `bridge-ha` canonical probe.
- Post-check:
  - canonical docs используют `n8n` URL как public probe;
  - public probe в docs валидируется по JSON/application/json, а не только по `200`;
  - `ops` path не описывается как supported canonical route без нового решения владельца.

### Workflow state documented by exact workflow IDs
- Что это: live workflow state закреплен в docs по exact workflow IDs, а не только по названиям.
- Почему не осталось: docs drift уже закрыт на уровне документации и reconciliation rules.
- Нужен ли apply: нет.
- Риск: будущая сверка только по названиям может снова дать ложный drift.
- Rollback: откатить docs-only updates по workflow audit.
- Post-check:
  - docs требуют reconciliation по workflow id;
  - live state зафиксирован как `WF3/WF8 relay/WF10/Telegram Logger/WF Watchdog=active`, `WF11/WF8 Watchdog/Email Attachment Parser=inactive`.

### okdesk-pipeline placement normalized in docs
- Что это: в docs закреплено, что canonical placement `okdesk-pipeline` = `S2`, а `S1` это stale path/symlink, не runtime host.
- Почему не осталось: narrow audit снял гипотезу про runtime split; это docs drift с operational risk, но не активный runtime conflict.
- Нужен ли apply: нет.
- Риск: снова начать deploy/rollback planning по `S1`.
- Rollback: откатить docs-only updates по placement.
- Post-check:
  - docs больше не описывают `S1` как runtime host;
  - live source of truth в docs = `S2 unit + S2 cron calls + S2 :3200`.

### Model routing layering documented in canon
- Что это: канон теперь явно раскладывает source of truth для internal default-chain, internal cron и External Boris по слоям.
- Почему не осталось: docs gap закрыт; separate server-side simplification сейчас не требуется.
- Нужен ли apply: нет.
- Риск: принять `openclaw.json` или `jobs.json` за единственный master и сломать routing не в том слое.
- Rollback: откатить docs-only updates по model routing layering.
- Post-check:
  - docs различают declarative master и effective runtime;
  - `circuit-breaker-internal.py` не описан как source of truth для cron models.

### Writer / enforcer map documented in canon
- Что это: новый read-only audit `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md` плюс docs-only правило искать master / derived / writer chain до любого server-side apply.
- Почему не осталось: docs gap закрыт; карта active/potential writers уже зафиксирована без server-side изменений.
- Нужен ли apply: нет.
- Риск: снова править runtime-файл как будто он stable master, игнорируя startup/cron/doctor/monitor/sync rewrite layer.
- Rollback: откатить docs-only updates и новый audit doc, если когда-либо потребуется вернуться к состоянию до этого read-only аудита.
- Post-check:
  - канон требует сначала искать master, derived/runtime, writers/enforcers и trigger writers;
  - critical target files больше не трактуются как safe-to-edit runtime по умолчанию.

### Doctor / self-heal control plane normalized in canon
- Что это: в каноне и backlog зафиксировано, что Boris production control plane = custom multi-layer `doctor / monitor / watchdog / self-heal` stack, а не только official OpenClaw doctor path.
- Почему не осталось: это docs-only normalization по `docs/ai/DOCTOR_AND_SELFHEAL_AUDIT_2026-03-11.md`; отдельный server-side apply не нужен.
- Нужен ли apply: нет.
- Риск: снова планировать monitoring/self-healing так, будто official OpenClaw docs описывают весь prod control plane, либо расширить dangerous auto-repair без owner decision.
- Rollback: откатить docs-only updates по canon/backlog, если более поздний live audit покажет иную control-plane topology.
- Post-check:
  - docs разделяют `safe observer`, `conditional repair`, `active self-heal`, `dangerous auto-repair`;
  - docs явно фиксируют current coverage profile = strong infra / partial BS24 business-liveness / weak semantic correctness;
  - dangerous contours перечислены отдельно и не описываются как safe defaults.

### Observer doctor-agent MVP implemented in repo and documented
- Что это: в repo уже существуют implementation files observer-doctor MVP:
  - `.openclaw/workspace/skills/observer-doctor/SKILL.md`
  - `scripts/observer_doctor.py`
  - `docs/ai/OBSERVER_DOCTOR_MVP.md`
- Почему не осталось: safe observer MVP уже оформлен как `skill + script`, `manual only`, `read-only`, `report only`, `no auto-repair`; отдельный server-side apply для самого MVP не нужен.
- Нужен ли apply: нет.
- Риск: будущая реализация может случайно превратиться в новый background monitoring/self-heal contour или выйти за границы observer-only.
- Rollback: откатить docs-only updates, если owner позже выберет другую архитектуру или scope.
- Post-check:
  - docs фиксируют chosen architecture = `skill + script`;
  - file layout задокументирован в `docs/ai/OBSERVER_DOCTOR_MVP.md`;
  - MVP ограничен `infra liveness` + `BS24 business-liveness`;
  - semantic business correctness и любые repair actions остаются вне scope;
  - dated safe live-check `2026-03-11` зафиксирован как operational snapshot, не как вечная live truth.

### Telegram runtime health-path contradiction on S1 corrected in docs
- Что это: follow-up read-only audit on `2026-03-12` resolved the contradiction between `openclaw gateway call health --json` and Telegram runtime status on `S1`.
- Почему не осталось: issue class reclassified as telemetry issue, not confirmed live outage; Telegram restore apply is not required.
- Source of truth:
  - `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_TG_HEALTH_PATH_CONTRADICTION.md`
- Rollback: откатить docs-only correction, если более поздний live audit опровергнет этот вывод.
- Post-check:
  - canonical docs explicitly name `openclaw channels status --json --probe` as the authoritative Telegram inbound runtime check on `S1`
  - canonical docs explicitly forbid using `openclaw gateway call health --json` as Telegram runtime proof on `S1`
  - historical next hardening contour `/route` has now been closed by `docs/ai/SERVER_CHANGELOG_2026-03-12_boris_group_selfmod_deny_and_route_closure.md`

### Boris employee architecture/security target state documented
- Что это: docs-only фиксация architecture/security analysis по Boris как full employee agent with self-modification denied and with explicit owner-policy/business-memory separation.
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_BORIS_EMPLOYEE_ARCHITECTURE.md`.
- Почему не осталось как docs gap:
  - в каноне теперь явно зафиксировано, что Boris не простой чат-бот, а full employee agent
  - employee capabilities нужно сохранять, а не убивать blanket-deny
  - self-admin / self-modification surfaces нужно deny-ить отдельно от business work
  - target architecture = 4 слоя:
    - system core
    - owner policy
    - business memory
    - session/task memory
- Почему это docs-only:
  - документ фиксирует accepted architecture/security target state
  - он не делает live apply и не заменяет отдельные approved hardening waves
- Post-check:
  - канон и backlog ссылаются на один dated addendum
  - key decisions по owner-policy layer, business-memory separation и `cron split off main` сохранены в repo, а не только в чате

## 3. Decisions accepted, no apply needed

### Workflow states accepted as current norm
- Что это: owner decisions приняты для `WF11=inactive`, `WF8 Watchdog=inactive`, `Email Attachment Parser=inactive/on-demand`.
- Почему не осталось: live уже совпадает с этими состояниями; отдельный apply не нужен.
- Нужен ли apply: нет.
- Риск: позже ошибочно трактовать эти `inactive` состояния как drift и самовольно включить workflows.
- Rollback: не требуется, потому что apply не выполняется.
- Post-check:
  - docs и backlog трактуют эти состояния как accepted current norm;
  - любые будущие изменения workflow flags помечены как approve-only.

### okdesk-pipeline canonical host accepted = S2
- Что это: owner decision принят: runtime `okdesk-pipeline` остается на `S2`.
- Почему не осталось: live уже соответствует решению; миграция или cleanup не нужны по умолчанию.
- Нужен ли apply: нет.
- Риск: попытка “допривести к handoff” через ненужный перенос сервиса.
- Rollback: не требуется, пока server-side apply не запускается.
- Post-check:
  - docs и backlog описывают `S2` как canonical host;
  - `S1` помечен только как stale path/symlink.

### Model routing architecture accepted = keep layered split
- Что это: owner decision принят: текущий layered split по model routing сохраняется, immediate live simplification не делается.
- Почему не осталось: live уже работает в этой архитектуре; задача на consolidation сейчас не открывается.
- Нужен ли apply: нет.
- Риск: начать unplanned simplification и задеть internal cron, External Boris или failover logic.
- Rollback: не требуется, пока server-side apply не запускается.
- Post-check:
  - backlog больше не трактует consolidation как обязательное следующее действие;
  - docs описывают layered split как accepted live reality.

## 4. Remaining server-side actions truly still needed

### Boris employee architecture separation program on S1
- Что это: approve-only architecture wave stack, needed to keep Boris as a full employee agent while removing self-modification and mixed-trust control-plane behavior.
- Почему осталось:
  - Wave 0 already closed official chat-admin surfaces
  - shared trust boundary still remains
  - owner policy and business memory are still not separated from system/core planning
  - stronger per-agent hardening of `main` is blocked while `10` enabled jobs still use `agentId=main` and one more enabled job (`okdesk-comment-monitor`) still has `agentId=null`
- Source of truth: `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-12_BORIS_EMPLOYEE_ARCHITECTURE.md`.
- Exact next architecture waves to preserve:
  - `cron split off main`
  - `owner policy layer`
  - `business memory writer`
  - `employee workspace / safe business file tooling`
  - self-modification deny without killing employee capabilities
  - later model exposure narrowing for shared chats
- Guardrails:
  - do not blanket-deny browser/web/file business work
  - do not mix business work with system-core mutation
  - do not move owner authority into normal business memory
  - do not harden `main` broadly before `cron split off main`
- Rollback:
  - not applicable until a specific approved server-side wave exists
- Post-check:
  - backlog preserves wave order
  - Boris employee capability boundary and self-mod deny boundary stay explicit in docs

### HQ Telegram requireMention stabilization on S1
- Что это: узкий live fix для Штаба в Telegram group/chat `-1002799098412`.
- Current state: reapply от `2026-03-11` уже выполнен; live canonical runtime field now = `.channels.telegram.groups["-1002799098412"].requireMention = true`.
- Что осталось: не новый apply, а только delayed validator-convergence verification для `/var/lib/apps-data/boris-doctor/backups/telegram-config.json`.
- Source of truth:
  - `docs/ai/SERVER_CHANGELOG_2026-03-11_HQ_REQUIRE_MENTION_REAPPLY.md`
  - `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md`
- Что не менялось этим apply:
  - `mentionPatterns`
  - `replyToMode`
  - topic overrides
  - `workspace-validator.py`
  - routing
  - workflows
  - bridge
  - monitoring
- Exact next validator refresh window:
  - `2026-03-12 04:02:37 UTC` to `2026-03-12 04:04:37 UTC`
  - `2026-03-12 07:02:37 MSK` to `2026-03-12 07:04:37 MSK`
- Important:
  - `telegram-config.json` still showing `false` before that window is expected and must not be treated as an error
- Stable success condition:
  - runtime field stays `true`
  - validator backup converges to `requireMention=true` on the next eligible cycle
  - `mentionPatterns`, `replyToMode`, topic overrides remain unchanged
- Rollback: не потребовался на immediate post-check; future rollback нужен только если later validator convergence goes wrong

### Tender specialist skill hygiene on S1
- Что это: узкий server-side patch для Boris skill `tender-specialist` на `S1`.
- Почему осталось: read-only audit подтвердил, что skill живёт в live skill-layer Boris на `S1`, contour устроен как `skill + script`, но в самом `SKILL.md` нужны три точечные правки:
  - `parse-attachment -> parse-file`
  - убрать опасную широкую формулировку про "видишь все сообщения пользователей и сам решаешь"
  - явно прописать do-not-touch boundary для `routing/workflows/bridge/monitoring/model files/jobs`
- Нужен ли apply: да, но только как low-risk server-side change в отдельное рабочее окно.
- Риск: patch ночью или без backup не нужен; patch шире одного skill-файла уже выйдет из agreed scope.
- Rollback: timestamp backup `tender-specialist/SKILL.md` + file-level restore.
- Post-check:
  - проверить updated `SKILL.md`
  - проверить, что contour по-прежнему = `skill + script`, а не уехал в routing/workflow/cron territory
  - убедиться, что scripts и соседние skills не менялись

Других подтвержденных remaining server-side actions сейчас больше нет.

- `boris-email-router.timer` и `chief-doctor.timer` уже безопасно отключены по owner decision.
- `Дайджест развития — Канал мастеров` оставлен как есть и не считается broken.
- Если позже появится новый live drift после `2026-03-10`, нужен новый read-only audit перед любым apply.

## 5. Optional housekeeping only

### pg-tunnel-s2 contingency contour on S1
- Что это: residual tunnel-based contour для старого Boris PG mode на `S1`.
- Почему не осталось: current live Boris PG mode уже `local`, local `boris-emails-pg-1` healthy, а `S2 -> S1` sync идёт через `ssh/scp` scripts; tunnel не является current live dependency.
- Нужен ли apply: нет по умолчанию; только если owner отдельно решит оставить contour как contingency или выводить его из эксплуатации.
- Риск: `failed` unit и monitoring noise могут путать диагностику и future apply planning.
- Rollback: при любом будущем approve-only apply восстановить исходный unit / monitoring enrollment / local PG routing из backup.
- Post-check:
  - `/var/lib/apps-data/infra-monitor/state/boris-pg-mode` = `local`
  - `service-guard` видит Boris PG contour healthy в local mode
  - `sync-pg-from-s2.sh` и `sync-executors-from-s2.sh` продолжают работать без tunnel

### ops-domain `/bridge-ha/*` support
- Что это: потенциальное future-решение поддерживать `bridge-ha` не только на `n8n` domain, но и на `ops` domain.
- Почему не осталось: current canonical public probe уже работает на `n8n` domain; `ops` domain активен, но path `/bridge-ha/*` на нём сейчас не поддерживается и не считается live outage.
- Нужен ли apply: нет по умолчанию; только если owner явно захочет supported `/bridge-ha/*` route и на `ops` domain.
- Риск: ненужный ingress change с затрагиванием `gateway`, `bridge` и failover routing.
- Rollback: восстановить прежние `nginx`/`Caddy`/Cloudflare settings из backup конкретного контура.
- Post-check:
  - `https://n8n.brendservice24.ru/bridge-ha/health` остаётся valid JSON probe
  - `ops` domain либо остаётся unsupported для `/bridge-ha/*`, либо после approve-only apply начинает давать тот же expected JSON

### S1 stale okdesk-pipeline path cleanup
- Что это: cleanup stale `S1` path/symlink, который больше не считается runtime host.
- Почему не осталось: это не active runtime problem и не competing runtime.
- Нужен ли apply: нет по умолчанию; только если owner отдельно захочет housekeeping.
- Риск: удалить path, который ещё нужен для runbook, backup-логики или будущего deploy-процесса.
- Rollback: вернуть symlink/path из backup или recreate его ровно в прежнем виде.
- Post-check:
  - на `S1` по-прежнему нет competing unit/process/port `:3200`;
  - `S2` runtime остается рабочим.

### Prompt / memory compatibility cleanup
- Что это: потенциальное создание compatibility file для `.openclaw/SOUL.md` или иная перестройка prompt/memory layout.
- Почему не осталось: live runtime failure не доказан; текущий layout стабилен.
- Нужен ли apply: нет.
- Риск: создать duplicate-source drift или сломать bootstrap без реальной причины.
- Rollback: удалить compatibility file/symlink и вернуть исходный layout из backup.
- Post-check:
  - bootstrap/prompts load;
  - отсутствие двух расходящихся master-paths.

### Internal cron periodic enforcer hardening
- Что это: возможное future-усиление periodic sync для internal `jobs.json`.
- Почему не осталось: owner принял layered split как текущую норму, а нехватка stronger enforcer сейчас зафиксирована как operational risk, но не как доказанная runtime failure.
- Нужен ли apply: нет по умолчанию.
- Риск: вмешаться в routing layer без явной необходимости и зацепить cron model overrides.
- Rollback: восстановить исходные `jobs.json`, `fix-model-strategy.py`, `circuit-breaker-internal.py`, startup/cron hooks из backup.
- Post-check:
  - internal cron models остаются ожидаемыми;
  - не возникает unintended rewrite runtime routing.

### Architectural migration of okdesk-pipeline
- Что это: возможная будущая миграция `okdesk-pipeline` между `S2` и `S1`.
- Почему не осталось: owner уже принял `S2` как canonical host; миграция сейчас не нужна.
- Нужен ли apply: нет.
- Риск: большой blast radius по `systemd`, `cron`, integration routes и rollback.
- Rollback: вернуть unit, cron и routes на исходный хост.
- Post-check:
  - pipeline health;
  - `S2 :3200`;
  - интеграционные cron endpoints;
  - отсутствие runtime split.

### Tender specialist patch timing
- Что это: timing constraint для уже найденного low-risk patch в live skill-layer Boris.
- Почему не осталось: сам patch ещё не сделан, но и emergency apply не нужен.
- Нужен ли apply: только в `low-risk change window`.
- Риск: делать patch вне окна без необходимости.
- Rollback: не отличается от file-level rollback для `tender-specialist/SKILL.md`.
- Post-check:
  - apply запускать только в `будни 12:00–15:00 MSK`
  - scope не расширять дальше одного skill file

## 6. Do not touch list

### Workflow live flags and workflow logic
- Что это: любые изменения `active/inactive`, logic, imports/exports или DB state в `n8n`.
- Почему не осталось: current accepted workflow states уже совпадают с live; новых apply-задач здесь нет.
- Нужен ли apply: нет, если нет отдельного explicit approval.
- Риск: прямое изменение production behavior.
- Rollback: только через DB snapshot/export restore и controlled workflow rollback.
- Post-check:
  - exact workflow IDs в `workflow_entity`;
  - `n8n` executions и logs после любой approve-only операции.

### okdesk-pipeline service state, placement, cron and deploy paths
- Что это: любые server-side изменения unit, path, cron calls, deploy location или restart `okdesk-pipeline`.
- Почему не осталось: canonical placement уже принят и live стабилен на `S2`.
- Нужен ли apply: нет, если нет отдельного explicit approval.
- Риск: accidental migration, cleanup не того path или остановка рабочего runtime.
- Rollback: пофайловый restore unit/crontab/path changes из backup.
- Post-check:
  - `systemctl status okdesk-pipeline`
  - `ss -ltn | grep :3200`
  - рабочие `S2` cron calls на `localhost:3200`

### Derived/runtime files behind active writer chains
- Что это: любые runtime/derived файлы, которые уже подтверждены как объекты startup/cron/doctor/monitor/sync rewrite layer.
- Почему не осталось: отдельного apply здесь нет; это safety boundary, а не backlog item.
- Нужен ли apply: нет, если нет explicit approval и заранее подготовленного плана по master/writer layer.
- Риск: ручная правка исчезнет после следующего writer trigger и создаст ложный вывод, будто apply "не сработал".
- Rollback: rollback делать не по runtime-файлу отдельно, а по master/writer chain этого контура.
- Post-check:
  - перед любым future apply использовать `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md`;
  - сначала синхронизировать master и writer layer, а не только runtime.

### Model routing files, fixers and startup hooks
- Что это: любые изменения `model-strategy.json`, internal/external `openclaw.json`, `jobs.json`, `fix-model-strategy.py`, `circuit-breaker-internal.py`, startup scripts и related cron.
- Почему не осталось: owner принял текущую layered architecture, а live routing уже документирован.
- Нужен ли apply: нет, если нет отдельного explicit approval.
- Риск: поломка internal default-chain, cron override, External Boris chain или bridge failover logic.
- Rollback: restore всех затронутых routing files/scripts из timestamped backups.
- Post-check:
  - `jq` на routing files
  - layering check: default-chain vs cron vs external
  - controlled validation internal/external flows

### Prompt / memory server-side layout
- Что это: любые правки rules paths, loader paths, compatibility files и related bootstrap behavior на `S1`.
- Почему не осталось: текущий layout stable; runtime failure не доказан.
- Нужен ли apply: нет, если нет отдельного explicit approval.
- Риск: duplicate-source drift или bootstrap regression.
- Rollback: restore исходного prompt/memory tree из backup.
- Post-check:
  - live rules path остается однозначным;
  - bootstrap читает ожидаемый rules file.

### Doctor / monitor / self-heal contour expansion
- Что это: любые попытки перевести observer -> repair, расширить rights/coverage существующего auto-repair или добавить новый dangerous auto-repair path.
- Почему не осталось: current control plane уже имеет high overlap и high blast radius; новой approved задачи на расширение нет.
- Нужен ли apply: нет, если нет отдельного owner decision и explicit approval.
- Риск: усилить auto-repair поверх уже опасных contours:
  - `watchdog-meta`
  - `service-guard`
  - `n8n-watchdog`
  - `n8n-doctor`
  - `monitor-locks.sh`
  - `workspace-validator`
  - `promise-watchdog`
- Rollback: restore затронутых scripts, units, cron entries, baseline/registry logic и widened permissions из timestamped backups конкретного контура.
- Post-check:
  - risk class contour не изменился без зафиксированного owner decision;
  - dangerous contours не получили новые repair права "по пути";
  - official OpenClaw docs не используются как единственное обоснование для расширения prod control plane.

### Gateway, bridge, auth, routing, monitoring, secrets and destructive actions
- Что это: любые изменения вне узко подтвержденных docs-only drift-контуров.
- Почему не осталось: active checks уже соответствуют live; серверный apply по этим зонам сейчас не требуется.
- Нужен ли apply: нет, если нет отдельного explicit approval.
- Риск: высокий blast radius и выход за пределы подтвержденных аудитов.
- Rollback: только по заранее подготовленным backup и rollback plan для конкретного контура.
- Post-check:
  - layer-specific verification
  - соседние контуры не деградировали
  - secrets не были затронуты
