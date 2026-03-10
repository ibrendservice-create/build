# OPERATING CONSENSUS

## Purpose
Этот файл задает общий канон памяти и общий safety contour для Claude и Codex внутри этого репозитория.

## Scope
- Только repo docs и project instruction files.
- Runtime, server-side truth, live workflows и secrets находятся вне этого repo.
- `docs/ai/HANDOFF_2026-03-10.md` и внешний `Boris-Detail-Schema.txt` используются для аудита, а не как live master.
- `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md` и `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md` это dated audit docs: они фиксируют проверенные live-факты на дату аудита, но не заменяют live master после этой даты.

## Canonical read order
1. `docs/ai/OPERATING_CONSENSUS.md`
2. `docs/ai/PROJECT_MEMORY.md`
3. `docs/ai/SOURCE_OF_TRUTH.md`
4. `docs/ai/CHANGE_POLICY.md`
5. `docs/ai/VERIFICATION_MATRIX.md`
6. `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`
7. `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`
8. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`
9. `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`
10. `docs/ai/HANDOFF_2026-03-10.md`
11. `Boris-Detail-Schema.txt` только если файл явно дан для аудита; сырой файл не копировать в repo.

## Document priority
- `AGENTS.md` и `CLAUDE.md` это agent entry points; они должны ссылаться на один и тот же канон и не расходиться по правилам проекта.
- Канон repo: этот файл плюс `docs/ai/PROJECT_MEMORY.md`, `docs/ai/SOURCE_OF_TRUTH.md`, `docs/ai/CHANGE_POLICY.md`, `docs/ai/VERIFICATION_MATRIX.md`, `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`.
- Dated audit docs: `docs/ai/SERVER_AUDIT_RESULT_2026-03-10_FULL.md`, `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md` и `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_PROMPT_MEMORY.md`.
- Snapshot docs: `docs/ai/HANDOFF_2026-03-10.md` и внешний `Boris-Detail-Schema.txt`.
- Live server-side truth проверяется только вне repo.

## Canon vs snapshots
- Канон определяет правила работы, safety contour и способ чтения памяти.
- Snapshot docs нужны для аудита, инвентаризации и фиксации состояния на дату снимка.
- Snapshot docs нельзя автоматически повышать до source of truth для live-системы.

## Conflict handling
- Если канон и snapshot docs расходятся, не угадывать.
- Если факта нет в repo и он относится к live-системе, не додумывать.
- В таких случаях помечать `SERVER_AUDIT_REQUIRED`.
- Не переписывать snapshot-документы в качестве live truth без server-side verification.
- Если dated audit docs и snapshot docs расходятся по уже проверенному факту, фиксировать drift в каноне и не переписывать snapshot docs.

## Shared safety contour
- сначала проверка, потом изменение;
- сначала source of truth, потом runtime;
- сначала нижний слой, потом верхний;
- только минимальный change set;
- всегда иметь rollback;
- всегда делать post-change verification;
- не читать и не выводить секреты.

## Forbidden without explicit approve
- auth;
- routing;
- gateway;
- bridge;
- monitoring / self-healing;
- workflows и live workflow state;
- server-side truth вне этого repo;
- runtime/generated files вместо master;
- secrets / tokens / credentials;
- restart критичных сервисов или контейнеров;
- destructive actions;
- широкий refactor вне текущей задачи.

## Audit-backed live deltas as of 2026-03-10
- `okdesk-pipeline` live active на S2; `HANDOFF` по этому контуру теперь snapshot drift.
- Internal cron models live = `bridge/claude-opus-4-6`; internal interactive default-chain live = `bridge/claude-sonnet-4-6` с fallback-цепочкой из `model-strategy.json`.
- External live routing = `anthropic/claude-haiku-4-5 -> openai/gpt-5`.
- Live prompt/memory paths: `.openclaw/SOUL.md` отсутствует; live rules source of truth на S1 = `/data/.openclaw/workspace/memory/RULES.md`.
- `/data/.openclaw/memory` в live используется как storage/DB path, а не как rules path.
- `CLAUDE.md` в live не является master-источником правил; он только ссылается на `workspace/memory/RULES.md`.
- Prompt/memory drift сейчас классифицирован как docs drift, а не как подтвержденный runtime failure.
- Live Caddyfile path = `/etc/caddy/Caddyfile`.
- `sites-enabled` на S1 сейчас regular files, не symlink.
- Local health для `8443` проверяется по `http`, не по `https`.
- Docling не публикует host `:5001`, но доступен внутри docker-сети.
- Live workflow statuses, подтвержденные аудитом: WF3 `active`, WF8 relay `active`, WF10 `active`, WF11 `inactive`, WF8 Watchdog `inactive`.
- S1 -> S2 проблема из первого аудита была alias drift; сеть и SSH по IP рабочие.
- Любые server-side изменения prompt/memory layout требуют explicit approve.

## Remaining unresolved contradictions
- Эти audit-backed facts корректны только на дату аудита `2026-03-10`; если задача зависит от их текущего live-состояния позже, требуется `SERVER_AUDIT_REQUIRED`.
- Все неаудированные live-факты из `HANDOFF` и внешней схемы по-прежнему нельзя повышать до master без отдельной проверки.
