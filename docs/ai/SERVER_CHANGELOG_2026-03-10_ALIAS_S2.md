# SERVER CHANGELOG 2026-03-10 ALIAS S2

## Что было не так
- На S1 не был настроен alias `s2`.
- Из-за этого `ssh s1 'ssh -o BatchMode=yes s2 "hostname -f"'` падал на hostname resolution, хотя сетевой путь `S1 -> 72.56.98.52:22` был рабочим.

## Что именно изменено
- На S1 в `/root/.ssh/config` добавлен минимальный block:

```sshconfig
Host s2
  HostName 72.56.98.52
  User root
```

- Другие host blocks не изменялись.

## Где backup
- `/root/.ssh/config.bak-20260310-194511`

## Какие post-check выполнены
- `ssh s1 'ssh -G s2 | egrep "^(hostname|user) "'`
  - `user root`
  - `hostname 72.56.98.52`
- `ssh s1 'ssh -o BatchMode=yes s2 "hostname -f"'`
  - `6612399-hf274138.twc1.net`

## Итог
- `fix successful`
