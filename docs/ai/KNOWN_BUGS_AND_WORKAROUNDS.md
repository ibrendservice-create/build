# KNOWN BUGS AND WORKAROUNDS

## Формат записи
Для каждого бага фиксировать:
- симптом;
- где проявляется;
- workaround;
- что нельзя делать;
- статус: active / mitigated / fixed.

## Текущий repo-visible набор
Ниже только те баги и противоречия, которые подтверждаются текущими repo docs и внешней схеме аудита.
Если речь идет о live-состоянии серверов, workflows или runtime, перед действием требуется `SERVER_AUDIT_REQUIRED`.

### OpenClaw config overwrite on startup
- симптом: `openclaw.json` может быть перезаписан при старте контейнера.
- где проявляется: OpenClaw runtime / config protection chain.
- workaround: считать master отдельно от runtime; опираться на patcher chain и post-change verification.
- что нельзя делать: редактировать live runtime config напрямую и считать его стабильным после restart.
- статус: mitigated.

### Runtime direct-edit overwrite by writers/enforcers
- симптом: ручная правка runtime/derived файла исчезает после startup, cron, doctor, monitor, self-heal или sync.
- где проявляется: `openclaw.json`, `jobs.json`, external `openclaw.json`, prompt/memory files, monitored config files, okdesk derived copies и другие layered contours.
- workaround: перед apply сначала найти master, derived/runtime, writers/enforcers и их trigger chain; если contour layered, менять master-слой; если runtime apply неизбежен, сначала обновить master или writer layer, либо по approved plan отключить enforcer.
- что нельзя делать: править runtime/derived файл в изоляции, если следующий writer/enforcer всё равно его перепишет.
- статус: active.

### okdesk-pipeline deployment truth mismatch
- симптом: snapshot docs расходились с live-аудитом по placement и состоянию деплоя `okdesk-pipeline`.
- где проявляется: deployment planning, audit, rollout decisions.
- workaround: для repo planning считать canonical placement = `S2`; live runtime source of truth = `S2 unit + S2 cron calls + S2 :3200`; `S1` трактовать как stale path/symlink, а не runtime host; для более нового live-состояния позже даты аудита требовать `SERVER_AUDIT_REQUIRED`.
- что нельзя делать: считать `S1` runtime host, деплоить, перезапускать service, переносить placement или менять `DRY_RUN` только на основании snapshot docs.
- статус: mitigated.

### Model routing documentation mismatch
- симптом: snapshot docs расходятся с live-аудитом по model routing для internal cron и External Boris, а source of truth по routing split по слоям.
- где проявляется: безопасное планирование изменений моделей.
- workaround: для repo planning использовать layered audit-backed facts: internal default-chain master=`model-strategy.json`, internal cron declarative master=`model-strategy.json` и effective runtime=`jobs.json`, external chain master=external `fix-model-strategy.py` и effective runtime=external `openclaw.json`; internal cron=`bridge/claude-opus-4-6`, external=`anthropic/claude-haiku-4-5 -> openai/gpt-5`; для более нового live-состояния требовать `SERVER_AUDIT_REQUIRED`.
- что нельзя делать: считать internal `openclaw.json`, `jobs.json` или external `openclaw.json` единственным master, считать `circuit-breaker-internal.py` source of truth для cron models или менять routing по одному snapshot-документу.
- статус: active.

### Workflow status drift in docs
- симптом: snapshot docs расходятся с live-аудитом по статусам части n8n workflows.
- где проявляется: планирование изменений и post-check для workflow контуров.
- workaround: в repo учитывать audit-backed status drift по exact workflow id: WF3/WF8 relay/WF10/Telegram Logger/WF Watchdog=`active`, WF11/WF8 Watchdog=`inactive`, Email Attachment Parser=`inactive`; reconciliation делать по workflow id, а не только по названию; для более нового live state требовать `SERVER_AUDIT_REQUIRED`.
- что нельзя делать: активировать, деактивировать или считать workflow inactive/active только по документации.
- статус: active.

### Bridge instability under load
- симптом: Bridge может давать `fetch failed` или не-JSON ответ под нагрузкой.
- где проявляется: AI-вызовы и pipeline/enrichment цепочки.
- workaround: планировать graceful degradation и пропуск stage, если это уже предусмотрено live-системой.
- что нельзя делать: считать Bridge стабильным на 100% или менять fallback по repo docs без live verification.
- статус: active.

### Prompt and memory path drift
- симптом: snapshot docs описывают `.openclaw/SOUL.md` и `.openclaw/memory/RULES.md`, но live-аудит подтверждает другой rules path и отсутствие `SOUL.md`.
- где проявляется: prompt/bootstrap planning и memory-related changes.
- workaround: для repo planning считать live source of truth на S1 = `/data/.openclaw/workspace/memory/RULES.md`; `/data/.openclaw/memory` трактовать как storage/DB path; `CLAUDE.md` считать operational context file, а не master-источником правил.
- что нельзя делать: восстанавливать `.openclaw/SOUL.md`, переносить `RULES.md` в `.openclaw/memory` или менять prompt/memory layout по snapshot docs без новой live-проверки и approve.
- статус: active.

