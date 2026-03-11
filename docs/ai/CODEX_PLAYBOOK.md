# CODEX PLAYBOOK

## База
Перед любой задачей читать:
- AGENTS.md
- docs/ai/BASELINE_2026-03-10.md
- docs/ai/BORIS_DETAIL_SCHEMA_CHECKLIST_v2.md
- docs/ai/CHANGE_WINDOWS.md
- docs/ai/CHANGE_RUNBOOK.md
- docs/ai/SOURCE_OF_TRUTH.md
- /Users/timuraripov/Desktop/BS24-MASTER-PLAN-v2.0.md

## Правила
- Сначала audit, потом plan, потом apply.
- Если это docs drift — только docs-only update.
- Если это live change — сначала найти:
  - master
  - runtime
  - writers/enforcers
  - trigger writers
  - safe apply path
- Не править runtime-файл напрямую, если его перезапишет writer/enforcer.
- Не трогать без explicit approval:
  - workflows active flags
  - model routing live files
  - bridge / gateway / auth
  - prompt/memory live layout
  - pipeline placement
  - monitoring / self-healing
  - secrets
  - destructive actions
- Не редактировать live jobs.json руками.
- Для server-side skill сначала найти точный live SKILL.md и связанные scripts.
- Для cron сначала понять: это cron или heartbeat.

## Типы задач
### 1. Analyze
Нужно понять, что это вообще: skill / cron / heartbeat / workflow / script.

### 2. Audit block
Нужно проверить один блок или один контур read-only.

### 3. Docs-only
Нужно только обновить docs после аудита.

### 4. Apply plan
Нужно подготовить безопасный live plan без изменений.

### 5. Apply
Делать только после approve и только в согласованном scope.

### 6. Changelog
После apply зафиксировать результат и обновить backlog/final actions.

## Формат ответа
- Что проверено
- Что найдено
- Риск
- Что можно исправить только в docs
- Что требует owner decision
- Что требует approve
- Вердикт

## Формат live apply plan
- Слой
- Source of truth
- Exact files/services
- Что меняется
- Что не меняется
- Backup
- Pre-check
- Apply
- Post-check
- Rollback
- Risk
- Verdict
