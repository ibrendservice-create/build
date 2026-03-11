# SERVER AUDIT ADDENDUM 2026-03-11 BRIDGE HA

Узкий read-only аудит по public `bridge-ha` URL ambiguity.
Изменения в live не выполнялись.

## Что проверено

- Repo refs на `bridge-ha`, `n8n.brendservice24.ru`, `ops.brendservice24.ru`.
- Public probes:
  - `https://n8n.brendservice24.ru/bridge-ha/health`
  - `https://ops.brendservice24.ru/bridge-ha/health`
- Live `S2` `/etc/caddy/Caddyfile`.
- Live `S1` `/etc/nginx/sites-enabled/n8n-public-edge`.
- Direct host-routed probes через `--resolve` на `S1` и `S2` для `n8n` / `ops` domain.

## Canonical URL

- Canonical public health probe = `https://n8n.brendservice24.ru/bridge-ha/health`.
- Подтверждение:
  - public probe возвращает `200 application/json`
  - audit checklist уже использует именно этот URL
  - live ingress на `S1` и `S2` содержит explicit routing для `n8n.../bridge-ha/*`
- Валидным этот public probe считать не только по `HTTP 200`, но и по `JSON / application/json`.

## Что legacy / ambiguous

- `ops.brendservice24.ru` сам по себе не legacy:
  - домен активен для n8n UI/API default handle
  - домен активен для `/pipeline/*`
- Но `ops.brendservice24.ru/bridge-ha/*` сейчас не является canonical route:
  - path `/bridge-ha/*` на `ops` domain в live `Caddyfile` не настроен
  - запрос уходит в default n8n UI и возвращает `200 text/html`
- Это не fallback route и не supported public health URL.
- Ambiguity появляется из snapshot/topology docs, где `ops` domain визуально ассоциирован с `bridge-ha`, хотя live ingress это не подтверждает.
- Реально настроенный live ingress:
  - `S1 nginx`, host `n8n.brendservice24.ru`: explicit `location /bridge-ha/`
  - `S2 Caddy`, host `n8n.brendservice24.ru`: explicit `handle /bridge-ha/*`
  - `S2 Caddy`, host `ops.brendservice24.ru`: `/bridge-ha/*` отсутствует

## Риск

- Классификация: `docs drift / ingress ambiguity`, не live outage.
- Operational risk умеренный:
  - ложный `OK`, если проверять только `HTTP 200`
  - неверный mental model по ingress при future changes
- Current live bridge-ha contour работает по canonical `n8n` URL.
- Owner decision нужен только если владелец захочет поддерживать `/bridge-ha/*` и на `ops` domain.

## Что можно сделать только в docs

- Зафиксировать canonical public probe = `https://n8n.brendservice24.ru/bridge-ha/health`.
- Зафиксировать, что `ops.brendservice24.ru/bridge-ha/*` не является canonical route.
- Зафиксировать, что `ops` domain активен, но path `/bridge-ha/*` на нём не поддерживается.
- Явно требовать для public `bridge-ha` probe проверку `application/json` / JSON body, а не только `HTTP 200`.
- Пометить snapshot/topology ambiguity как docs drift, не как live outage.

## Что требует approve

- Любые server-side изменения `nginx`, `Caddy`, Cloudflare/DNS, TLS ingress или reverse-proxy routing вокруг `/bridge-ha/*`.
- Любые live changes failover logic `S1:8443 primary -> S2:3100 fallback`.
- Любая попытка добавить official `/bridge-ha/*` support на `ops` domain.
- Любые monitoring/self-healing changes, которые начнут использовать `ops` URL как canonical probe.

## Вердикт

- `WARN`
- Canonical public probe = `https://n8n.brendservice24.ru/bridge-ha/health`.
- `ops.brendservice24.ru/bridge-ha/*` не canonical и не supported route в текущем live ingress.
- Это docs drift / ingress ambiguity, а не подтвержденный live outage.
