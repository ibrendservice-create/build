# CHANGE RUNBOOK

## Цель
Любое server-side изменение делать одинаково: проверка, backup, apply, post-check, rollback.

## Обязательный порядок

### 1. Определи слой
Перед началом всегда определить:
- какой контур меняется;
- source of truth;
- blast radius;
- что не должно быть затронуто.

### 2. Pre-check
До изменения обязательно:
- подтвердить live state;
- подтвердить путь/файл/юнит/процесс;
- убедиться, что нет drift между ожиданием и реальностью;
- зафиксировать текущий статус.

Если pre-check не совпал с ожиданием, apply не делать.

### 3. Backup
Перед любым apply:
- сделать timestamp backup;
- сохранить pre-state;
- сохранить путь к backup;
- не читать содержимое секретов.

### 4. Minimal apply
Менять только то, что входит в согласованный scope.
Не расширять задачу на ходу.
Не делать “попутные улучшения”.

### 5. Post-check
После apply обязательно проверить:
- целевой контур;
- соседние контуры;
- отсутствие новых ошибок;
- что apply дал именно ожидаемый результат;
- что rollback всё ещё возможен.

### 6. Rollback
Rollback обязателен, если:
- post-check не проходит;
- появилось неожиданное изменение соседнего контура;
- live state стал хуже;
- цель изменения не достигнута.

Rollback делать сразу, не откладывать.

## Формат change plan
Для каждого server-side apply заранее должен быть готов такой блок:

- Слой
- Source of truth
- Что меняется
- Что не меняется
- Backup
- Apply
- Post-check
- Rollback
- Risk
- Verdict

## Что запрещено
Без explicit approval нельзя:
- auth
- routing
- gateway
- bridge
- monitoring
- workflows
- model routing
- pipeline placement
- prompt/memory live layout
- restart критичных сервисов
- destructive actions
- secrets/tokens/credentials

## Формат change result
После каждого apply нужно зафиксировать:
- что было не так;
- что изменили;
- где backup;
- результат pre-check;
- результат post-check;
- был ли rollback;
- итог: success / failed / rolled back.

