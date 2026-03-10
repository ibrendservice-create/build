# OWNER DECISIONS REQUIRED

Сводка owner-level решений по подтвержденным audit-фактам на дату `2026-03-10`.
Документ не заменяет live source of truth и не разрешает apply без отдельного approve.

## 1. Workflow state decisions

### WF11
- Текущий live факт: `WF11` в live = `inactive`; в `HANDOFF_2026-03-10.md` он описан как `Active`.
- Риск: ошибочно активировать или оставить выключенным workflow, который owner ожидает в другом состоянии.
- Варианты решения:
  - оставить `inactive` как новую норму;
  - активировать обратно после owner-подтверждения intended behavior.
- Что рекомендовано: сначала принять owner decision по intended state; до этого считать проблему docs drift, а не runtime failure.
- Что будет требовать server-side apply: любое изменение `active` flag в n8n/live.

### WF8 Watchdog
- Текущий live факт: `WF8 Watchdog` в live = `inactive`; в `HANDOFF_2026-03-10.md` он описан как `Active`.
- Риск: потерять watchdog-контроль webhook-контура или, наоборот, включить legacy watchdog без понимания intended state.
- Варианты решения:
  - оставить `inactive` как новую норму;
  - активировать обратно после owner-подтверждения.
- Что рекомендовано: owner decision before apply; до этого считать это docs drift.
- Что будет требовать server-side apply: любое изменение `active` flag в n8n/live.

### Email Attachment Parser
- Текущий live факт: `Email Attachment Parser` в live = `inactive`; это совпадает со snapshot docs и выглядит как on-demand/paused usage.
- Риск: ложная активация workflow только из-за неверной трактовки `inactive` как drift.
- Варианты решения:
  - оставить `inactive` как норму;
  - активировать только если owner подтверждает постоянную необходимость.
- Что рекомендовано: оставить без apply.
- Что будет требовать server-side apply: только если owner решит перевести workflow в постоянный `active`.

## 2. Okdesk-pipeline placement decision

### Canonical runtime host
- Текущий live факт: `okdesk-pipeline` реально работает на `S2`; live source of truth = `S2 systemd unit + S2 cron calls + S2 :3200`; на `S1` только stale path/symlink, competing runtime не найден.
- Риск: выполнять deploy/rollback/cleanup не на том сервере, если продолжать ориентироваться на snapshot docs.
- Варианты решения:
  - официально принять `S2` как canonical placement и оставить runtime там;
  - отдельно спланировать миграцию на `S1` как новую архитектурную задачу.
- Что рекомендовано: принять `S2` как canonical placement и не мигрировать сервис только ради соответствия `HANDOFF`.
- Что будет требовать server-side apply:
  - любое редактирование `okdesk-pipeline.service`;
  - cleanup `S1` path/symlink;
  - перенос runtime между `S1` и `S2`;
  - правка cron или restart service.

## 3. Model routing architecture decision

### Layered split vs single-master normalization
- Текущий live факт:
  - internal default-chain master = `model-strategy.json`;
  - internal `openclaw.json` = effective runtime;
  - internal cron declarative master = `model-strategy.json`;
  - internal cron effective runtime = `jobs.json`;
  - external chain master = external `fix-model-strategy.py`;
  - external `openclaw.json` = effective runtime.
- Риск: принять runtime-файл за master и сломать routing не в том слое; особенно опасен split между internal cron и external fixer layer.
- Варианты решения:
  - принять layered split как рабочую архитектуру и не консолидировать сейчас;
  - отдельно спланировать нормализацию к более явному single-master design.
- Что рекомендовано: пока принять текущий layered split как live reality и не делать consolidation без отдельного проекта.
- Что будет требовать server-side apply:
  - любые правки `model-strategy.json`, internal/external `openclaw.json`, `jobs.json`;
  - любые правки internal/external `fix-model-strategy.py`, `circuit-breaker-internal.py`, startup scripts, `crontab`;
  - любые restarts, связанные с model routing.

### Internal cron sync ownership
- Текущий live факт: internal cron models в `jobs.json` = `bridge/claude-opus-4-6`; startup sync из `fix-model-strategy.py` подтвержден, но periodic enforcer для `jobs.json` не подтверждён так же явно, как external fixer layer; `circuit-breaker-internal.py` не подтверждён как source of truth для cron models.
- Риск: ошибочно считать `jobs.json` self-owned runtime или ожидать periodic self-heal, которого может не быть.
- Варианты решения:
  - оставить текущий split и документально считать `model-strategy.json` declarative master для cron;
  - добавить/явно закрепить periodic enforcer для `jobs.json` как отдельное решение;
  - консолидировать cron routing в другой master-слой.
