# SERVER AUDIT CHECKLIST

## Цель
Безопасно провести server-side аудит S1/S2 в режиме read-only, проверить нижние слои раньше верхних и подтвердить или опровергнуть live-факты из `docs/ai/HANDOFF_2026-03-10.md` и внешнего `Boris-Detail-Schema.txt`.

## Режим только read-only
- Разрешены только чтение, инвентаризация, `health-check`, просмотр статусов, логов и `SELECT`.
- Идти строго снизу вверх: если нижний слой сломан, верхние не считать достоверными.
- При конфликте repo docs и live-фактов не угадывать, а помечать `SERVER_AUDIT_REQUIRED`.

## Что запрещено во время аудита
- Любые изменения runtime, server-side truth, workflows и конфигов.
- Любые `restart`, `enable`, `disable`, `edit`, `sed -i`, `docker compose up/down`, `systemctl restart`.
- Любые `UPDATE`, `DELETE`, `INSERT`, `ALTER`, destructive SQL.
- Чтение или вывод секретов, токенов, credential contents.
- Любые правки `auth`, `routing`, `gateway`, `bridge`, `monitoring`, `self-healing`.

## Порядок аудита
1. Сеть и доступы
2. Контейнеры и процессы
3. Model routing
4. Prompts / memory / skills
5. Bridge / gateway
6. Monitoring / self-healing
7. Cron / jobs
8. Интеграции

## Слой: сеть и доступы
**Что проверять**
- Доступность S1/S2.
- SSH-порты, базовые ресурсы, listening ports.
- Стандарт директорий и symlink-и.
- Базовую связность S1->S2.
- Отдельно отличать alias-проверку `ssh s2` от реальной live-проверки по IP.

**Команды**
```bash
ssh s1 'hostname -f; date -Is; uptime; df -h / /var/lib/apps-data; free -h'
ssh s2 'hostname -f; date -Is; uptime; df -h / /var/lib/apps-data; free -h'
ssh s1 'ss -ltn | egrep ":58536|:80|:443|:8443|:3100|:3102|:15432|:55228|:18790"'
ssh s2 'ss -ltn | egrep ":22|:80|:443|:5678|:5001|:15432|:3300|:3301|:3200|:3100"'
ssh s1 'stat -c "%a %U:%G %n" /etc/apps/secrets; readlink -f /docker/openclaw-kbxr /opt/knowledge-bus /opt/claude-bridge /opt/okdesk-pipeline /opt/ops-hub'
ssh s2 'stat -c "%a %U:%G %n" /etc/apps/secrets; readlink -f /opt/app /opt/knowledge-bus /opt/claude-bridge /opt/n8n-doctor /opt/okdesk-executors'
ssh s1 'timeout 5 ssh -o BatchMode=yes s2 "hostname -f" || true'
ssh s1 'ip route get 72.56.98.52'
ssh s1 'nc -zvw5 72.56.98.52 22'
ssh s1 'timeout 7 ssh -o BatchMode=yes -o PreferredAuthentications=publickey -o ConnectTimeout=5 root@72.56.98.52 "hostname -f"'
```

**Примечание**
- `ssh s2` зависит от локального alias или DNS и не считается надёжной live-проверкой сам по себе.
- Для S1 -> S2 каноническая read-only проверка связности: маршрут до `72.56.98.52`, TCP-доступ к `72.56.98.52:22` и SSH по IP `root@72.56.98.52`.
- Если `ssh s2` не работает, но маршрут, TCP и SSH по IP рабочие, это `WARN` по alias/drift, а не `FAIL` по сети.

**Норма**
- SSH доступ есть.
- Ожидаемые порты слушают.
- `S1 /etc/apps/secrets` имеет `711`, `S2` `751`.
- Symlink-и ведут в `/opt/apps/*`.
- S1->S2 доступ по IP `72.56.98.52` работает.
- Диск S2 не в критической зоне.

**Красные флаги**
- Недоступен SSH.
- Нет порта `8443`, `3100`, `5678` или `15432`.
- Сломанные symlink-и.
- `secrets` dir mode не совпадает.
- S2 диск близок к заполнению.
- Нет маршрута до `72.56.98.52`.
- Нет TCP-доступа до `72.56.98.52:22`.
- SSH по IP `root@72.56.98.52` не работает.
- `ssh s2` не работает при рабочем IP-пути: это alias/drift `WARN`, а не сетевой `FAIL`.

