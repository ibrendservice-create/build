# SERVER AUDIT ADDENDUM 2026-03-10 MODEL ROUTING

## Что проверено

- Read-only проверены live файлы на `S1`:
  - `model-strategy.json`
  - internal `openclaw.json`
  - `jobs.json`
  - external `openclaw.json`
- Read-only проверены связанные patcher/loader references:
  - internal `fix-model-strategy.py`
  - `circuit-breaker-internal.py`
  - `startup-cleanup.sh`
  - external `fix-model-strategy.py`
  - `startup-external.sh`
  - root `crontab`
- Проверялись только model-related поля через `jq` и точечные `rg`/`sed`; секреты не читались.

## Live routing map

- Internal default-chain сейчас: `bridge/claude-sonnet-4-6` с fallback-цепочкой `openai-codex/gpt-5.3-codex -> openai-bridge2/gpt-5 -> openai/gpt-5 -> ...`; это совпадает между `model-strategy.json` и internal `openclaw.json`.
- Internal subagents live: `bridge/claude-opus-4-6`; это совпадает между `model-strategy.json` и internal `openclaw.json`.
- Internal cron live: все 13 jobs в `jobs.json` явно сидят на `bridge/claude-opus-4-6`.
- В `model-strategy.json` для cron тоже зафиксировано `cron_default_model=bridge/claude-opus-4-6` и `cron_models` для `digest`, `email`, `headhunter`, `monitor`, `commitment`, `okdesk`, `gdrive`.
- External Boris live chain в external `openclaw.json`: primary `anthropic/claude-haiku-4-5`, fallback `openai/gpt-5`.
- External `fix-model-strategy.py` подтверждает ту же цепочку как preferred state и умеет swap на `openai/gpt-5` primary по health circuit breaker.

## Master / source of truth by layer

- Internal default-chain master: `S1 /var/lib/apps-data/openclaw/data/model-strategy.json`.
- Internal default-chain effective runtime file: `S1 /var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`.
- Это подтверждается тем, что internal `fix-model-strategy.py` прямо читает `STRATEGY_FILE=/data/model-strategy.json` и пишет `CONFIG=/data/.openclaw/openclaw.json`.
- Internal cron model override declarative master: тот же `model-strategy.json`, поля `cron_default_model` и `cron_models`.
- Internal cron effective runtime file: `S1 /var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json`, поле `payload.model`.
- Internal `fix-model-strategy.py` имеет отдельный блок `Fix cron/jobs.json`, который переписывает `jobs.json` из strategy.
- External Boris chain master: `S1 /var/lib/apps-data/openclaw-external/data/fix-model-strategy.py`, а не external `openclaw.json`.
- External Boris effective runtime file: `S1 /var/lib/apps-data/openclaw-external/data/.openclaw/openclaw.json`.
- Это подтверждается тем, что external `fix-model-strategy.py` хранит `PREFERRED_PRIMARY` / `PREFERRED_FALLBACKS` / `SWAPPED_*` как code constants и переписывает `OC_CFG=/data/.openclaw/openclaw.json`.
- Итого одного master на весь routing contour нет; source of truth split по слоям.

## Где split допустим, а где риск

- Допустимый split: internal `model-strategy.json -> openclaw.json` для default-chain выглядит намеренной архитектурой.
- Допустимый split: external `fix-model-strategy.py -> external openclaw.json` тоже намеренный, потому что startup и cron явно запускают fixer.
- Риск: internal cron override живёт отдельным слоем в `jobs.json`, а не внутри same-file master.
- Риск: periodic enforcer для internal `jobs.json` не подтверждён так же явно, как для external.
- Live `crontab` на `S1` подтвердил только:
  - `docker exec openclaw-ext-openclaw-1 python3 /data/fix-model-strategy.py`
  - `docker exec openclaw-kbxr-openclaw-1 python3 /data/circuit-breaker-internal.py`
- Internal `startup-cleanup.sh` действительно запускает `fix-model-strategy.py` post-K, но это подтверждает startup sync, а не явный periodic sync.
- Риск: `circuit-breaker-internal.py` по коду мутирует `openclaw.json`, но в проверенном коде не трогает `jobs.json`, хотя header говорит про swap crons тоже.
- Риск: external `openclaw.json` легко принять за master, хотя его реально переписывает external fixer code.

## Drift vs docs/handoff

- Точно подтверждён drift vs `HANDOFF_2026-03-10.md`: internal crons не `claude-sonnet-4-6`, а `bridge/claude-opus-4-6`.
- Точно подтверждён drift vs `HANDOFF_2026-03-10.md`: External Boris не `gpt-4o/codex`, а `claude-haiku-4-5 -> gpt-5`.
- Точно подтверждён drift vs handoff source-of-truth table: `openclaw.json` и `jobs.json` нельзя считать единственным master для model routing.
- Current canon в repo уже правильно отражает live значения моделей для internal cron и External Boris.
- Но current canon ещё не раскладывает достаточно явно source-of-truth layering:
  - internal cron = `strategy -> jobs` split
  - external chain = `fixer code -> openclaw` split

## Что можно исправить только в repo

- Уточнить канон и bug register так, чтобы явно фиксировать source of truth по слоям:
  - internal default-chain master = `model-strategy.json`
  - internal cron declarative master = `model-strategy.json`, effective runtime = `jobs.json`
  - external chain master = external `fix-model-strategy.py`, effective runtime = external `openclaw.json`
- Отдельно зафиксировать, что internal periodic sync для `jobs.json` не подтверждён так же явно, как external cron enforcer.
- Отдельно зафиксировать, что `circuit-breaker-internal.py` по inspected code не является source of truth для cron models.

## Что требует approve

- Любые изменения `model-strategy.json`, internal `openclaw.json`, `jobs.json`, external `openclaw.json`.
- Любые изменения internal/external `fix-model-strategy.py`, `circuit-breaker-internal.py`, `startup-cleanup.sh`, `startup-external.sh`, `crontab`.
- Любые live changes model routing, fallback-chain, bridge failover logic или restarts.

## Вердикт

- `WARN`
- Live routing map подтверждён.
- Архитектура не `single-master`; это layered split.
- Для internal default-chain split выглядит допустимым.
- Для internal cron и external Boris split создаёт operational risk, если runtime-файлы принять за master или если игнорировать fixer layer.
- Главные уже подтверждённые drift-пункты: internal cron model, External Boris chain и неполное описание source-of-truth layering в snapshot docs.