- Что рекомендовано: сначала owner decision, нужен ли вообще явный periodic enforcer для internal cron, или достаточно startup sync + docs.
- Что будет требовать server-side apply:
  - любые изменения cron enforcer logic;
  - любые правки `jobs.json`, `fix-model-strategy.py`, `circuit-breaker-internal.py`, `crontab`.

## 4. What is already stable

### Gateway / health-check contour
- Текущий live факт: active checks уже используют `/etc/caddy/Caddyfile`, local `8443` probe по `http`, не требуют symlink для `sites-enabled` и не требуют host `:5001` для Docling.
- Риск: лишний server-side apply в `gateway`/`monitoring` без реальной проблемы.
- Варианты решения:
  - считать контур стабильным и оставить без apply;
  - всё равно переприводить paths/assumptions на сервере ради единообразия.
- Что рекомендовано: оставить без server-side apply; считать проблему закрытой docs-only нормализацией.
- Что будет требовать server-side apply: только если owner захочет сознательный housekeeping в `gateway`/`monitoring`.

### Prompt / memory source of truth
- Текущий live факт: live rules source of truth на `S1` = `/data/.openclaw/workspace/memory/RULES.md`; `/data/.openclaw/memory` = storage/DB path; `.openclaw/SOUL.md` отсутствует; runtime failure не подтверждён.
- Риск: ненужная server-side перестройка layout или создание ложного compatibility layer.
- Варианты решения:
  - принять текущий layout как норму;
  - позже спланировать cleanup/compatibility only if needed.
- Что рекомендовано: считать контур стабильным и не менять server-side layout без отдельной необходимости.
- Что будет требовать server-side apply: любые изменения prompt/memory layout, loader-paths, создание `SOUL.md` или перенос `RULES.md`.

### S1 -> S2 connectivity
- Текущий live факт: сетевой путь `S1 -> 72.56.98.52:22` рабочий; исходная проблема была в alias `s2`; alias уже починен на `S1`.
- Риск: повторная ложная диагностика как network failure.
- Варианты решения:
  - считать вопрос закрытым;
  - дополнительно приводить runbook и локальные aliases в единую норму.
- Что рекомендовано: считать контур стабильным; без нового apply не трогать.
- Что будет требовать server-side apply: только если owner захочет дальше менять SSH aliases/DNS/system SSH config.

## 5. What must not be touched without explicit approval

### Workflow live state
- Текущий live факт: workflow flags в n8n подтверждены audit-ом по exact IDs.
- Риск: случайно изменить production behavior через `active/inactive`.
- Варианты решения:
  - ничего не менять;
  - менять только после owner decision и отдельного approve.
- Что рекомендовано: не трогать без explicit approval.
- Что будет требовать server-side apply: любые изменения workflow flags, logic, imports/exports, DB updates, `n8n` restart.

### Okdesk-pipeline placement and service state
- Текущий live факт: runtime на `S2`, `S1` не является runtime host.
- Риск: accidental migration, cleanup не того path, restart рабочего сервиса.
- Варианты решения:
  - оставить без изменений;
  - менять placement/service только как отдельную approve-задачу.
- Что рекомендовано: не трогать без explicit approval.
- Что будет требовать server-side apply: любые правки unit, cron, path cleanup, deploy, restart.

### Model routing files and enforcers
- Текущий live факт: routing contour split между `model-strategy.json`, `openclaw.json`, `jobs.json`, external `fix-model-strategy.py`.
- Риск: изменение не того master-слоя и поломка internal/external routing.
- Варианты решения:
  - оставить как есть;
  - менять только по owner-approved server plan.
- Что рекомендовано: не трогать без explicit approval.
- Что будет требовать server-side apply: любые правки routing files, fixer scripts, startup scripts, cron, bridge failover logic.

### Prompt / memory server-side layout
- Текущий live факт: layout стабилен, но отличается от snapshot docs.
- Риск: создать duplicate-source drift или сломать bootstrap.
- Варианты решения:
  - оставить как есть;
  - менять только как отдельную approve-задачу.
- Что рекомендовано: не трогать без explicit approval.
- Что будет требовать server-side apply: любые правки prompt/memory files, loader-paths, compatibility files.
