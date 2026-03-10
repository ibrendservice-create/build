# SERVER AUDIT ADDENDUM 2026-03-10 S1 S2 ALIAS

## Summary
- Исходный `FAIL` по сети снят.
- Причина была в отсутствии alias `s2` на S1.
- Low-risk fix применён: alias `s2` добавлен на S1 в `/root/.ssh/config`.
- Сетевой путь `S1 -> 72.56.98.52:22` рабочий, и alias теперь тоже рабочий.

## Что проверено
- На S1: `whoami`, `$HOME`, наличие `/root/.ssh` и файлов в нём.
- Наличие `~/.ssh/config` и alias `Host s2`.
- Эффективный SSH config через `ssh -G s2`.
- Наличие записей для `s2` и `72.56.98.52` в `/etc/hosts`, system SSH config и `known_hosts`.
- Маршрут до `72.56.98.52`.
- TCP-доступ до `72.56.98.52:22`.
- Локальные outbound firewall rules на S1: `ufw`, `iptables`, `nft`.
- Прямой SSH по IP с S1 на S2.

## Что найдено
- На S1 пользователь `root`, home `/root`, есть `/root/.ssh`, `id_ed25519`, `known_hosts`.
- `~/.ssh/config` на S1 отсутствует.
- `ssh -G s2` на S1 оставляет `hostname s2`, то есть alias не подставляется.
- В `/etc/hosts` нет записи для `s2` или `72.56.98.52`.
- В system SSH config alias для `s2` не найден.
- В `known_hosts` есть запись только для `72.56.98.52`, для `s2` записи нет.
- `ip route get 72.56.98.52` на S1 работает.
- `nc -zvw5 72.56.98.52 22` с S1 успешен.
- Outbound firewall на S1 не блокирует SSH:
  - `ufw` inactive/not installed
  - `iptables`: `-P OUTPUT ACCEPT`
  - `nft`: output policy `accept`
- Прямой SSH по IP с S1 на S2 работает:
  - соединение установлено
  - ключ `/root/.ssh/id_ed25519` принят сервером
  - `hostname -f` на S2 вернулся успешно

## Корневая причина
- На S1 не настроен alias `s2`.
- Это не проблема маршрута, не проблема TCP-доступа и не проблема исходящего firewall.
- Предыдущий `FAIL` в полном аудите относился к отсутствию alias `s2`, а не к сетевой недоступности S2.

## Alias problem vs network problem
- `Alias problem`
- Сетевой путь `S1 -> 72.56.98.52:22` исправен.
- SSH по IP и по ключу работает.

## Что можно исправить без риска
- В операционных runbook использовать `ssh root@72.56.98.52` вместо `ssh s2`, пока alias не оформлен.
- В repo docs пометить, что `ssh s2` зависит от локального alias и не является гарантированным live-фактом.
- Обновить вывод прошлого аудита: проблема была не в сетевой недоступности, а в отсутствии alias.

## Fix applied 2026-03-10
- На S1 в `/root/.ssh/config` добавлен минимальный block:

```sshconfig
Host s2
  HostName 72.56.98.52
  User root
```

- Backup: `/root/.ssh/config.bak-20260310-194511`
- Post-check 1:
  - `user root`
  - `hostname 72.56.98.52`
- Post-check 2:
  - `6612399-hf274138.twc1.net`

## Что требует approve
- Любая server-side правка `/root/.ssh/config`, `/etc/hosts` или system SSH config на S1.
- Любые изменения firewall, cloud security settings, routing или SSH daemon config.
- Любые правки snapshot/live docs на серверах.

## Вердикт
- `RESOLVED`
- Реальной сетевой проблемы между S1 и S2 не было; корневая причина была в alias drift, и после low-risk fix alias `s2` на S1 работает.
