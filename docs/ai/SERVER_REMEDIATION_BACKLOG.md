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

### Observer doctor-agent MVP boundary documented
- Проблема: без явной docs-фиксации safe observer MVP легко спутать с новым self-heal contour или с ещё одним resident doctor loop.
- Риск: accidental expansion в `cron`, `heartbeat`, `workflow` или auto-repair, несмотря на уже зафиксированный dangerous control plane.
- Source of truth: `docs/ai/DOCTOR_AGENT_DECISION.md`.
- Минимальное исправление: в docs закрепить, что observer doctor-agent MVP = `skill + script`, `manual only`, `read-only`, `report only`, `no auto-repair`, `no cron / heartbeat / workflow` for MVP; scope ограничен `infra liveness` и `BS24 business-liveness`.
- Rollback: откатить docs-only updates, если owner позже выберет другой MVP contour.
- Post-check:
  - backlog не трактует observer doctor-agent как pending server-side self-heal implementation;
  - docs явно отделяют observer-only MVP от semantic business correctness;
  - любые periodic/background variants остаются owner-decision + approve-only.

## 3. Next server-side fixes by priority

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

### Model routing normalization
- Проблема: live routing split между `model-strategy.json`, internal `openclaw.json`, `jobs.json` и external `openclaw.json`; snapshot docs устарели по cron и External Boris.
- Риск: поломка internal cron, external Boris или fallback-chain при правке не того master-слоя.
- Source of truth: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_MODEL_ROUTING.md`, `docs/ai/SERVER_FIX_PLAN_2026-03-10.md`.
- Минимальное исправление: сначала зафиксировать intended cron override и intended external chain; потом при необходимости править только один master-слой за раз, не считая internal `openclaw.json`, `jobs.json` или external `openclaw.json` единственным master.
- Дополнительный риск: periodic enforcer для internal `jobs.json` подтверждён слабее, чем external fixer layer; `circuit-breaker-internal.py` не считать source of truth для cron models.
- Rollback: timestamped backup `model-strategy.json`, internal/external `openclaw.json` и `jobs.json` с возвратом исходных версий.
- Post-check:
  - `jq` на все model files
  - сверка layering: default-chain vs cron vs external
  - сравнение providers/fallbacks
  - controlled cron/manual invocation для internal и external

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