## Слой: контейнеры и процессы
**Что проверять**
- Состав контейнеров на S1/S2.
- Статус systemd-сервисов.
- Health и restart status.
- Отсутствие restart loop.

**Команды**
```bash
ssh s1 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
ssh s2 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
ssh s1 'systemctl --no-pager --type=service --state=running | egrep "claude-bridge|openai-bridge|openclaw-agent-bridge|nginx|infra-monitor|boris-doctor|openclaw-hooks-proxy"'
ssh s2 'systemctl --no-pager --type=service --state=running | egrep "caddy|infra-monitor|n8n-doctor|claude-bridge|okdesk-pipeline"'
ssh s1 'docker inspect -f "{{.Name}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}" openclaw-kbxr-openclaw-1 openclaw-ext-openclaw-1 boris-emails-pg-1'
ssh s2 'docker inspect -f "{{.Name}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}" app-n8n-1 app-n8n-worker-1 app-db-1 app-cache-1 app-docling-1'
```

**Норма**
- Все критичные контейнеры `Up`.
- Health это `healthy` или `none`.
- Критичные systemd-сервисы `active`.
- Нет restart loop.

**Красные флаги**
- Контейнеры `Restarting` или `Exited`.
- Health `unhealthy`.
- Отсутствует ожидаемый сервис.
- Жив неожиданный legacy-процесс, конфликтующий с текущей схемой.

## Слой: model routing
**Что проверять**
- Наличие `model-strategy.json`.
- Согласованность `model-strategy.json -> openclaw.json -> jobs.json`.
- Модельные цепочки internal/external.
- Cron model и config drift.

**Команды**
```bash
ssh s1 'ls -l /var/lib/apps-data/openclaw/data/model-strategy.json /var/lib/apps-data/openclaw/data/.openclaw/openclaw.json /var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json /var/lib/apps-data/openclaw-external/data/.openclaw/openclaw.json'
ssh s1 'jq "{primary:.primary, fallbacks:.fallbacks, providers:(.providers|keys)}" /var/lib/apps-data/openclaw/data/model-strategy.json'
ssh s1 'jq "{defaults:.agents.defaults.model, providers:(.models.providers|keys)}" /var/lib/apps-data/openclaw/data/.openclaw/openclaw.json'
ssh s1 'jq "[.jobs[] | {name:.name, schedule:.schedule, model:(.payload.model // .model // null)}]" /var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json'
ssh s1 'jq "{defaults:.agents.defaults.model, providers:(.models.providers|keys)}" /var/lib/apps-data/openclaw-external/data/.openclaw/openclaw.json'
```

**Норма**
- `model-strategy.json` существует.
- `openclaw.json` и `jobs.json` не противоречат strategy по primary, fallback и providers.
- Cron использует bridge-модель, если так устроен live-контур.
- Internal и external конфиги внутренне согласованы.

**Красные флаги**
- Отсутствует `model-strategy.json`.
- Providers или fallbacks расходятся между файлами.
- Cron указывает прямой `anthropic/*` вместо bridge при текущем контуре.
- External/internal конфиги расходятся с собственной strategy chain.

## Слой: prompts / memory / skills
**Что проверять**
- Наличие core prompt/memory файлов.
- Возможный drift между двумя путями `RULES.md`.
- Инвентарь skills и scripts.
- Базовые telegram/chat настройки без вывода секретов.

**Команды**
```bash
ssh s1 'for p in /var/lib/apps-data/openclaw/data/.openclaw/SOUL.md /var/lib/apps-data/openclaw/data/CLAUDE.md /var/lib/apps-data/openclaw/data/.openclaw/memory /var/lib/apps-data/openclaw/data/.openclaw/workspace/memory; do [ -e "$p" ] && ls -ld "$p"; done'
ssh s1 'for p in /var/lib/apps-data/openclaw/data/.openclaw/memory/RULES.md /var/lib/apps-data/openclaw/data/.openclaw/workspace/memory/RULES.md; do [ -e "$p" ] && { wc -l "$p"; sha256sum "$p"; }; done'
ssh s1 'find /var/lib/apps-data/openclaw/data/.openclaw/workspace/skills -maxdepth 2 -name SKILL.md | wc -l'
ssh s1 'find /var/lib/apps-data/openclaw/data/scripts -maxdepth 1 -type f | wc -l'
ssh s1 'jq "{dmPolicy:.channels.telegram.dmPolicy, groupPolicy:.channels.telegram.groupPolicy, mentionPatterns:.messages.groupChat.mentionPatterns, ackReactionScope:.messages.ackReactionScope}" /var/lib/apps-data/openclaw/data/.openclaw/openclaw.json'
```

