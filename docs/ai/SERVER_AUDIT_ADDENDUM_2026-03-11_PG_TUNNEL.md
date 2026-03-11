# SERVER AUDIT ADDENDUM 2026-03-11 PG TUNNEL

Узкий read-only аудит по `pg-tunnel-s2.service`.
Изменения в live не выполнялись.

## Что проверено

- `systemctl cat/status/show pg-tunnel-s2.service` на `S1`.
- Кто реально слушает `172.18.0.1:15432` на `S1`.
- `docker inspect` по `boris-emails-pg-1`.
- Live `crontab` на `S1`.
- Live sync scripts:
  - `/opt/apps/openclaw/sync-pg-from-s2.sh`
  - `/opt/apps/openclaw/sync-executors-from-s2.sh`
- `infra-monitor` / `service-guard` logic по `boris_pg_mode` и `pg-tunnel-s2`.
- State file `/var/lib/apps-data/infra-monitor/state/boris-pg-mode`.
- Read-only вызов `check_pg_tunnel()` из live `service-guard.py`.
- Свежий лог `sync-pg-s2.log` и базовая читаемость локального `boris-emails-pg-1`.

## Что найдено

- `pg-tunnel-s2.service` это `autossh`-tunnel:
  - `-L 172.18.0.1:15432:127.0.0.1:15432`
  - target = `root@72.56.98.52`
- Unit сейчас = `disabled + failed`.
- Прямая причина `failed`:
  - `bind [172.18.0.1]:15432: Address already in use`
- Порт `172.18.0.1:15432` уже занят локальным `docker-proxy` для `boris-emails-pg-1`.
- Current Boris PG mode on `S1` = `local`:
  - source = `/var/lib/apps-data/infra-monitor/state/boris-pg-mode`
- Live Boris PG data plane на `S1` сейчас = local container `boris-emails-pg-1`, а не tunnel.
- Live sync `S2 -> S1` сейчас идёт не через tunnel:
  - `sync-pg-from-s2.sh` использует прямой `ssh root@72.56.98.52 "docker exec app-db-1 ..."`
  - `sync-executors-from-s2.sh` использует `scp`
- `service-guard.py` в режиме `local` считает этот contour healthy через local PG container:
  - `check_pg_tunnel()` вернул `healthy=true`
- `infra-monitor` всё ещё знает про `pg-tunnel-s2` как auto-enrolled service и пытается делать `reset-failed`, но этот cleanup path не проходит по `sudo`.
- Свежий sync log подтверждает, что `technicians/dispatch/.../emails` продолжают синхронизироваться без tunnel.

## Это legacy или live dependency

- Для текущего live-контура это не current live dependency.
- Это residual / contingency contour от старого tunnel-based PG mode.
- Текущая live реальность на `S1`:
  - Boris PG mode = `local`
  - Boris PG backend = `boris-emails-pg-1`
  - `S2 -> S1` sync = `ssh/scp scripts`

## Риск

- Классификация: `legacy noise` с `operational risk`, а не runtime failure.
- Что именно рискованно:
  - `failed` unit остаётся в systemd state и путает диагностику;
  - monitoring contour всё ещё помнит этот unit;
  - можно ошибочно начать "чинить" tunnel вместо current local PG data plane;
  - contour конфликтует с local PG по `172.18.0.1:15432`.
- Owner decision нужен перед любым apply:
  - оставить это как contingency contour;
  - или выводить из эксплуатации.

## Что можно сделать только в docs

- Зафиксировать в каноне, что `pg-tunnel-s2.service` не является текущей live dependency.
- Зафиксировать, что current Boris PG mode on `S1` = `local`.
- Зафиксировать конфликт `pg-tunnel-s2` с local `boris-emails-pg-1` по `172.18.0.1:15432`.
- Зафиксировать, что live sync `S2 -> S1` идёт через `ssh/scp` scripts, а не через tunnel.
- Описать contour как `legacy noise with operational risk`, не как runtime failure.

## Что требует approve

- Любые server-side действия по `pg-tunnel-s2.service`:
  - `enable/disable/start/stop/restart/reset-failed`
  - редактирование или удаление unit
- Любые изменения local Boris PG contour на `S1`:
  - `boris-emails-pg-1`
  - bind `172.18.0.1:15432`
  - related docker compose / PG routing
- Любые изменения `infra-monitor`, `service-guard`, `auto-services.txt`, `sudoers` или self-healing логики вокруг этого unit.
- Любые изменения sync scripts / crontab для `S2 -> S1` PG sync.

## Вердикт

- `WARN`
- `pg-tunnel-s2.service` сейчас = legacy contour, не current live dependency.
- Текущий live Boris PG contour на `S1` работает в `local` mode.
- Проблема сейчас = operational noise и docs gap, а не active runtime outage.
