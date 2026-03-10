# CHANGE POLICY

## Можно без отдельного approve
- чтение файлов и конфигов;
- диагностика;
- health-check;
- backup;
- rollback plan;
- документация и read-only проверки.

## Нельзя без явного approve
- перезапуск критичных контейнеров;
- auth/routing/gateway/bridge changes;
- смена токенов и секретов;
- destructive SQL и удаление данных;
- правка generated/runtime вместо master;
- широкие рефакторинги.
