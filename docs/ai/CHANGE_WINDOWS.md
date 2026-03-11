# CHANGE WINDOWS

## Цель
Любые изменения в Борисе и связанных сервисах делать только в предсказуемое время и по понятному сценарию.

## Категории изменений

### Docs-only
Можно в любое время.

Сюда относятся:
- CLAUDE.md
- AGENTS.md
- docs/ai/*
- .claude/agents/*
- любые audit/result/baseline файлы

### Low-risk server changes
Только в рабочее окно:
- будни
- 12:00–15:00 МСК

Сюда относятся:
- точечные server-side fixes с малым blast radius
- alias / housekeeping
- отключение подтверждённого legacy
- корректировка health-check assumptions
- действия, где есть backup, rollback и короткий post-check

### High-risk changes
Только по отдельному explicit approval и отдельному change window.

Сюда относятся:
- auth
- routing
- gateway
- bridge
- monitoring / self-healing
- model files
- workflows active flags
- pipeline placement
- prompt/memory live layout
- restart критичных сервисов
- изменения systemd/nginx/caddy/crontab/jobs.json
- любые destructive actions

## Общие правила
- Сначала pre-check.
- Потом backup.
- Потом минимальный apply.
- Потом post-check.
- При провале post-check — immediate rollback.
- Никаких high-risk изменений ночью, в пиковую нагрузку и без owner decision.
- Если live contradicts docs, сначала обновлять канон, а не чинить наугад.

## Stop conditions
Изменение не начинать или немедленно остановить, если:
- нет backup;
- неясен source of truth;
- неясен rollback;
- pre-check не совпадает с ожиданием;
- blast radius больше, чем у согласованного scope;
- затрагивается соседний критичный контур вне окна изменений.