### Gateway and file path drift
- симптом: snapshot docs раньше расходились с live по `Caddyfile`, типу файлов в `sites-enabled` и local `8443` health probe.
- где проявляется: gateway audit, reverse proxy post-check, config path assumptions.
- workaround: использовать audited live facts и locate-confirmed active checks: `Caddyfile=/etc/caddy/Caddyfile`, local `8443` probe=`http`, `sites-enabled` regular files допустимы; server-side fix для этих assumptions не нужен.
- что нельзя делать: предполагать `/opt/app/Caddyfile`, symlink в `sites-enabled` или local TLS на `8443` без проверки.
- статус: mitigated.

### Public bridge-ha URL ambiguity
- симптом: `https://n8n.brendservice24.ru/bridge-ha/health` возвращает live JSON health, а `https://ops.brendservice24.ru/bridge-ha/health` возвращает `200 text/html`, хотя snapshot/topology docs могут визуально ассоциировать `bridge-ha` с `ops` domain.
- где проявляется: public health probes, ingress runbooks, gateway audit.
- workaround: считать canonical public probe только `https://n8n.brendservice24.ru/bridge-ha/health`; валидировать не только `HTTP 200`, но и `application/json` / JSON body; `ops` domain считать active domain без supported path `/bridge-ha/*`, пока владелец явно не решит иначе.
- что нельзя делать: считать `ops.brendservice24.ru/bridge-ha/*` canonical route, принимать `200 text/html` за valid bridge health или менять ingress по snapshot docs без нового live-аудита и approve.
- статус: mitigated.

### S1 Boris PG tunnel legacy noise
- симптом: на `S1` остаётся `pg-tunnel-s2.service` в состоянии `failed`, хотя current Boris PG mode = `local`, а port `172.18.0.1:15432` уже занят local `boris-emails-pg-1`.
- где проявляется: PostgreSQL data plane planning on `S1`, systemd/monitoring noise, server audits.
- workaround: считать current Boris PG contour на `S1` локальным (`boris-emails-pg-1`), не считать `pg-tunnel-s2.service` текущей live dependency; live sync `S2 -> S1` трактовать как `ssh/scp`-based via `sync-pg-from-s2.sh` и `sync-executors-from-s2.sh`; перед любым apply сначала получить owner decision: contingency contour ещё нужен или уже legacy.
- что нельзя делать: "чинить" tunnel как будто это current live data plane, освобождать `172.18.0.1:15432` без понимания local PG contour или менять monitoring/self-healing вокруг этого unit без нового live-аудита и approve.
- статус: active.

### Docling host-port assumption drift
- симптом: docs могли предполагать host `:5001`, но live-аудит и locate подтверждают только container/docker-network expectation для Docling.
- где проявляется: integration checks и OCR troubleshooting.
- workaround: считать host `:5001` необязательным; опираться на Docker-network health и active checks, которые не требуют host-port.
- что нельзя делать: объявлять интеграцию сломанной только потому, что `ss` на хосте не показывает `:5001`.
- статус: mitigated.

### S1 to S2 alias drift
- симптом: `ssh s2` на S1 не работает, хотя маршрут, TCP и SSH по IP исправны.
- где проявляется: network audit, runbooks, cross-server scripts.
- workaround: отличать alias problem от network problem; использовать `root@72.56.98.52` как каноническую read-only проверку связности.
- что нельзя делать: объявлять network `FAIL`, если сломан только alias `s2`.
- статус: active.

### Cron / timer housekeeping debt
- симптом: `boris-email-router.timer` и `chief-doctor.timer` на `S1` = `enabled + active(elapsed) + no next trigger`; при этом `Дайджест развития — Канал мастеров` в `jobs.json` имеет `lastStatus=null`, но `enabled=true` и заданный `nextRunAtMs`.
- где проявляется: housekeeping of background automation on `S1`, distinction between stale timers and first-run-pending cron jobs.
- workaround: считать timers отдельным operational-risk contour и не смешивать его с `jobs.json`; для repo planning фиксировать, что оба timers требуют owner decision, а `Дайджест развития — Канал мастеров` сейчас трактуется как `not yet run`, не broken; на `S2` этот housekeeping contour crontab-based, а не timer-based.
- что нельзя делать: автоматически считать weekly digest broken, а также автоматически чинить, отключать или удалять timers без owner decision и approve.
- статус: active.

### Tender specialist skill boundary and tool drift
- симптом: server-side Boris skill `tender-specialist` на `S1` уже построен как `skill + script`, но в `SKILL.md` есть узкий tool/boundary drift: ссылка на несуществующий `parse-attachment`, слишком широкая формулировка про "видишь все сообщения пользователей и сам решаешь", и нет явной do-not-touch boundary для `routing/workflows/bridge/monitoring/model files/jobs`.
- где проявляется: Boris tender contour на `S1`, чат ТЕНДЕР, orchestration layer поверх `tender-analysis-helper.py`.
- workaround: до apply считать contour именно `skill + script`, а не pure skill; не расширять scope за пределы `tender-specialist/SKILL.md`; планировать patch только как low-risk server-side change в рабочее окно; соседние contours (`scripts`, `jobs.json`, model files, workflows, bridge, monitoring`) не трогать.
- что нельзя делать: чинить это через `jobs.json`, model files, workflow routing, bridge config или monitoring/self-healing; превращать patch в refactor helper scripts без отдельной задачи; делать apply вне `low-risk change window`, если нет emergency.
- статус: active.
