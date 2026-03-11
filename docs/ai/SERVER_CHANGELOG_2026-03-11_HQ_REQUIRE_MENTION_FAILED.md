# SERVER CHANGELOG 2026-03-11 HQ REQUIRE MENTION FAILED

## Слой

- Internal Boris Telegram group-response gating for Штаба на `S1`.

## Source of truth / target during attempt

- Live runtime target:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
  - `.channels.telegram.groups["-1002799098412"].requireMention`
- Adjacent restore layer:
  - `/var/lib/apps-data/boris-doctor/backups/telegram-config.json`
- Related writer / restore contour:
  - `workspace-validator.py`

## Что было не так

- Штаб chat id = `-1002799098412`.
- Current live Telegram group config держал `requireMention=false`.
- В таком состоянии Boris мог отвечать в Штабе без explicit mention.
- Нужен был минимальный live fix: перевести Штаб на mention-only gating без изменения других Telegram group-response knobs.

## Что пытались изменить

- Был запланирован и выполнен только один narrow change:
  - `.channels.telegram.groups["-1002799098412"].requireMention`
  - `false -> true`
- Что не меняли:
  - `mentionPatterns`
  - `replyToMode`
  - `topic overrides`
  - `workspace-validator.py`
  - routing
  - workflows
  - bridge
  - monitoring

## Где backup

- `/root/hq-requiremention-apply-20260311T143704Z`
- Внутри:
  - `openclaw.json.bak`
  - `telegram-config.json.bak`
  - `precheck.json`

## Pre-check

Подтверждено до apply:

- channel = `Telegram`
- chat id = `-1002799098412`
- current `requireMention = false`
- `groupPolicy = open`
- topic overrides для группы отсутствуют
- `replyToMode` отсутствует / default
- `mentionPatterns` не менялись и были:
  - `^\\s*@?aibuildingbot\\b`
  - `^\\s*(?:борис|ионов)\\b`
  - `^\\s*boris\\b`
- validator backup существует и тоже хранит `requireMention = false`

## Immediate post-check

Immediate post-check прошел:

- `requireMention = true`
- `groupPolicy` остался `open`
- topic overrides не появились
- `replyToMode` не изменился
- `mentionPatterns` не изменились
- изменился только целевой field

## Delayed validator-backup check

Delayed check не прошел:

- polling выполнялся по `/var/lib/apps-data/boris-doctor/backups/telegram-config.json`
- внутри backup оставалось:
  - `.groups["-1002799098412"].requireMention = false`
- backup `mtime` не менялся и оставался:
  - `2026-03-11 10:01:35.779940623 +0000`
- значит delayed validator-backup convergence внутри check window не произошел

## Почему change считался unstable

- Runtime field в `openclaw.json` переключился на `true`, но adjacent validator backup остался stale.
- Пока `/var/lib/apps-data/boris-doctor/backups/telegram-config.json` не конвергирует, refresh / ownership logic для этого Telegram contour нельзя считать понятной и стабильной.
- По согласованному правилу success нельзя было объявлять только по immediate runtime result.
- Перед любым новым apply нужно отдельно понять refresh / ownership logic для `telegram-config.json`.

## Rollback required or not

- `Rollback required` = `yes`
- Rollback был выполнен сразу после failed delayed validator-backup check.
- Были восстановлены:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
  - `/var/lib/apps-data/boris-doctor/backups/telegram-config.json`
- Current live state после rollback:
  - `.channels.telegram.groups["-1002799098412"].requireMention = false`

## Итог

- `rolled back`
- Immediate apply worked, но delayed validator-backup convergence не произошел внутри check window.
- Current live state остался исходным: `requireMention=false`.
- Новая попытка apply требует отдельного понимания refresh / ownership logic для Telegram backup contour.