**Норма**
- Core prompt/memory файлы существуют.
- Если `RULES.md` есть по двум путям, их хеши совпадают или один путь явно не используется.
- Skills и scripts не пустые.
- Telegram и mention settings читаются из ожидаемых путей.

**Красные флаги**
- Отсутствует `SOUL.md` или `RULES.md`.
- Две копии `RULES.md` с разным hash.
- Пустой skills dir.
- Mention patterns исчезли или переехали в неожиданный путь.

## Слой: bridge / gateway
**Что проверять**
- Состояние `claude-bridge`, `openai-bridge`, `agent-bridge`, nginx и Caddy.
- Health endpoints.
- `sites-enabled` как symlink.
- Фактический путь hooks.

**Команды**
```bash
ssh s1 'systemctl is-active claude-bridge openai-bridge openclaw-agent-bridge nginx'
ssh s2 'systemctl is-active claude-bridge caddy'
ssh s1 'ss -ltnp | egrep ":8443|:3100|:3102|:55228|:18790"'
ssh s1 'curl -ksS https://127.0.0.1:8443/health; echo; curl -sS http://127.0.0.1:3100/health; echo; curl -sS http://127.0.0.1:3102/health; echo'
ssh s2 'curl -ksS https://n8n.brendservice24.ru/bridge-ha/health; echo'
ssh s1 'grep -R "location /webhook/\\|location /hooks/\\|location /openai/v1/\\|location /agent-notify" /etc/nginx/sites-enabled'
ssh s2 'grep -n "/bridge-ha/\\|/boris-agent/\\|/pipeline/\\|/webhook/boris-mention" /opt/app/Caddyfile'
ssh s1 'readlink -f /etc/nginx/sites-enabled/claude-bridge /etc/nginx/sites-enabled/n8n-public-edge'
```

**Норма**
- `8443`, `3100`, `3102`, `55228`, `18790` слушают.
- Health endpoints отвечают.
- `openai-bridge` health показывает `ok`.
- `sites-enabled` это symlink-и.
- `/hooks/` смотрит на актуальный gateway path, не на legacy bridge.

**Красные флаги**
- `codex_auth:false`.
- `8443` или `3100` не отвечает.
- `sites-enabled` это копия, не symlink.
- `/hooks/` указывает на legacy `socat`.
- `bridge-ha` не работает или даёт `5xx`.

## Слой: monitoring / self-healing
**Что проверять**
- `infra-monitor`, `boris-doctor`, `n8n-doctor`, `fail2ban`.
- Heartbeat и state files.
- Restart counts.
- Признаки crash-loop или бесконечного auto-fix.

**Команды**
```bash
ssh s1 'systemctl is-active infra-monitor boris-doctor fail2ban'
ssh s2 'systemctl is-active infra-monitor n8n-doctor'
ssh s1 'systemctl show infra-monitor boris-doctor --property=ActiveState,SubState,NRestarts,ExecMainStartTimestamp'
ssh s2 'systemctl show infra-monitor n8n-doctor --property=ActiveState,SubState,NRestarts,ExecMainStartTimestamp'
ssh s1 'journalctl -u infra-monitor -S -2h --no-pager | tail -n 50'
ssh s2 'journalctl -u infra-monitor -S -2h --no-pager | tail -n 50'
ssh s1 'find /opt/infra-monitor/state -maxdepth 1 -type f -printf "%TY-%Tm-%Td %TH:%TM %p\n" | sort | tail -n 20'
```

**Норма**
- `infra-monitor` и doctor-сервисы `active`.
- Heartbeat и state файлы обновляются.
- `NRestarts` не растёт аномально.
- В journal нет повторяющихся recover/restart циклов.

**Красные флаги**
- Stale heartbeat.
- Monitor или doctor inactive.
- Много рестартов за короткий интервал.
- Логи полны одинаковых auto-fix событий.
- Safe-mode или cooldown не выходит из активного состояния.

