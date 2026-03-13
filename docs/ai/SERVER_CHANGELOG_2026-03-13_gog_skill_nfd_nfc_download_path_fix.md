# SERVER CHANGELOG 2026-03-13: GOG SKILL NFD/NFC DOWNLOAD PATH FIX

## Layer
- `S1` internal OpenClaw `gog` skill text

## Scope
- One file: `/var/lib/apps-data/openclaw/data/.openclaw/workspace/skills/gog/SKILL.md`
- Content-only edit in `### Download file` section
- No restart, no locale change, no binary change, no openclaw.json change

## Root cause addressed
- Google Drive API returns Cyrillic filenames in Unicode NFD form (й = U+0438 + U+0306)
- `gog` saves files with NFD filename verbatim to `~/.config/gogcli/drive-downloads/`
- Boris (LLM) reconstructs paths using NFC form (й = U+0439)
- Linux filesystem is byte-exact: NFC ≠ NFD → ENOENT
- Symptom: `cp: cannot stat ... No such file or directory` on downloaded Cyrillic-named files
- Fresh symptom observed in session `a9339b83` (2026-03-13, TENDER chat flow)

## What changed
- Added WARNING block after `### Download file` code example
- WARNING makes `--out /tmp/<ascii_name>.<ext>` mandatory for downloads
- WARNING forbids relying on default download path by reconstructed Cyrillic filename
- WARNING provides `find` by file-ID prefix as fallback if `--out` was not used

## Pre-hash / Post-hash
- Pre: `776685c67c96c01776bd14bc65bd0afd85aac398a84dec0be32274185fdab63a` (2583 bytes)
- Post: `a754678a30db79cb09b6835f12fe8a8f6f661654d07eb54fcc73c21b4a7ea3da` (3039 bytes)

## Backup
- Container: `/tmp/gog-SKILL.md.bak-nfd-fix-20260313`
- Host: `/root/gog-SKILL.md.bak-nfd-fix-20260313`

## Post-check
- Patched section correct
- All adjacent sections intact (frontmatter, upload, delete, Gmail, Calendar, Sheets, Docs, Contacts)
- WARNING count: 2 → 3 (one added)

## Validator convergence
- Manual `workspace-validator.py` run: 18 OK, 1 WARN, 0 FAIL
- Section [13] Skills backup: 22 SKILL.md files backed up (not restored = validator accepted edit)
- Validator backup hash converged to post-hash: `a754678a...`
- Validator will not revert (copies live → backup for files > 50 bytes; no hash-based restore for SKILL.md)

## Canary
- Session `6a152919` (appended), 2026-03-13T16:07 UTC+3
- Boris read updated SKILL.md with new WARNING
- Boris used `--out`: exact command = `gog drive download 1TqIM_hYDo97nD1wbfP8C9B50bmUye2tK --out /tmp/canary_nfd_test.xlsx`
- Download succeeded: `path /tmp/canary_nfd_test.xlsx, size 33.4 KB`
- `openpyxl.load_workbook` succeeded: sheets `['улица', 'островок']`
- Zero `No such file or directory` / `ENOENT` / `cannot stat` in canary trace
- Boris self-reported success

## Diagnostic evidence (read-only, pre-apply)
- Disk filename bytes: NFD `d0 b8 cc 86` for й (confirmed via `find -print0 | od`)
- Command string bytes: NFC `d0 b9` for й (confirmed via `printf | od`)
- Google Drive API metadata: codepoints `0x438, 0x306` (confirmed via `gog drive get --json`)
- NFD mismatch count in `drive-downloads/`: 1 of 58 files (only files with decomposable Cyrillic chars affected)
- Container locale: POSIX (no UTF-8 normalization)
- `--out` flag proven to bypass the problem completely

## What stayed out of scope
- locale / container env
- gog binary
- openclaw.json / exec tool
- parse-file / tender-specialist / other skills
- jobs.json / cron layer
- bridge / routing / monitoring

## Relationship to other contours
- Separate from CLOSED `exec-denied-via-bash-alias` (that was `bash` → `exec` alias in `tools.deny`)
- Separate from CLOSED `parse-file exec-first/staging-first` (that was inbound attachment staging)
- Separate from CLOSED `gog closeout` (that proved read-only gog paths; download+reference was not in scope)
- Does not reopen any CLOSED contour

## Rollback required or not
- `Rollback required` = `no`

## Result
- `successful`
- Contour `gog/SKILL.md NFD/NFC download path avoidance` = CLOSED
