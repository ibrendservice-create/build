# SERVER AUDIT ADDENDUM 2026-03-10 WORKFLOWS

## Что проверено

- Snapshot-ожидания в `docs/ai/HANDOFF_2026-03-10.md` сверены с каноном repo и bug register.
- Live flags на S2 read-only проверены напрямую в `n8n.workflow_entity` по exact workflow IDs:
  - `eHRHeiYttQgUgkHK`
  - `0iwcXPWA3XKGknLz`
  - `0Qj2ZeBsz5UtlZps`
  - `VxaGd6LaPHOg3KHi`
  - `qWKnu4iqTspEsCxi`
  - `VufRh7hHufiddQZQ`
  - `kCZriGsWrWFVd3pG`
  - `wvVidk9SZJ1n0DAN`
- Результат дополнительно сверен с `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md` и `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`.

## Live state

- `WF3` `eHRHeiYttQgUgkHK` -> `active`
- `WF8 relay` `0iwcXPWA3XKGknLz` -> `active`
- `WF8 Watchdog` `0Qj2ZeBsz5UtlZps` -> `inactive`
- `WF10` `VxaGd6LaPHOg3KHi` -> `active`
- `WF11` `qWKnu4iqTspEsCxi` -> `inactive`
- `Email Attachment Parser` `VufRh7hHufiddQZQ` -> `inactive`
- `Telegram Logger` `kCZriGsWrWFVd3pG` -> `active`
- `WF Watchdog` `wvVidk9SZJ1n0DAN` -> `active`

## Drift vs handoff

- Совпадает с `HANDOFF_2026-03-10.md`:
  - `WF3 = active`
  - `WF8 relay = active`
  - `WF10 = active`
  - `Telegram Logger = active`
  - `WF Watchdog = active`
  - `Email Attachment Parser = inactive`
- Расходится с `HANDOFF_2026-03-10.md`:
  - `WF11`: `HANDOFF=Active`, `live=inactive`
  - `WF8 Watchdog`: `HANDOFF=Active`, `live=inactive`

## Docs drift или operational issue

- Для `WF11` и `WF8 Watchdog` подтверждён `docs drift` относительно snapshot docs.
- По read-only данным нет доказательства runtime-аварии или самопроизвольной деградации именно из-за этих flags.
- Но это не считается автоматически нормой: для `WF11` и `WF8 Watchdog` требуется `owner decision`, потому что snapshot docs ожидают `active`, а live сейчас `inactive`.
- `Email Attachment Parser` выглядит как нормальная `inactive`-конфигурация:
  - он `inactive` и в snapshot docs, и в live;
  - live name содержит `(on-demand)`, что не противоречит paused/manual usage.

## Что можно исправить только в repo

- Обновлять канон и bug register так, чтобы repo-visible live state отражал:
  - `WF11 = inactive`
  - `WF8 Watchdog = inactive`
  - `WF3 / WF8 relay / WF10 / Telegram Logger / WF Watchdog = active`
  - `Email Attachment Parser = inactive`
- Явно помечать, что reconciliation workflow state нужно делать по `workflow id`, а не только по названию, потому что live names частично дрейфуют.

## Что требует approve

- Любое изменение `active` flags в n8n/live.
- Любая активация или деактивация `WF11` или `WF8 Watchdog`.
- Любые правки workflow logic, restart `n8n`, DB updates или import/export workflow state.

## Вердикт

- `WARN`
- Live state подтверждён.
- Реальный drift есть только по `WF11` и `WF8 Watchdog`.
- `Email Attachment Parser inactive` сейчас выглядит нормой.
- Для `WF11` и `WF8 Watchdog` нужен `owner decision` перед любым apply.
