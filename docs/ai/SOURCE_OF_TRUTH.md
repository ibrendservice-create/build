# SOURCE OF TRUTH

## Базовое правило
- Никогда не считать runtime/generated файл источником истины, если есть master-конфиг, patcher, generator или sync pipeline.

## Канон внутри repo
- Для project instructions и planning source of truth в repo: `docs/ai/OPERATING_CONSENSUS.md`, `docs/ai/PROJECT_MEMORY.md`, `docs/ai/SOURCE_OF_TRUTH.md`, `docs/ai/CHANGE_POLICY.md`, `docs/ai/VERIFICATION_MATRIX.md`, `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`.
- `AGENTS.md` и `CLAUDE.md` это входные project instruction files; они должны вести к одному и тому же канону, а не расходиться с ним.

## Snapshot docs, но не live master
- `docs/ai/HANDOFF_2026-03-10.md` это snapshot и handoff на дату документа.
- `Boris-Detail-Schema.txt` это внешний audit artifact; сырой файл не переносить в repo.
- Эти документы нужны для аудита и поиска пробелов, но не заменяют live master.

## Repo-visible audited live facts
- Для live-фактов, подтвержденных read-only аудитами `2026-03-10` и `2026-03-11`, repo-visible source of truth = `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_OKDESK_PIPELINE.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_MODEL_ROUTING.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_PG_TUNNEL.md` и `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BRIDGE_HA.md`.
- Это относится к:
  - live placement/status `okdesk-pipeline`;
  - live model routing для internal cron и External Boris;
  - live prompt/memory paths и rules source of truth на S1;
  - live gateway/file path details и active health-check assumptions;
  - canonical public `bridge-ha` probe и live ingress ambiguity по `ops` domain;
  - live Boris PG data plane on S1, `pg-tunnel-s2.service` и sync contour `S2 -> S1`;
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

## Live truth вне repo
- Live server-side configs, runtime state, workflow state, systemd, nginx/Caddy, database schema, secrets и прочий server-side truth проверяются только вне repo.
- Если факт относится к live-системе и не подтвержден каноном repo, требуется `SERVER_AUDIT_REQUIRED`.

## Перед любой правкой определить
- master source;
- generated/runtime files;
- что нельзя править напрямую;
- что перезаписывается при рестарте, bootstrap, sync или patch;
- можно ли доказать факт по repo docs или нужен server audit.

## Правило конфликта
- Если канон и snapshot docs расходятся, не угадывать.
- Не переписывать snapshot-документы в live truth без server-side verification.
- Если dated audit docs и snapshot docs расходятся по уже проверенному live-факту, считать snapshot drift документально подтвержденным и отражать это только в каноне repo.
