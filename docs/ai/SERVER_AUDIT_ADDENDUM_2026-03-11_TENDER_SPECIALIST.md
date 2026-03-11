# SERVER AUDIT ADDENDUM 2026-03-11 TENDER SPECIALIST

## Где найден skill

- На `S1` как server-side Boris skill:
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/skills/tender-specialist/SKILL.md`
- Это не repo-local skill и не `.claude/agents/*`.
- Это live skill-layer Boris/OpenClaw на `S1`.

## Какие связанные файлы участвуют

- Основной orchestration file:
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/skills/tender-specialist/SKILL.md`
- Основные helper scripts:
  - `/var/lib/apps-data/openclaw/data/scripts/tender-analysis-helper.py`
  - `/var/lib/apps-data/openclaw/data/scripts/parse-tender-email.py`
- Связанные server-side skills:
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/skills/email-handler/SKILL.md`
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/skills/parse-file/SKILL.md`
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/skills/find-executor/SKILL.md`
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/skills/okdesk/SKILL.md`
  - `/var/lib/apps-data/openclaw/data/.openclaw/workspace/skills/contractor-search/SKILL.md`

## Почему это skill + script, а не pure skill

- `tender-specialist/SKILL.md` выполняет роль диалогового orchestration layer:
  - понимает trigger из чата ТЕНДЕР и button actions;
  - выбирает, какой helper запускать;
  - формирует итоговый ответ человеку;
  - ведёт natural chat вокруг черновиков и решения по тендеру.
- Тяжёлая бизнес-логика уже вынесена в scripts:
  - `tender-analysis-helper.py` делает enrich/analyze/docs/decide/list-pending/remind/stats;
  - `parse-tender-email.py` делает structured extraction из email body;
  - `find-executor`, `okdesk`, `contractor-search`, `parse-file` закрывают соседние подзадачи.
- Для BS24 это правильнее, чем pure skill:
  - skill остаётся тонким orchestration layer;
  - stateful/операционная логика живёт в scripts;
  - риск поломки Boris/OpenClaw ниже, чем если в `SKILL.md` держать весь бизнес-процесс.

## Что в нём правильно

- Skill уже оформлен в ожидаемом OpenClaw-style contour:
  - отдельная папка skill;
  - `SKILL.md` как orchestration entrypoint;
  - heavy logic вынесена в scripts.
- Логика соответствует BS24 domain:
  - FM/ТО/клининг/СМР профиль;
  - выбор юрлица;
  - проверка заказчика;
  - проверка покрытия техниками;
  - письмо-уточнение и natural dialog.
- Skill не пытается быть cron или workflow.
- `tender-analysis-helper.py` уже имеет явный CLI surface и покрывает ключевые операции, то есть contour технически ближе к `skill + script`, а не к "большому prompt без инструмента".

## Какие 3 точечные правки нужны

### 1. `parse-attachment` -> `parse-file`
- В `tender-specialist/SKILL.md` есть ссылка на несуществующий skill `parse-attachment`.
- На live `S1` существует `parse-file`, и именно он соответствует текущему file parsing contour.
- Это прямой docs/runtime mismatch внутри skill.

### 2. Убрать опасную формулировку про "видишь все сообщения пользователей и сам решаешь"
- Текущая формулировка в skill слишком широкая и размывает boundary.
- Для Boris/OpenClaw безопаснее явно сузить контур:
  - чат ТЕНДЕР;
  - tender-related dialog;
  - button actions / explicit tender context;
  - без имплицитного права "сам решать всё".
- Иначе skill выглядит как mini-router поверх соседних contours.

### 3. Явно прописать do-not-touch boundary
- В skill сейчас не хватает явного запрета залезать в:
  - routing;
  - workflows;
  - bridge;
  - monitoring;
  - model files;
  - `jobs.json` / live cron layer.
- Для текущей архитектуры Бориса это важно, потому что skill работает рядом с критичными contours, но не должен их менять или трактовать как свой scope.

## Почему это low-risk server-side change

- Правки точечные и локализованы в одном file:
  - `tender-specialist/SKILL.md`
- Не требуют изменения:
  - scripts;
  - `jobs.json`;
  - model files;
  - workflows;
  - bridge;
  - monitoring;
  - routing.
- Контур уже правильно split на `skill + script`, поэтому нужен не refactor, а только hygiene patch в orchestration text.
- По `docs/ai/CHANGE_WINDOWS.md` это попадает в `low-risk server changes`, но только в рабочее окно:
  - будни;
  - `12:00–15:00 MSK`.

## Что нельзя трогать

- `tender-analysis-helper.py`, кроме отдельной задачи.
- `parse-tender-email.py`, кроме отдельной задачи.
- `email-handler` routing logic.
- `bridge`, `agent-bridge`, ingress, webhook routes.
- `n8n` workflows и workflow state.
- `monitoring / self-healing`.
- `model files`.
- `jobs.json`.
- Любые secrets / tokens / SMTP creds / DB creds.

## Вердикт

- `tender-specialist` живёт на `S1` как server-side Boris skill.
- Его текущий правильный архитектурный класс = `skill + script`, не pure skill и не cron-first contour.
- В целом contour устроен правильно для BS24 и не требует расширения scope.
- Нужны только 3 точечные правки в `SKILL.md`:
  - `parse-attachment -> parse-file`
  - убрать опасную широкую формулировку про полный контроль над сообщениями
  - явно прописать do-not-touch boundary
- Apply пока не делался.
- Изменение отложено до `low-risk change window`.
