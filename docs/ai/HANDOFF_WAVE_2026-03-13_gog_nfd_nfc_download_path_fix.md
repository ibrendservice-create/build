# HANDOFF WAVE 2026-03-13: GOG NFD/NFC DOWNLOAD PATH FIX

## Contour
- `gog/SKILL.md default download path avoidance for Unicode NFD/NFC filenames`

## Classification
- Server-side apply + canary proof (prompt type `E` completed)

## Status
- **CLOSED**

## What is proven [LIVE]
- Root cause: Google Drive API returns NFD Cyrillic filenames; `gog` saves NFD verbatim; Boris reconstructs path in NFC; Linux fs is byte-exact → ENOENT
- Disk bytes for `й`: NFD `d0 b8 cc 86` (и + combining breve); command bytes: NFC `d0 b9`
- `--out /tmp/<ascii>.<ext>` completely bypasses the problem
- Apply: one WARNING added to `gog/SKILL.md` `### Download file` section
- Pre-hash: `776685c6...` (2583 B) → post-hash: `a754678a...` (3039 B)
- workspace-validator convergence: 18 OK, 1 WARN, 0 FAIL; backup converged to new hash
- Canary (session `6a152919`, 2026-03-13T16:07): Boris read new WARNING, used `--out`, download+openpyxl succeeded, zero ENOENT
- No restart performed

## What is [DOCS] only
- This wave handoff and SERVER_CHANGELOG in repo

## What remains [UNKNOWN]
- Nothing for this contour

## Relationship to other contours
- Separate from CLOSED `exec-denied-via-bash-alias`
- Separate from CLOSED `parse-file exec-first/staging-first`
- Separate from CLOSED `gog closeout`
- Does not reopen any CLOSED contour

## Guardrail
- `gog/SKILL.md` download section WARNING must not be removed; without it Boris will revert to constructing default download paths with NFC Cyrillic → ENOENT recurrence
