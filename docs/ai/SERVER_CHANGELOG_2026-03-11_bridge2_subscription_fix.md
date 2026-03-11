# SERVER CHANGELOG 2026-03-11 BRIDGE2 SUBSCRIPTION FIX

## Слой

- Internal Boris model routing -> Bridge 2 subscription contour на `S1`.

## Source of truth

- `/var/lib/apps-data/openclaw/data/model-strategy.json`
- sync через internal `fix-model-strategy.py`
- runtime:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
  - `/var/lib/apps-data/openclaw/data/.openclaw/agents/main/agent/models.json`

## Что было не так

- Boris Bridge 2 contour ходил в `POST /openai/chat/completions` и ловил `HTTP 404`.
- Runtime advertising для Bridge 2 был неполным: в master/runtime был только `openai-bridge2/gpt-5`.
- Exact unsupported id `gpt-5.4-codex` отсутствует в live-supported contour и не должен был рекламироваться.

## Что изменили

- В `model-strategy.json` исправили `providers.openai-bridge2.baseUrl`:
  - с `http://172.18.0.1:8443/openai`
  - на `http://172.18.0.1:8443/openai/v1`
- В `providers.openai-bridge2.models` оставили и/или добавили только live-supported ids:
  - `gpt-5`
  - `gpt-5.2`
  - `gpt-5.3-codex`
  - `gpt-5.4`
- В `model_aliases` оставили и/или добавили только Boris-facing aliases:
  - `openai-bridge2/gpt-5`
  - `openai-bridge2/gpt-5.2`
  - `openai-bridge2/gpt-5.3-codex`
  - `openai-bridge2/gpt-5.4`
- Internal `fix-model-strategy.py` прогнан один раз для sync runtime.
- Runtime `openclaw.json` и `agents/main/agent/models.json` синхронизировались.
- `jobs.json` по enabled models не менялся.

## Что не меняли

- `jobs.json` вручную
- `circuit-breaker-internal.py`
- `startup-cleanup.sh`
- `nginx`
- `openai-bridge.service` config
- auth
- workflows
- monitoring
- external contour

## Где backup

- `/root/bridge2-apply-20260311T133425Z`
- Внутри:
  - `model-strategy.json.bak`
  - `openclaw.json.bak`
  - `models.json.bak`
  - `jobs.json.bak`
  - `precheck.txt`

## Pre-check

Подтверждено до apply:

- `openai-bridge.service` = `active`
- до apply master/runtime `openai-bridge2.baseUrl` был `http://172.18.0.1:8443/openai`
- в master/runtime был только `openai-bridge2/gpt-5`
- enabled cron jobs оставались на `bridge/claude-opus-4-6`
- подтверждённые `404` в `bridge-access.log`:
  - `2026-03-11 09:58:02 UTC`
  - `2026-03-11 10:01:34 UTC`
  - `2026-03-11 10:01:44 UTC`
  - path = `POST /openai/chat/completions`

## Post-check

Подтверждено после apply:

- `openai-bridge.service` = `active`
- runtime `openclaw.json` содержит `openai-bridge2.baseUrl = http://172.18.0.1:8443/openai/v1`
- runtime alias keys есть для:
  - `openai-bridge2/gpt-5`
  - `openai-bridge2/gpt-5.2`
  - `openai-bridge2/gpt-5.3-codex`
  - `openai-bridge2/gpt-5.4`
- `jobs.json` по enabled models остался `bridge/claude-opus-4-6`
- после apply в `bridge-access.log` идут только `POST /openai/v1/chat/completions`
- новых `POST /openai/chat/completions` после apply нет
- live probes:
  - `gpt-5 -> 200, source=codex_subscription`
  - `gpt-5.2 -> 200, source=codex_subscription`
  - `gpt-5.3-codex -> 200, source=codex_subscription`
  - `gpt-5.4 -> 200, source=codex_subscription`
- control probe:
  - `gpt-5.4-codex` не добавлялся
  - probe для `gpt-5.4-codex` после apply = unsupported / fail

## Rollback required or not

- `Rollback required` = `no`
- Причина: apply прошёл в согласованном scope, post-check подтвердил ожидаемый routing/result contour.

## Итог

- `successful`
- `HTTP 404` устранён
- supported Bridge 2 routing заведён только для подтверждённых live ids:
  - `gpt-5`
  - `gpt-5.2`
  - `gpt-5.3-codex`
  - `gpt-5.4`
- `gpt-5.4-codex` не добавлялся
