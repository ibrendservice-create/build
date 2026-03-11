# SERVER CHANGELOG 2026-03-11 CRON DELIVERY PHASE B

## Что было не так

- После успешного Phase A canary оставались 7 live cron jobs с устаревшим delivery tail.
- Во всех 7 jobs текст в Telegram уходил через inline positional argument вида `"$TEXT"` вместо canonical stdin delivery.
- Это сохраняло риск ложного `ok` или скрытого delivery failure в isolated sessions.

Scope Phase B был строго ограничен этими jobs:
- `879abd47-d390-4a77-84ba-0e4631130278` `Timur Evening Digest`
- `de978743-d6ab-438e-80bc-e469ff00815a` `Commitment Checker`
- `e6642fda-3c16-4acf-9463-2d2ec966db2d` `Email morning digest`
- `8d7e19a6-7105-4011-b08e-b8b1693c0444` `Email evening digest`
- `fa920a38-8c49-4ca2-b8cd-472ed7ef8020` `Weekly Self-Audit`
- `1370bb4c-190e-45a9-acae-f237bf478cea` `Price List Sync + Contract Check`
- `c9e5ce4b-a982-426e-972c-57ad3cccff19` `Дайджест развития — Штаб`

Вне scope и без изменений:
- `e8e2803e-7d5f-4bc8-831a-c85a3b1aa4ab` `okdesk-comment-monitor`
- `e5dff9f8-49ea-4623-8427-58ba62499a3b` `Timur Morning Digest`
- `65f1280e-b4fb-42cb-860f-7bb92ce9bd39` `Дайджест развития — Канал мастеров`
- любые `routing / workflows / bridge / monitoring / model files / jobs` вне перечисленного scope

## Что изменили

На `S1` изменён только `payload.message` у 7 scoped jobs.

Во всех 7 jobs:
- direct inline send через `exec python3 /data/scripts/tg-send-helper.py ... "$TEXT"` заменён на canonical stdin delivery;
- добавлено требование считать успех только по `OK: sent to ...`;
- добавлено явное правило не заявлять delivery success при failed send или отсутствии success marker.

Для `Commitment Checker` нормализованы все три send points.
Для `Дайджест развития — Штаб` нормализованы оба threaded send points:
- `thread_id=25`
- `thread_id=31`

Schedule, model, session target, wake mode и соседние jobs не менялись.

## Где backup

- full backup: `/var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json.bak-20260311-073333`
- scoped backup: `/var/lib/apps-data/openclaw/data/.openclaw/cron/phaseB-scope-20260311-073333.json`

Локальная temp-копия pre-state:
- `/tmp/phaseB_scope_before_20260311.json`

## Pre-check

Pre-check совпал с ожиданием.

Подтверждено до apply:
- все 7 scoped jobs ещё использовали старый inline delivery tail;
- `Commitment Checker` имел 3 старых send points;
- `Дайджест развития — Штаб` имел 2 старых threaded send points;
- out-of-scope anchors были зафиксированы до apply:
  - `Timur Morning Digest` `updatedAtMs=1773213311522`
  - `Дайджест развития — Канал мастеров` `updatedAtMs=1773033466252`
  - `okdesk-comment-monitor` `updatedAtMs=1773214226374`

## Post-check

Structural post-check прошёл.

Подтверждено после apply:
- все 7 scoped jobs now содержат canonical stdin delivery blocks;
- в scoped jobs больше нет old actionable lines вида `exec python3 /data/scripts/tg-send-helper.py ... "$TEXT"`;
- `Commitment Checker` содержит все 3 canonical send blocks;
- `Дайджест развития — Штаб` содержит оба canonical threaded send blocks;
- out-of-scope anchors не изменились:
  - `Timur Morning Digest` `updatedAtMs=1773213311522`
  - `Дайджест развития — Канал мастеров` `updatedAtMs=1773033466252`
  - `okdesk-comment-monitor` `updatedAtMs=1773214226374`

Функциональный send retest в рамках Phase B не запускался, чтобы не создавать новые message side effects.

## Rollback required or not

- `Rollback required` = `no`
- Причина: apply прошёл в согласованном scope, structural post-check подтвердил ожидаемый результат, drift вне scope не найден.

## Итог

- `successful`
