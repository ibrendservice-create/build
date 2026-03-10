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
15. `HANDOFF_2026-03-10.md` не переписан; drift отражен только в каноне repo.
16. Если правка опирается на live-аудит, в каноне есть ссылка на dated audit docs, а не на память "по умолчанию".
17. Для audit-backed drift проверены и отражены:
    - `okdesk-pipeline` active на S2;
    - internal cron = `bridge/claude-opus-4-6`;
    - external routing = `claude-haiku-4-5 -> gpt-5`;
    - `.openclaw/SOUL.md` отсутствует и `RULES.md` живет в `workspace/memory`;
    - Caddyfile = `/etc/caddy/Caddyfile`;
    - `sites-enabled` на S1 это regular files;
    - local `8443` health = `http`;
    - Docling без host `:5001`, но доступен в docker-сети;
    - WF3/WF8 relay/WF10 active, WF11/WF8 Watchdog inactive;
    - S1 -> S2 alias drift не описан как network failure.
