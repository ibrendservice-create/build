# SOURCE OF TRUTH

## Базовое правило
- Никогда не считать runtime/generated файл источником истины, если есть master-конфиг, patcher, generator или sync pipeline.
- Перед любой server-side правкой сначала определить не только master, но и derived/runtime файл, active/potential writers/enforcers и их trigger chain.

## Канон внутри repo
- Для project instructions и planning source of truth в repo: `docs/ai/OPERATING_CONSENSUS.md`, `docs/ai/PROJECT_MEMORY.md`, `docs/ai/SOURCE_OF_TRUTH.md`, `docs/ai/CHANGE_POLICY.md`, `docs/ai/VERIFICATION_MATRIX.md`, `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`.
- `AGENTS.md` и `CLAUDE.md` это входные project instruction files; они должны вести к одному и тому же канону, а не расходиться с ним.
- `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md` = repo-visible read-only audit helper по writer/enforcer chains на `S1` и `S2`; использовать его для классификации master vs runtime перед server-side apply.

## Snapshot docs, но не live master
- `docs/ai/HANDOFF_2026-03-10.md` это snapshot и handoff на дату документа.
- `Boris-Detail-Schema.txt` это внешний audit artifact; сырой файл не переносить в repo.
- Эти документы нужны для аудита и поиска пробелов, но не заменяют live master.

## Repo-visible audited live facts
- Для live-фактов, подтвержденных read-only аудитами `2026-03-10` и `2026-03-11`, repo-visible source of truth = `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_OKDESK_PIPELINE.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_MODEL_ROUTING.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_PG_TUNNEL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BRIDGE_HA.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCKS_5_6_7_8.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCK_10_MONITORING.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCK_11_CRON_SKILLS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BLOCK_12_TOOLS_PLUGINS.md` и `docs/ai/DOCTOR_AND_SELFHEAL_AUDIT_2026-03-11.md`.
- Это относится к:
  - live placement/status `okdesk-pipeline`;
  - live model routing для internal cron и External Boris;
  - live prompt/memory paths и rules source of truth на S1;
  - live gateway/file path details и active health-check assumptions;
  - canonical public `bridge-ha` probe и live ingress ambiguity по `ops` domain;
  - live Boris PG data plane on S1, `pg-tunnel-s2.service` и sync contour `S2 -> S1`;
  - live doctor/monitor/watchdog/self-heal topology, risk classes и coverage profile;
  - live Boris tools/plugin entrypoints/helper-script contour;
  - live workflow statuses, явно проверенным в аудите;
  - S1 -> S2 alias drift vs network health.
- Эти audit docs не заменяют live master после даты аудита; для более нового состояния нужен новый server audit.

## okdesk-pipeline specifics
- Для `okdesk-pipeline` canonical placement на дату аудита = `S2`.
- Repo-visible live runtime source of truth по этому контуру = `S2 systemd unit + S2 cron calls + S2 listener :3200`, как это подтверждено в `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_OKDESK_PIPELINE.md`.
- `S1` по этому контуру не считать runtime host: аудит подтверждает только stale path/symlink без unit, process, `:3200` и cron calls.
- Competing runtime между `S1` и `S2` на дату аудита не подтвержден.
- Любые server-side правки placement, unit, cron или path для `okdesk-pipeline` требуют explicit approve.

## Model routing specifics
- Internal default-chain master на дату аудита = `model-strategy.json`; internal `openclaw.json` это effective runtime, а не единственный master.
- Internal cron declarative master = `model-strategy.json`; internal cron effective runtime = `jobs.json`, поле `payload.model`.
- External Boris chain master = external `fix-model-strategy.py`; external `openclaw.json` это effective runtime, а не master.
- `circuit-breaker-internal.py` по inspected code не считать source of truth для cron models: он мутирует `openclaw.json`, но не подтверждён как owner/master для `jobs.json`.
- Internal cron periodic sync для `jobs.json` подтверждён слабее, чем external fixer layer: startup sync подтверждён, но periodic enforcer для `jobs.json` не доказан так же явно.
- Для model routing это layered split с operational risk, а не доказанная runtime failure.
- Любые server-side изменения `model-strategy.json`, internal/external `openclaw.json`, `jobs.json`, internal/external fixer scripts, `circuit-breaker-internal.py`, `startup` scripts или `crontab` требуют explicit approve.

