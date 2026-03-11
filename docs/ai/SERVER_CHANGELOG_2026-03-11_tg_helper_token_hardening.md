# SERVER CHANGELOG 2026-03-11 TG HELPER TOKEN HARDENING

## Слой

- Shared Telegram helper token-resolution contour on `S1`.

## Source of truth

- `/var/lib/apps-data/openclaw/data/scripts/tg-send-helper.py`
- `/var/lib/apps-data/openclaw/data/scripts/boris-health-check.py`

## Что было не так

- `tg-send-helper.py` имел split token contract.
- Host env-file `/etc/apps/secrets/openclaw.env` использовал key `TG_BOT_TOKEN`.
- Helper file parser в `/etc/apps/secrets/openclaw.env` искал только `TELEGRAM_BOT_TOKEN`.
- File read не был safe и мог ломать lookup contour до полного fallback chain.
- Historical failure class уже была подтверждена как:
  - `TELEGRAM_BOT_TOKEN not found`

## Что изменили

- В `tg-send-helper.py` зафиксирован deterministic lookup order:
  - env `TELEGRAM_BOT_TOKEN`
  - env `TG_BOT_TOKEN`
  - file `/etc/apps/secrets/openclaw.env` key `TELEGRAM_BOT_TOKEN`
  - file `/etc/apps/secrets/openclaw.env` key `TG_BOT_TOKEN`
- File read сделан safe через `OSError` fallback.
- Miss-error оставлен source-level only, без вывода token value.
- CLI не менялся.
- Canonical stdin behavior не менялся.
- Thread behavior не менялся.
- `boris-health-check.py` переведён на boolean helper-resolution check через `resolve_helper_token(...)`.

## Что не меняли

- jobs
- model routing
- bridge
- monitoring
- runtime config
- digest payloads

## Где backup

- `/root/tg-helper-token-hardening-20260311T173118Z`

## Pre-check

Подтверждено до apply:

- current helper sha256 = `db8c585d9b1be0b1cd5fdbe965c15a847a15712cc7e7bfbe54555dee24bad9f7`
- current lookup chain before apply:
  - file `/etc/apps/secrets/openclaw.env`
  - only key `TELEGRAM_BOT_TOKEN` in file
  - then env fallback `TELEGRAM_BOT_TOKEN -> TG_BOT_TOKEN`
- `HOST_HELPER_GET_TOKEN=no`
- `CT_HELPER_GET_TOKEN=yes`
- host env-file key name = `TG_BOT_TOKEN`
- host-file token equals container-env token = `yes`
- morning/evening digest hashes были зафиксированы до apply:
  - morning delivery = `74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b`
  - morning message = `5d1221cf8582f8f6fccb475e749ccd3d709ffe3228993a33acc64554fbeeba1b`
  - evening delivery = `74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b`
  - evening message = `db1fdf6af6e946d79d2da956bd3d341f2afad407587d6bc5d4956b9fa2a85475`
- scope не затрагивал:
  - `jobs.json`
  - `model-strategy.json`
  - `fix-model-strategy.py`
  - bridge
  - monitoring
  - runtime config

## Post-check

Подтверждено после apply:

- new helper sha256 = `fdb85e1a3f83805cd3a1e348e37973a0086b6302f2bc16d5725c9f479075d5d1`
- `HOST_HELPER_GET_TOKEN=yes`
- `CT_HELPER_GET_TOKEN=yes`
- `RUNUSER_HELPER_GET_TOKEN=yes`
- helper caller inventory unchanged
- morning/evening digest hashes unchanged exactly
- `payload_job_drift=[]`
- `py_compile` passed for both files
- `boris-health-check.py` now uses helper-resolution boolean check without token output

## Rollback required or not

- `Rollback required` = `no`

## Итог

- `successful`
- jobs/model routing/bridge/monitoring/runtime config/digest payloads не менялись
