# SERVER AUDIT RESULT 2026-03-10

## Summary
- Аудит остановлен на network layer.
- Причина остановки: слой `сеть и доступы` дал `FAIL`, потому что связность `S1 -> s2` по имени не подтверждена, а прямой SSH с S1 на `72.56.98.52` не подтвердился в рамках timeout.
- Выше лежащие слои не проверены по правилу остановки из `docs/ai/SERVER_AUDIT_CHECKLIST.md`.

## Слой: сеть и доступы
**Что проверено**
- Доступность S1 и S2 по SSH с audit-хоста.
- Базовые ресурсы S1 и S2: `hostname`, `date`, `uptime`, `df`, `free`.
- Listening ports на S1 и S2.
- Права на `/etc/apps/secrets`.
- Symlink-и на S1 и S2.
- Связность `S1 -> s2`.

**Фактический результат**
- S1 доступен: `srv1373331.hstgr.cloud`, uptime `1 day`, `/` использовано `49%`.
- S2 доступен: `6612399-hf274138.twc1.net`, uptime `13 days`, `/` использовано `71%`.
- На S1 слушают `58536`, `80`, `443`, `8443`, `3100`, `3102`, `15432`, `55228`, `18790`.
- На S2 слушают `22`, `80`, `443`, `5678`, `15432`, `3200`, `3300`, `3301`, `3100`.
- `S1 /etc/apps/secrets = 711`, `S2 /etc/apps/secrets = 751`.
- Symlink-и на обоих серверах ведут в `/opt/apps/*`.
- `ssh s1 'ssh s2 ...'` вернул `Could not resolve hostname s2`.
- `ssh s1 'ssh root@72.56.98.52 ...'` не подтвердился в рамках timeout.

**Красные флаги**
- На S1 не резолвится hostname `s2`.
- Связность `S1 -> S2` не подтверждена.
- На S2 не видно listening `:5001`, хотя docs описывают Docling на `5001`.
- На S2 диск `71%`, это operational warning.

**PASS / WARN / FAIL**
- `FAIL`

## Слой: контейнеры и процессы
**Что проверено**
- Не проверялось.

**Красные флаги**
- `SERVER_AUDIT_REQUIRED`

**PASS / WARN / FAIL**
- `WARN`

## Слой: Model routing
**Что проверено**
- Не проверялось.

**Красные флаги**
- `SERVER_AUDIT_REQUIRED`

**PASS / WARN / FAIL**
- `WARN`

## Слой: prompts / memory / skills
**Что проверено**
- Не проверялось.

**Красные флаги**
- `SERVER_AUDIT_REQUIRED`

**PASS / WARN / FAIL**
- `WARN`

## Слой: bridge / gateway
**Что проверено**
- Не проверялось.

**Красные флаги**
- `SERVER_AUDIT_REQUIRED`

**PASS / WARN / FAIL**
- `WARN`

## Слой: monitoring / self-healing
**Что проверено**
- Не проверялось.

**Красные флаги**
- `SERVER_AUDIT_REQUIRED`

**PASS / WARN / FAIL**
- `WARN`

## Слой: cron / jobs
**Что проверено**
- Не проверялось.

**Красные флаги**
- `SERVER_AUDIT_REQUIRED`

**PASS / WARN / FAIL**
- `WARN`

## Слой: интеграции
**Что проверено**
- Не проверялось, кроме косвенных сетевых признаков на первом слое.

**Красные флаги**
- `SERVER_AUDIT_REQUIRED`

**PASS / WARN / FAIL**
- `WARN`

## Общий статус
- `FAIL`
- Полный аудит остановлен на слое `сеть и доступы`.

## Противоречия между handoff, схемой и live
- Схема утверждает рабочую связность `S1↔S2` и использование `ssh s2`; live показал, что на S1 имя `s2` не резолвится.
- Схема пишет `S2 disk ~58% used`; live показал `71%`. Здесь `HANDOFF` ближе к live, схема устарела.
- Схема пишет `S1 disk ~38% used`; live показал `49%`. Схема устарела.
- Docs описывают Docling на `5001`; на сетевом слое live не показал listening `:5001` на S2. Требуется дальнейшая проверка.
- На S2 live виден listening `127.0.0.1:3200`; по docs это похоже на `okdesk-pipeline`, но `HANDOFF` утверждает, что `okdesk-pipeline.service` не развернут. Требуется `SERVER_AUDIT_REQUIRED`.

## Что требует отдельного approve
- Любое исправление S1->S2 hostname, DNS или SSH-связности.
- Любые действия с `bridge`, `gateway`, `routing`, `monitoring`, `self-healing`, `workflows`.
- Любые restart критичных сервисов или контейнеров.
- Любые правки server-side truth, live configs, systemd, nginx/Caddy, DB.

## Что можно донастроить только в repo
- Отразить в docs конфликт по `S1 -> s2` hostname resolution.
- Пометить устаревшие disk usage значения в snapshot docs.
- Добавить `SERVER_AUDIT_REQUIRED` для `Docling :5001`.
- Добавить `SERVER_AUDIT_REQUIRED` для `S2 :3200` и live-статуса `okdesk-pipeline`.