## Gateway / health-check specifics
- Для gateway/health-check контура repo-visible truth на дату аудита включает не только paths, но и locate-подтверждение active checks.
- На S2 active checks уже используют `/etc/caddy/Caddyfile`; stale path `/opt/app/Caddyfile` в active server-side checks не подтвержден.
- На S1 и S2 active checks уже используют `http` для local/remote `8443` health probe; stale TLS-assumption для local `8443` не подтвержден.
- Active checks не требуют symlink-type для `/etc/nginx/sites-enabled/*`; regular files на S1 не являются server-side defect сами по себе.
- Active checks не требуют host `:5001` для Docling; live expectation = container/docker-network health.
- Для этих gateway/health assumptions server-side fix не требуется; это docs drift, закрытый аудитом и read-only locate.
- Canonical public `bridge-ha` probe = `https://n8n.brendservice24.ru/bridge-ha/health`.
- `ops.brendservice24.ru/bridge-ha/*` не считать canonical route: `ops` domain активен, но path `/bridge-ha/*` на нём в live ingress не поддерживается.
- Public `bridge-ha` probe считать valid не только по `HTTP 200`, но и по `application/json` / JSON body.
- Если владелец захочет supported `/bridge-ha/*` route и на `ops` domain, это owner decision + approve-only ingress change.
- Для текущего состояния это docs drift / ingress ambiguity, а не подтверждённый live outage.

## Boris PG data plane on S1
- Current Boris PG mode on `S1` = `local`.
- Current Boris PG backend on `S1` = local `boris-emails-pg-1` на `172.18.0.1:15432`.
- `pg-tunnel-s2.service` не считать current live dependency: он конфликтует с local PG contour по `172.18.0.1:15432`.
- Live sync `S2 -> S1` сейчас опирается на `ssh/scp` scripts (`sync-pg-from-s2.sh`, `sync-executors-from-s2.sh`), а не на `pg-tunnel-s2.service`.
- `pg-tunnel-s2.service` сейчас классифицирован как legacy noise с operational risk, а не как runtime failure.
- По future server-side судьбе `pg-tunnel-s2.service` нужен owner decision: contingency contour ещё нужен или уже legacy.
- Любые server-side изменения unit, local PG contour, sync scripts или monitoring/self-healing вокруг этого контура требуют explicit approve.

## Prompt / memory specifics on S1
- Для live правил на S1 repo-visible source of truth = `/data/.openclaw/workspace/memory/RULES.md`, как это подтверждено в `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`.
- `/data/.openclaw/memory` в live не является rules path; это storage/DB path.
- `CLAUDE.md` не является master-источником правил; он выступает как operational context file и указывает на `workspace/memory/RULES.md`.
- Отсутствие `.openclaw/SOUL.md` на дату аудита зафиксировано как docs drift, а не как доказанный runtime failure.
- Любые server-side изменения prompt/memory layout или loader-paths требуют explicit approve.

## Doctor / monitor / self-heal control plane
- Repo-visible source of truth для doctor/self-heal contour on `2026-03-11` = `docs/ai/DOCTOR_AND_SELFHEAL_AUDIT_2026-03-11.md`.
- Boris production control plane считать custom multi-layer stack:
  - host `crontab`
  - systemd services/timers
  - custom doctors/watchdogs/monitors on `S1` and `S2`
  - related state/baseline/rollback layers
- Block 10 read-only result on `2026-03-11`:
  - core monitoring contour is alive on both servers
  - active outage is not confirmed
  - current issue class = working control plane with legacy monitoring drift on `S1`
- Official OpenClaw `doctor / cron / heartbeat` docs описывают Gateway primitives, но не описывают текущий Boris production control plane целиком.
- Repo-visible classification for live contours:
  - `safe observer` = read-only observer/alert contour
  - `conditional repair` = repair only under narrow trigger/cooldown
  - `active self-heal` = regular autonomous repair loop with bounded scope
  - `dangerous auto-repair` = contour that mutates runtime/config/workflows or widens blast radius
- Dangerous contours currently include:
  - `watchdog-meta`
  - `service-guard`
  - `n8n-watchdog`
  - `n8n-doctor`
  - `monitor-locks.sh`
  - `workspace-validator`
  - `promise-watchdog`
- Coverage profile on audit date:
  - strong infrastructure coverage
  - partial BS24 business-liveness coverage
  - weak semantic business correctness coverage
- `monitor-safe.service` on both servers is `disabled/inactive`; stale `heartbeat-safe.json` by itself is not a standalone incident.
- Stale monitored contours currently visible in `S1` monitoring-space:
  - `pg-tunnel-s2`
  - `okdesk-pipeline`
