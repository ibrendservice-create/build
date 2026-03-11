# SERVER CHANGELOG 2026-03-11 BLOCK 9 WEBHOOK ROUTES FIX

## Что было не так

- На `S1` в `/etc/nginx/sites-enabled/n8n-public-edge` оставались 3 stale exact-match webhook routes:
  - `/webhook/executor-search`
  - `/webhook/boris-memory-read`
  - `/webhook/boris-mention`
- Все 3 routes указывали на `127.0.0.1:3200`, но listener на `S1 :3200` отсутствовал.
- Generic `location /webhook/` contour целиком сломанным не выглядел, `/hooks/` contour на `S1` был живой, поэтому проблема была narrow live routing drift только в stale exact-match exceptions.

## Что изменили

На `S1` в `/etc/nginx/sites-enabled/n8n-public-edge` удалены только 3 stale exact-match `location` blocks:
- `/webhook/executor-search`
- `/webhook/boris-memory-read`
- `/webhook/boris-mention`

Не менялись:
- `/hooks/`
- generic `location /webhook/`
- `/webhook/email-att-parse`
- `S2 Caddy`
- workflow flags

## Где backup

- `/etc/nginx/sites-enabled/n8n-public-edge.bak-20260311-092148`

## Pre-check

Pre-check совпал с ожиданием.

Подтверждено до apply:
- все 3 stale routes на `S1` указывали на `127.0.0.1:3200`
- listener на `S1 :3200` отсутствовал
- `S2 127.0.0.1:3200/health` был `OK`
- workflows active:
  - `0iwcXPWA3XKGknLz` `WF8 relay`
  - `Rd9sCsT2sqUmOfBS` `Executor Search API`
  - `XMYeAy7quxvHl4xa` `Boris Memory Read`
- `/hooks/` contour на `S1` живой и вне scope
- `nginx -t` до apply successful

## Post-check

Post-check прошёл.

Подтверждено после apply:
- 3 stale exact-match blocks отсутствуют
- сохранены:
  - `location = /webhook/email-att-parse`
  - generic `location /webhook/`
  - `/hooks/` block
- `nginx -t` successful
- `systemctl is-active nginx = active`

Функциональный webhook retest не запускался, чтобы не триггерить live workflows.

## Rollback required or not

- `Rollback required` = `no`
- Причина: apply прошёл в согласованном scope, post-check подтвердил ожидаемый routing shape, drift вне scope не найден.

## Итог

- `successful`
- confirmed live routing issue fixed in narrow scope
