# SKILL AUTHORING POLICY

## Scope
- Docs-only policy for future server-side Boris skill authoring.
- This document defines repo canon for attachment/file skill examples and helper usage.
- It does not perform or authorize any live apply by itself.

## Canonical layers
- Live canonical rule layer on `S1` for attachment/file handling = `/data/.openclaw/workspace/memory/RULES.md`.
- `CLAUDE.md` is not the live master for this contour; it is only an operational context file.
- Repo authoring entry point = `docs/ai/CODEX_PLAYBOOK.md`.
- This file is the detailed repo policy for future `SKILL.md` and related helper authoring.

## Mandatory rules for inbound attachments
- Raw inbound path `/data/.openclaw/media/inbound/*` must never be used as a working path in new skills, examples or helper instructions.
- If the source file is an inbound attachment under `/data/.openclaw/media/inbound/*`, staging is mandatory before any `read`, `write`, `edit`, `apply_patch`, `exec` or `process`.
- Required staging command:
  - `python3 /data/scripts/stage-inbound-media.py SOURCE_PATH`
- After staging, only `/data/.openclaw/workspace/downloads/inbound/*` may be used as the working path.
- Skills must not show raw inbound paths as the final `USED_PATH`, example path, or extract/read target.

## Parser naming and helper rules
- `parse-attachment` is forbidden for new skills and new helper instructions.
- Canonical parser name for this class = `parse-file`.
- If a helper accepts an arbitrary file path, the skill must explicitly require staging first for inbound attachments before passing that path into the helper.
- A generic helper example such as `extract PATH_TO_FILE` is not sufficient for inbound attachments unless the same skill text makes the staging precondition explicit.

## Authoring guidance
- Prefer skill examples that operate on:
  - staged inbound files under `/data/.openclaw/workspace/downloads/inbound/*`;
  - approved non-inbound sources such as Okdesk attachments, email attachments, URLs, base64, or already-approved workspace paths.
- Do not normalize raw inbound examples in `SKILL.md`, helper instructions, snippets, or templates.
- If a skill is attachment-aware but does not own attachment ingress, it must delegate to the canonical parser/path flow instead of inventing its own raw inbound example.

## Recommended check rule
- Future repo lint/check for skill authoring should fail on:
  - `/data/.openclaw/media/inbound/`
  - `parse-attachment`
  - raw inbound examples passed directly into extract/read helpers
- This check should target skill/helper authoring sources, not audit docs or changelogs.

## Status
- Canonical repo policy for future skill authoring: active.
- Live corrective applies for existing risky skills/helpers remain separate approved waves.
