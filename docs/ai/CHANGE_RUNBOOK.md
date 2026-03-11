# CHANGE RUNBOOK

## Цель
Любое server-side изменение делать одинаково: проверка, backup, apply, post-check, rollback.

Before editing any live config, first identify:
- source of truth
- derived/runtime file
- all writers/enforcers
- their triggers
- whether the target will be rewritten after apply

If a writer/enforcer exists, do not patch runtime directly unless the change plan explicitly covers the writer layer too.

## Обязательный порядок

### 1. Определи слой
Перед началом всегда определить:
- какой контур меняется;
- source of truth;
- master;
- derived/runtime;
- writers/enforcers;
- trigger writers;
- blast radius;
- что не должно быть затронуто.

### 2. Pre-check
До изменения обязательно:
- подтвердить live state;
- подтвердить путь/файл/юнит/процесс;
- подтвердить, какой файл является master, а какой derived/runtime;
- найти active/potential writers/enforcers и их trigger chain;
- убедиться, что нет drift между ожиданием и реальностью;
- зафиксировать текущий статус.

Если pre-check не совпал с ожиданием, apply не делать.
Если runtime/derived файл будет перезаписан writer/enforcer, apply в него по умолчанию не делать.

### 3. Backup
Перед любым apply:
- сделать timestamp backup;
- сохранить pre-state;
- сохранить путь к backup;
- не читать содержимое секретов.

### 3a. Existing secret use
Если согласованный operational `pre-check`, `apply` или `post-check` нельзя выполнить без уже существующего секрета:
- использовать только уже существующие server-side `tokens / API keys / cookies / env secrets / existing secret-store values`;
- использовать секрет только in-place из existing source, без намеренного вывода значения;
- не печатать секрет в `stdout/stderr`, если это не требуется самим безопасным использованием;
- не сохранять секрет в repo, docs, changelog, temp files или shell history намеренно;
- не менять существующий секрет и не создавать новый;
- не просить пользователя вручную вставлять секрет в чат, если его можно безопасно использовать из existing server-side source;
- если секрет нельзя безопасно использовать без раскрытия значения, остановиться и зафиксировать это в change result.

Это разрешение касается только использования, а не управления секретами.

### 4. Minimal apply
Менять только то, что входит в согласованный scope.
Не расширять задачу на ходу.
Не делать “попутные улучшения”.
Если контур живёт через layered sync, менять master-слой.
Если apply нужен именно в runtime, сначала выбрать только один допустимый путь:
- обновить master;
- обновить writer/enforcer layer;
- по approved plan отдельно отключить enforcer.

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
- Master
- Derived/runtime
- Writers/enforcers
- Trigger writers
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
- rotate/revoke/create/delete secrets/tokens/credentials
- правка runtime/derived файла без writer-chain анализа и согласованного плана по enforcer layer

## Формат change result
После каждого apply нужно зафиксировать:
- что было не так;
- что изменили;
- где backup;
- результат pre-check;
- результат post-check;
- был ли rollback;
- итог: success / failed / rolled back.