- Для planning нельзя считать official OpenClaw doctor единственным control plane и нельзя повышать dangerous auto-repair contours до "safe default" без отдельного owner decision.
- Любое расширение auto-repair scope/rights внутри этого control plane требует owner decision и explicit approve.

## Cron / jobs / skills specifics
- Internal cron model layer on audit date = `bridge/claude-opus-4-6`.
- `jobs.json` on `S1` contains `13` enabled OpenClaw jobs, and all enabled jobs use `bridge/claude-opus-4-6`.
- `jobs.json` is schedule/config layer and effective cron runtime config, but not runtime truth by itself; runtime result state must still be verified separately.
- `Дайджест развития — Канал мастеров` on audit date is `enabled`, has `nextRunAtMs`, keeps `lastRunAtMs=null` and `consecutiveErrors=0`; this is `not yet run`, not broken cron.
- `S1` stale timers `boris-email-router.timer` and `chief-doctor.timer` are already safe-disabled and should not be mixed with OpenClaw cron health.
- Skills workspace structure on audit date:
  - `24` top-level dirs
  - `22` real skills
  - service dirs `scripts`, `snippets`
- Old snapshot name `parse-attachment` is obsolete; live skill entrypoint is `parse-file`.
- Critical live entrypoints confirmed present:
  - `email-handler`
  - `okdesk`
  - `find-executor`
  - `parse-file`
  - `tender-specialist`
- Skills/tooling layer is repo/runtime orchestration, not live business master by itself.
- Raw session trace sampling and plugin presence confirm live tooling availability, but they do not alone prove business-critical active contour.

## Boris tools / plugin entrypoints / helper-script specifics
- Repo-visible read-only result on `2026-03-11`:
  - live tooling contour is confirmed
  - sampled `S1` main-agent traces directly confirm real `exec` and `process` tool events
  - `exec` remains the main bridge from Boris to server-side helper scripts
  - `process` is the confirmed follow-up layer for long-running `exec`
- Live plugin entrypoints confirmed present:
  - `/data/route-command/openclaw.plugin.json`
  - `/data/callback-forward/openclaw.plugin.json`
- Sampled helper-path evidence in `exec` calls includes:
  - `/data/scripts/okdesk-comment-poller.py`
  - `/data/.openclaw/workspace/scripts/okdesk-supabase-sync.mjs`
- This contour is currently classified as:
  - `OK with WARN`
  - not live outage
  - mostly docs / mental-model / inspection-method drift
- Live tool inventory must be proven by:
  - traces
  - plugin entrypoints
  - helper-path evidence
- Old schema/snapshot assumptions alone do not prove live tool inventory.
- Plugin presence alone does not prove business-critical active contour.
- Any server-side changes to plugin files, tool-routing entrypoints or helper scripts require explicit approve.

## Live truth вне repo
- Live server-side configs, runtime state, workflow state, systemd, nginx/Caddy, database schema, secrets и прочий server-side truth проверяются только вне repo.
- Если факт относится к live-системе и не подтвержден каноном repo, требуется `SERVER_AUDIT_REQUIRED`.

## Writer / enforcer discipline
- Нельзя править runtime/derived файл, если его затем перезапишет startup, cron, doctor, monitor, self-heal, sync или другой writer/enforcer.
- Doctor / monitor / self-heal contours сами могут быть writers/restorers:
  - `workspace-validator`
  - `service-guard`
  - `watchdog-meta`
  - `memory-watchdog`
  - `promise-watchdog`
  - `n8n-watchdog`
  - `n8n-doctor`
- Если контур живёт через layered sync, менять нужно master-слой, а не derived/runtime-слой.
- Если apply всё же нужен в runtime, сначала требуется одно из трёх:
  - обновить master;
  - обновить writer/enforcer layer;
  - отдельно и осознанно отключить enforcer по approved plan.
- Для критичных target files writer chain нужно зафиксировать до apply:
  - `openclaw.json`;
  - `jobs.json`;
  - model-strategy related files;
  - prompt/memory paths;
  - monitored config files;
  - systemd/runtime configs;
  - sync-derived data copies.

## Перед любой правкой определить
- master source;
- generated/runtime files;
- active/potential writers/enforcers;
- trigger writers;
- что нельзя править напрямую;
- что перезаписывается при рестарте, bootstrap, sync или patch;
- можно ли доказать факт по repo docs или нужен server audit.

## Правило конфликта
- Если канон и snapshot docs расходятся, не угадывать.
- Не переписывать snapshot-документы в live truth без server-side verification.
- Если dated audit docs и snapshot docs расходятся по уже проверенному live-факту, считать snapshot drift документально подтвержденным и отражать это только в каноне repo.
