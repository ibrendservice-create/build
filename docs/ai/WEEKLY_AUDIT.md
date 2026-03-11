# WEEKLY AUDIT

## Цель
Раз в неделю делать короткий read-only аудит Бориса и связанных сервисов, чтобы ловить drift до аварии.

## Режим
Только read-only.
Ничего не менять.
Ничего не перезапускать.
Секреты не читать.

## Проверять каждую неделю

### 1. Доступы и базовое состояние
- SSH до S1 и S2
- hostname
- uptime
- disk usage
- memory
- ключевые listening ports

### 2. Контейнеры и сервисы
- critical docker containers
- critical systemd services
- health status
- restart loops
- inactive/unexpected services

### 3. Bridge / gateway
- local health endpoints
- external health endpoints
- path assumptions
- nginx/caddy drift
- hooks path

### 4. Workflows
- live active/inactive state по workflow id
- drift против канона
- owner-decision candidates

### 5. Cron / jobs / timers
- stale timers
- consecutiveErrors
- jobs with lastStatus=null
- unexpected schedule drift

### 6. Pipeline / integrations
- okdesk-pipeline placement
- :3200
- docling health
- n8n stack
- db availability
- obvious integration drift

### 7. Prompt / memory / rules
- live source of truth для правил
- drift между docs и live paths
- отсутствие неожиданных layout changes

### 8. Model routing
- internal default-chain
- cron model override
- external chain
- drift между master и effective runtime layers

## Выход weekly audit
Результат сохранять как новый файл с датой, например:
- docs/ai/WEEKLY_AUDIT_RESULT_YYYY-MM-DD.md

## Формат weekly audit result
- Что проверено
- Что ок
- Что drift
- Что risky
- Что требует owner decision
- Что можно исправить только в repo
- Что требует approve

## Правило
Если weekly audit находит drift:
- сначала зафиксировать это в docs;
- server-side apply делать только после отдельного change plan.

