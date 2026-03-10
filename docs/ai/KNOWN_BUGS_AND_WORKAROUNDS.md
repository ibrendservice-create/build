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
- симптом: `HANDOFF` и внешняя схема расходятся по расположению и состоянию деплоя `okdesk-pipeline`.
- где проявляется: deployment planning, audit, rollout decisions.
- workaround: любой live-факт по pipeline помечать `SERVER_AUDIT_REQUIRED`.
- что нельзя делать: деплоить, перезапускать service или менять `DRY_RUN` только на основании repo docs.
- статус: active.

### Model routing documentation mismatch
- симптом: `HANDOFF` и внешняя схема расходятся по model routing для cron/subagents и External Boris.
- где проявляется: безопасное планирование изменений моделей.
- workaround: считать конфликт неразрешенным до server-side verification.
- что нельзя делать: менять model routing по одному snapshot-документу.
- статус: active.

### Workflow status drift in docs
- симптом: snapshot docs расходятся по статусам части n8n workflows.
- где проявляется: планирование изменений и post-check для workflow контуров.
- workaround: сверять live state только вне repo; в repo помечать `SERVER_AUDIT_REQUIRED`.
- что нельзя делать: активировать, деактивировать или считать workflow inactive/active только по документации.
- статус: active.

### Bridge instability under load
- симптом: Bridge может давать `fetch failed` или не-JSON ответ под нагрузкой.
- где проявляется: AI-вызовы и pipeline/enrichment цепочки.
- workaround: планировать graceful degradation и пропуск stage, если это уже предусмотрено live-системой.
- что нельзя делать: считать Bridge стабильным на 100% или менять fallback по repo docs без live verification.
- статус: active.
