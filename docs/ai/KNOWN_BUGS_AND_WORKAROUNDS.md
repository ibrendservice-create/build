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

### okdesk-pipeline deployment truth mismatch
- симптом: snapshot docs расходятся с live-аудитом по расположению и состоянию деплоя `okdesk-pipeline`.
- где проявляется: deployment planning, audit, rollout decisions.
- workaround: для repo planning считать audit-backed live-фактом `okdesk-pipeline active на S2`; для нового live-подтверждения позже даты аудита требовать `SERVER_AUDIT_REQUIRED`.
- что нельзя делать: деплоить, перезапускать service или менять `DRY_RUN` только на основании snapshot docs.
- статус: active.

### Model routing documentation mismatch
- симптом: snapshot docs расходятся с live-аудитом по model routing для internal cron и External Boris.
- где проявляется: безопасное планирование изменений моделей.
- workaround: для repo planning использовать audit-backed facts: internal cron=`bridge/claude-opus-4-6`, external=`anthropic/claude-haiku-4-5 -> openai/gpt-5`; для более нового live-состояния требовать `SERVER_AUDIT_REQUIRED`.
- что нельзя делать: менять model routing по одному snapshot-документу.
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
