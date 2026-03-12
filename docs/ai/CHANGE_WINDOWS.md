# CHANGE WINDOWS

## Цель
Любые изменения в Борисе и связанных сервисах делать только в предсказуемое время и по понятному сценарию.

Canonical default approvals: `docs/ai/DEFAULT_APPROVALS.md`.

## Категории изменений

### Docs-only
Можно в любое время.

Сюда относятся:
- CLAUDE.md
- AGENTS.md
- docs/ai/*
- .claude/agents/*
- любые audit/result/baseline файлы

Docs-only updates, docs-only commits и docs-only push разрешены по умолчанию, если более узкий task-specific scope не запрещает это явно.

### Low-risk server changes
Ежедневно в любое время.

Сюда относятся:
- read-only inspection в repo и на согласованных серверах
- read-only SSH и `pre-check` на согласованных хостах
- точечные server-side fixes с малым blast radius
- alias / housekeeping
- отключение подтверждённого legacy
- корректировка health-check assumptions
- действия, где есть backup, rollback и короткий post-check
- apply только в явно названном узком scope (`one file | one field | one job | one service contour`)
- in-place использование existing server-side secrets, если без этого нельзя выполнить `pre-check`, `apply` или `post-check`

### High-risk changes
Только по отдельному explicit approval.

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
- restart / reload
- restart критичных сервисов
- изменения systemd/nginx/caddy/crontab/jobs.json
- broad live refactor
- любые destructive actions

## Общие правила
- Сначала pre-check.
- Потом backup.
- Потом минимальный apply.
- Потом post-check.
- При провале post-check — immediate rollback.
- Low-risk apply по умолчанию допустим только в рамках `docs/ai/DEFAULT_APPROVALS.md`.
- Никаких high-risk изменений без explicit approval.
- Если live contradicts docs, сначала обновлять канон, а не чинить наугад.

## Stop conditions
Изменение не начинать или немедленно остановить, если:
- нет backup;
- неясен source of truth;
- неясен rollback;
- pre-check не совпадает с ожиданием;
- blast radius больше, чем у согласованного scope;
- затрагивается соседний критичный контур вне согласованного scope.
