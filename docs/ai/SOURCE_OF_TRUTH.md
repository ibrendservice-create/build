# SOURCE OF TRUTH

## Базовое правило
- Никогда не считать runtime/generated файл источником истины, если есть master-конфиг, patcher, generator или sync pipeline.

## Канон внутри repo
- Для project instructions и planning source of truth в repo: `docs/ai/OPERATING_CONSENSUS.md`, `docs/ai/PROJECT_MEMORY.md`, `docs/ai/SOURCE_OF_TRUTH.md`, `docs/ai/CHANGE_POLICY.md`, `docs/ai/VERIFICATION_MATRIX.md`, `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`.
- `AGENTS.md` и `CLAUDE.md` это входные project instruction files; они должны вести к одному и тому же канону, а не расходиться с ним.

## Snapshot docs, но не live master
- `docs/ai/HANDOFF_2026-03-10.md` это snapshot и handoff на дату документа.
- `Boris-Detail-Schema.txt` это внешний audit artifact; сырой файл не переносить в repo.
- Эти документы нужны для аудита и поиска пробелов, но не заменяют live master.

## Live truth вне repo
- Live server-side configs, runtime state, workflow state, systemd, nginx/Caddy, database schema, secrets и прочий server-side truth проверяются только вне repo.
- Если факт относится к live-системе и не подтвержден каноном repo, требуется `SERVER_AUDIT_REQUIRED`.

## Перед любой правкой определить
- master source;
- generated/runtime files;
- что нельзя править напрямую;
- что перезаписывается при рестарте, bootstrap, sync или patch;
- можно ли доказать факт по repo docs или нужен server audit.

## Правило конфликта
- Если канон и snapshot docs расходятся, не угадывать.
- Не переписывать snapshot-документы в live truth без server-side verification.
