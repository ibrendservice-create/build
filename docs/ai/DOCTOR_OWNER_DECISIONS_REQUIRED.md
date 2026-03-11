# DOCTOR OWNER DECISIONS REQUIRED

Дата: 2026-03-11
Статус: pending owner decisions

Основание:
- `docs/ai/DOCTOR_AND_SELFHEAL_AUDIT_2026-03-11.md`
- `docs/ai/FINAL_REMAINING_ACTIONS.md`
- `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`
- `BS24-MASTER-PLAN-v2.0.md`

## Контекст

- Boris production control plane сейчас = custom multi-layer `doctor / monitor / watchdog / self-heal` stack вокруг OpenClaw, n8n и BS24 integrations, а не только official OpenClaw `doctor`.
- Текущий coverage profile по аудиту:
  - strong infra coverage;
  - partial BS24 business-liveness coverage;
  - weak semantic business correctness coverage.
- Ниже только те решения, без которых dangerous auto-repair нельзя расширять, а часть текущих live прав на auto-repair остаётся спорной.

## 1. Нужен ли дальше `S1 n8n-watchdog`, если уже есть `S2 n8n-doctor`

### Текущий live факт

- На `S1` активен `n8n-watchdog.service`.
- На `S2` активен `n8n-doctor.service`.
- Оба контура относятся к `dangerous auto-repair`.
- Оба контура могут трогать один и тот же workflow/webhook surface:
  - webhook registration;
  - workflow active state;
  - repair tasks;
  - payload replay.
- Дополнительно тот же operational surface частично видит `S2 infra-monitor`.

### Риск

- Multi-controller race на одном и том же n8n contour.
- Double repair и взаимоисключающие действия между `S1` и `S2`.
- Изменение business automation state, а не только инфраструктуры.
- Сложный rollback и размытая зона ответственности.

### Варианты решения

1. Оставить оба контура активными с полными правами.
2. Оставить `S2 n8n-doctor` canonical repair contour, а `S1 n8n-watchdog` перевести в observer-only или alert-only.
3. Полностью убрать `S1 n8n-watchdog` из active repair path и оставить только `S2 n8n-doctor`.

### Что рекомендовано

- Рекомендовано убрать dual-control как минимум на уровне repair authority.
- Базовый рекомендуемый вариант: `S2 n8n-doctor` считать единственным active repair contour для n8n, а `S1 n8n-watchdog` либо перевести в observer-only, либо вывести из active path.
- Вариант "оба с полными правами" не рекомендован.

### Что потребует approve

- Любое отключение, демоция или переразделение прав между `S1 n8n-watchdog` и `S2 n8n-doctor`.
- Любое сохранение dual-controller topology как intentional production norm.

## 2. Допустим ли auto full webhook re-register

### Текущий live факт

- `S1 n8n-watchdog` умеет делать auto full webhook re-register.
- Этот же contour умеет full deactivate/activate workflows после repeated webhook failures.
- `S2 n8n-doctor` тоже работает с webhook/workflow repair и payload replay.

### Риск

- Автоматическое массовое изменение webhook lifecycle влияет на BS24 business-liveness contour.
- Возможен ложный repair по transient failure и дальнейшая цепная деградация workflow state.
- Full re-register без owner intent может пересобрать production path шире, чем исходная проблема.

### Варианты решения

1. Оставить full webhook re-register как полностью автономный repair.
2. Разрешить только conditional re-register по узким preconditions и с жёстким scope.
3. Запретить auto full re-register и оставить alert/manual-approve path.

### Что рекомендовано

- Не считать auto full webhook re-register safe default.
- Рекомендуемый вариант: запретить fully automatic full re-register и оставить только manual/approve path.
- Если owner всё же хочет условный auto-repair, он должен быть narrow-scoped, single-contour и документирован как explicit exception.

### Что потребует approve

- Любое право на auto full webhook re-register в production.
- Любой conditional re-register path, если он меняет webhook lifecycle без ручного подтверждения.

## 3. Допустим ли auto-restore от `workspace-validator`

### Текущий live факт

- `workspace-validator` внутри `boris-doctor` уже умеет auto-restore:
  - `RULES.md`;
  - `CLAUDE.md`;
  - missing/small `SKILL.md`;
  - fragments inside `openclaw.json`, включая `channels.telegram` и `messages.groupChat.mentionPatterns`.
- Это restore runtime files напрямую из backup/state layer, а не через явный repo master apply flow.

### Риск

- Runtime-over-master drift: live restore может перезаписать owner intent, если master уже изменился в другом слое.
- Это затрагивает не только infra, но и prompt/rules/skills/config behavior.
- Для BS24 semantic correctness coverage этот contour слишком грубый: он чинит форму файла, но не гарантирует корректность бизнес-смысла.

### Варианты решения

1. Оставить auto-restore для всех перечисленных targets.
2. Оставить auto-restore только для строго ограниченного subset и только при missing/empty corruption.
3. Убрать auto-restore и оставить observer/alert path.

### Что рекомендовано

