# OPERATING CONSENSUS

## Purpose
Этот файл задает общий канон памяти и общий safety contour для Claude и Codex внутри этого репозитория.

## Scope
- Только repo docs и project instruction files.
- Runtime, server-side truth, live workflows и secrets находятся вне этого repo.
- `docs/ai/HANDOFF_2026-03-10.md` и внешний `Boris-Detail-Schema.txt` используются для аудита, а не как live master.
- `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_OKDESK_PIPELINE.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_MODEL_ROUTING.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_CRON_TIMERS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_PG_TUNNEL.md` и `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BRIDGE_HA.md` это dated audit docs: они фиксируют проверенные live-факты на дату аудита, но не заменяют live master после этой даты.

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
13. `docs/ai/HANDOFF_2026-03-10.md`
14. `Boris-Detail-Schema.txt` только если файл явно дан для аудита; сырой файл не копировать в repo.

## Document priority
- `AGENTS.md` и `CLAUDE.md` это agent entry points; они должны ссылаться на один и тот же канон и не расходиться по правилам проекта.
- Канон repo: этот файл плюс `docs/ai/PROJECT_MEMORY.md`, `docs/ai/SOURCE_OF_TRUTH.md`, `docs/ai/CHANGE_POLICY.md`, `docs/ai/VERIFICATION_MATRIX.md`, `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`.
- Dated audit docs: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_OKDESK_PIPELINE.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_MODEL_ROUTING.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_CRON_TIMERS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_PG_TUNNEL.md` и `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BRIDGE_HA.md`.
- Snapshot docs: `docs/ai/HANDOFF_2026-03-10.md` и внешний `Boris-Detail-Schema.txt`.
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
- сначала нижний слой, потом верхний;
- только минимальный change set;
- всегда иметь rollback;
- всегда делать post-change verification;
- не читать и не выводить секреты.

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

## Remaining unresolved contradictions
- Эти audit-backed facts корректны только на дату аудита `2026-03-10`; если задача зависит от их текущего live-состояния позже, требуется `SERVER_AUDIT_REQUIRED`.
- Все неаудированные live-факты из `HANDOFF` и внешней схемы по-прежнему нельзя повышать до master без отдельной проверки.