## Слой: cron / jobs
**Что проверять**
- OpenClaw `jobs.json`.
- Host crontab на S1/S2.
- Systemd timers.
- `lastStatus`, `lastRunAtMs`, `consecutiveErrors`.
- Критичные sync, backup и watchdog job-ы.

**Команды**
```bash
ssh s1 'crontab -l'
ssh s2 'crontab -l'
ssh s1 'systemctl list-timers --all | egrep "boris-email-router|chief-doctor"'
ssh s2 'systemctl list-timers --all | egrep "email-categorizer|n8n-reviewer"'
ssh s1 'jq ".jobs | length" /var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json'
ssh s1 'jq ".jobs[] | {name:.name, lastStatus:.state.lastStatus, lastRunAtMs:.state.lastRunAtMs, nextRunAtMs:.state.nextRunAtMs, consecutiveErrors:.state.consecutiveErrors}" /var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json'
ssh s1 'jq ".jobs[] | select(.payload.prompt != null) | .name" /var/lib/apps-data/openclaw/data/.openclaw/cron/jobs.json'
```

**Норма**
- `jobs.json` читается.
- Ожидаемое число jobs похоже на live-конфигурацию.
- State хранится в `lastRunAtMs` и `lastStatus`.
- Backup, sync и watchdog cron-ы и timers присутствуют.
- `consecutiveErrors` не копится по критичным job-ам.

**Красные флаги**
- Отсутствует `jobs.json`.
- Jobs используют `payload.prompt`.
- Пропали `sync-pg-from-s2.sh`, `sync-executors-from-s2.sh`, `backup-full.sh`, `watchdog-meta.sh`.
- Массовые `consecutiveErrors`.
- Ожидаемые timers отсутствуют.

## Слой: интеграции
**Что проверять**
- Реальное местоположение и статус `okdesk-pipeline`.
- n8n stack.
- Active flags workflows.
- DB counts для `emails`, `technicians`, `mem_events`.
- Интеграционные порты и возможный desync между S1/S2.

**Команды**
```bash
ssh s1 'ls -ld /opt/okdesk-pipeline /opt/apps/okdesk-pipeline 2>/dev/null; systemctl status okdesk-pipeline --no-pager --lines=0 || true; ss -ltn | grep ":3200" || true'
ssh s2 'ls -ld /opt/okdesk-pipeline /opt/apps/okdesk-pipeline 2>/dev/null; systemctl status okdesk-pipeline --no-pager --lines=0 || true; ss -ltn | grep ":3200" || true'
ssh s2 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | egrep "app-n8n|app-db|app-cache|app-docling|img2pdf|pdf2img|office2pdf|bs24-api|bs24-miniapp"'
ssh s2 'docker exec app-db-1 psql -U postgres -d n8n -Atc "select name,active from workflow_entity order by name" | egrep "WF3|WF8|WF10|WF11|Telegram Logger|Email|Watchdog"'
ssh s2 'docker exec app-db-1 psql -U postgres -d emails -Atc "select count(*) from emails; select count(*) from technicians;"'
ssh s1 'docker exec boris-emails-pg-1 psql -U postgres -d emails -Atc "select count(*) from mem_events;"'
ssh s2 'ss -ltn | egrep ":5678|:5001|:3300|:3301|:15432|:3200"'
```

**Норма**
- `okdesk-pipeline` локализован однозначно на одном live-контуре.
- n8n, DB, Redis, Docling и BS24-контейнеры живы.
- Workflow active flags читаются из live DB.
- `emails`, `technicians`, `mem_events` доступны и не пустые.
- Все интеграционные порты слушают.

**Красные флаги**
- `okdesk-pipeline` отсутствует на обоих серверах или "как будто есть" на обоих.
- Workflow flags противоречат ingress-контуру.
- `technicians` или `mem_events` пустеют или не читаются.
- Docling, n8n или API-порты не слушают.
- Есть явный desync между S1 и S2.

## Правило остановки аудита
- Если нижний слой не прошёл, верхние слои не считать достоверными.
- Если обнаружен конфликт между `HANDOFF`, схемой и live-фактом, фиксировать это как `SERVER_AUDIT_REQUIRED`.
- Во время аудита не исправлять проблему на месте.
