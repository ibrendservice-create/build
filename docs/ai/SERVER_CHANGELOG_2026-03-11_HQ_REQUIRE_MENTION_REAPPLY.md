# SERVER CHANGELOG 2026-03-11 HQ REQUIRE MENTION REAPPLY

## Слой

- Internal Boris Telegram group-response gating for Штаба on `S1`.

## Source of truth / target during reapply

- Live canonical source:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
  - `.channels.telegram.groups["-1002799098412"].requireMention`
- Adjacent periodic restore snapshot:
  - `/var/lib/apps-data/boris-doctor/backups/telegram-config.json`
- Related refresh contour:
  - `workspace-validator.py`
  - `boris-doctor` healthcheck cycle

## Что было не так

- Штаб chat id = `-1002799098412`.
- Current live Telegram group config kept `requireMention=false`.
- In that state Boris could answer in Штабе without explicit mention.
- Previous attempt from `2026-03-11` was rolled back because delayed backup check window was too short and treated stale `telegram-config.json` as an error before the next eligible validator cycle.

## Что изменили

- Applied only one narrow live change:
  - `/var/lib/apps-data/openclaw/data/.openclaw/openclaw.json`
  - `.channels.telegram.groups["-1002799098412"].requireMention`
  - `false -> true`
- Did not change:
  - `mentionPatterns`
  - `replyToMode`
  - `topic overrides`
  - `workspace-validator.py`
  - `telegram-config.json` by hand
  - routing
  - workflows
  - bridge
  - monitoring
  - restart behavior

## Где backup

- `/root/hq-requiremention-reapply-20260311T181025Z`
- Inside:
  - `openclaw.json.bak`
  - `telegram-config.json.bak`
  - `precheck.json`

## Pre-check

Confirmed before apply:

- channel = `Telegram`
- chat id = `-1002799098412`
- current `requireMention = false`
- current `groupPolicy = open`
- current `replyToMode` absent / `null`
- topic overrides absent
- `mentionPatterns` unchanged and hashed as:
  - `c203433e1ca24591420d571caa3303ec555d586e2d2cfef9a454acda5340429e`
- adjacent group fields hash without `requireMention`:
  - `ce91f0693755b0a6e9b2a94b39daf788e9604009f9bbfd7e65c3746c69a318cf`
- backup snapshot also had `requireMention = false`
- last validator healthcheck:
  - `2026-03-11 16:02:37 UTC`

## Immediate post-check

Immediate runtime post-check passed:

- runtime `requireMention = true`
- `groupPolicy` unchanged = `open`
- `replyToMode` unchanged = `null`
- topic overrides unchanged / absent
- `mentionPatterns` hash unchanged:
  - `c203433e1ca24591420d571caa3303ec555d586e2d2cfef9a454acda5340429e`
- adjacent group hash unchanged:
  - `ce91f0693755b0a6e9b2a94b39daf788e9604009f9bbfd7e65c3746c69a318cf`
- exact changed path count = `1`
- exact changed path:
  - `channels.telegram.groups.-1002799098412.requireMention`
- current `telegram-config.json` still shows `requireMention = false`, and this is expected before the next eligible validator refresh window

## Exact next eligible validator refresh window

- `2026-03-12 04:02:37 UTC` to `2026-03-12 04:04:37 UTC`
- `2026-03-12 07:02:37 MSK` to `2026-03-12 07:04:37 MSK`

## Delayed post-check after validator window

Read-only delayed closeout check executed after the eligible validator window:

- check time:
  - `2026-03-12 15:40:54 UTC`
- runtime `openclaw.json` still confirms:
  - `.channels.telegram.groups["-1002799098412"].requireMention = true`
- periodic restore snapshot `telegram-config.json` converged to:
  - `.groups["-1002799098412"].requireMention = true`
- adjacent fields remained unchanged in the checked scope:
  - `groupPolicy = open`
  - `replyToMode = null`
  - topic overrides absent
  - runtime and backup matched on the checked adjacent field set for this group
- rollback remained not required

## Что считать success condition

- Immediate success:
  - runtime field in `openclaw.json` = `true`
  - no scope drift
  - adjacent fields unchanged
- Stable success:
  - on the next eligible validator cycle `telegram-config.json` converges to `requireMention = true`
  - runtime field remains `true`
  - `mentionPatterns`, `replyToMode`, topic overrides remain unchanged
- Important:
  - stale `telegram-config.json` before the validator window above is **not** an error

## Rollback required or not

- `Rollback required` = `no`
- Rollback condition remains only for:
  - failed immediate runtime post-check
  - scope drift
  - incorrect later validator convergence

## Текущий итог

- `runtime success`
- `validator convergence confirmed`
- Current live canonical runtime state after reapply:
  - `.channels.telegram.groups["-1002799098412"].requireMention = true`
- Current converged backup state after delayed read-only post-check:
  - `.groups["-1002799098412"].requireMention = true`
- Adjacent fields remained unchanged in the checked scope.
- `Rollback required` = `no`
- Final contour verdict:
  - `resolved / converged`
