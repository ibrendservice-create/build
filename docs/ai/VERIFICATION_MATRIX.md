# VERIFICATION MATRIX

После любого изменения проверить:
1. Целевой компонент.
2. Зависимости ниже.
3. Зависимости выше.
4. Routing и delivery, если затронуты.
5. Hooks / cron / skills, если затронуты.
6. Monitoring / self-healing, если затронуты.
7. Логи на ошибки.
8. Отсутствие config drift.
9. Возможность rollback.

Для docs / project instruction changes дополнительно проверить:
10. `AGENTS.md` и `CLAUDE.md` читают один и тот же канон и один и тот же порядок памяти.
11. Канон явно отделен от snapshot docs.
12. Все конфликтующие факты помечены `SERVER_AUDIT_REQUIRED`.
13. В repo не добавлены secrets / tokens / credentials.
14. Не изменены runtime/server-side files.