- Не держать единое правило "auto-restore для всех targets".
- Рекомендуемое разделение:
  - `RULES.md`: максимум conditional repair при `missing/zero-size`, не при content drift.
  - `CLAUDE.md`: observer-only; auto-restore не рекомендован.
  - `SKILL.md`: observer-only; auto-restore не рекомендован.
  - `openclaw.json fragments`: auto-restore не рекомендован; такие изменения должны идти через canonical config writer/master path.

### Что потребует approve

- Любое сохранение auto-restore для `RULES.md`.
- Любое авто-восстановление `CLAUDE.md`, `SKILL.md` или `openclaw.json fragments`.
- Любое расширение списка restore targets внутри `workspace-validator`.

## 4. Допустим ли auto-write в `commitments.json` со стороны `promise-watchdog`

### Текущий live факт

- `promise-watchdog.py` анализирует assistant messages на promise patterns.
- По результату он автоматически добавляет новые commitments в `commitments.json`.
- Контур уже классифицирован как `dangerous auto-repair`.

### Риск

- Это прямое изменение product/internal state, а не инфраструктуры.
- Возможны false positives, дубли, неверные обязательства и искажение операционного журнала.
- Такой repair не улучшает semantic business correctness сам по себе; он лишь закрепляет интерпретацию watchdog.

### Варианты решения

1. Оставить auto-write как есть.
2. Оставить detection, но перевести запись в suggestion/review queue.
3. Полностью убрать auto-write и оставить только alerting.

### Что рекомендовано

- Рекомендуемо убрать autonomous write path.
- Базовый вариант: detection + alert/suggestion без прямой записи в `commitments.json`.
- Если owner хочет сохранить automation, то только через review queue с явным human approval.

### Что потребует approve

- Любое прямое auto-write право в `commitments.json`.
- Любая новая схема commitments auto-enforcement поверх текущего watchdog.

## 5. Допустим ли AI-patch `monitor.sh` через `watchdog-meta`

### Текущий live факт

- `watchdog-meta.sh` на `S1` и `S2` отслеживает freshness/crash-loop `infra-monitor`.
- При проблеме contour может запросить patch у Bridge, применить его к `monitor.sh`, прогнать syntax test, сделать backup/rollback и перезапустить `infra-monitor`.
- Контур уже классифицирован как `dangerous auto-repair`.

### Риск

- Это self-modifying production monitoring code.
- Даже с backup/test/rollback contour меняет саму логику мониторинга, а не только состояние сервиса.
- Ошибка здесь может изменить весь infra control loop и затронуть соседние repairs.

### Варианты решения

1. Оставить AI-patch apply в fully automatic режиме.
2. Разрешить только patch proposal, но не auto-apply.
3. Полностью убрать AI-patch path и оставить safe-mode/alerting.

### Что рекомендовано

- Fully automatic AI-patch apply не рекомендован.
- Рекомендуемый вариант: оставить detection + patch proposal artifact, но запретить auto-apply без человека.
- Safe-mode можно сохранять отдельно от права менять `monitor.sh`.

### Что потребует approve

- Любое сохранение права на autonomous patch/apply для `monitor.sh`.
- Любое расширение AI-patch rights на другие monitoring scripts.

## 6. Какой contour считать каноническим

### Текущий live факт

- Official OpenClaw docs описывают `doctor / cron / heartbeat` как product primitives и CLI-centered troubleshooting path.
- Live Boris production control plane фактически состоит из custom host-side contours:
  - `boris-doctor`;
  - `infra-monitor`;
  - `watchdog-meta`;
  - `service-guard`;
  - `monitor-locks`;
  - `n8n-watchdog`;
  - `n8n-doctor`.
- Official docs не описывают этот Boris production control plane end-to-end.

### Риск

- Если считать canonical только official OpenClaw path, docs и planning снова потеряют реальный production control plane.
- Если считать canonical только Boris custom path, можно потерять связь с product primitives и diagnostic baseline OpenClaw.
- Без явного выбора будет продолжаться терминологический drift и спор о scope у auto-repair.

### Варианты решения

1. Считать canonical только official OpenClaw doctor path.
2. Считать canonical только Boris custom doctor path.
3. Считать canonical hybrid с явным разделением по слоям.

### Что рекомендовано

- Рекомендуемый вариант: `hybrid`, но не как "оба равны".
- Canonical split должен быть таким:
  - official OpenClaw path = canonical source for product primitives;
  - Boris custom doctor path = canonical source for actual production operational control plane.
- Для production remediation, owner decisions и auto-repair boundaries приоритет должен идти от Boris live control plane, а не от abstract official primitive model.

### Что потребует approve

- Любой выбор canonical contour как owner decision.
- Любая server-side перестройка, которая будет подгонять live topology под выбранную каноническую схему.

## Итоговая рамка до owner decision

- Не расширять auto-repair rights.
- Не считать dangerous contours safe-by-default.
- Любые server-side изменения в `monitoring / self-healing` оставлять approve-only.
- До owner decision безопасная docs-позиция остаётся такой:
  - Boris control plane уже больше official OpenClaw doctor path;
  - infra coverage сильное;
  - BS24 business-liveness coverage частичное;
  - semantic business correctness coverage слабое.
