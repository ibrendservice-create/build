# SERVER AUDIT ADDENDUM 2026-03-12: BORIS EMPLOYEE ARCHITECTURE

## Scope
- Docs-only architecture/security analysis addendum.
- No live apply was performed by this document.
- Focus only: Boris on `S1` as a full employee agent with self-modification denied and with explicit separation between system core, owner policy, business memory and session memory.

## Executive summary
- Boris is a full employee agent, not a simple chat bot.
- Employee capabilities must be preserved:
  - browser
  - `web_search` / `web_fetch`
  - image analysis
  - business file/doc work
  - OKDesk/business-system actions
  - vendor/client/tender workflows
- Self-modification and self-admin must be denied:
  - no chat path to mutate system core, control-plane or runtime policy
  - no persistent chat path to restart, reconfigure or reroute Boris itself
- Current shared trust boundary remains:
  - one shared conversational/control-plane runtime is still being used in a way that exceeds the official personal-assistant trust model
  - broader architecture hardening is still required even after Wave 0
- What is already closed correctly on the current baseline:
  - `commands.config=false`
  - `commands.restart=false`
  - `channels.telegram.configWrites=false`
  - helper token hardening applied
  - exact morning/evening digest fallback chains applied

## What Boris must keep

### Employee capabilities to preserve
- `browser`
- `web_search`
- `web_fetch`
- `image`
- business file/doc work
- OKDesk/business-system actions
- vendor/client/tender workflows
- business skills/scripts/helper tooling required to complete employee tasks

### Important boundary
- Do not apply blanket-deny that kills Boris employee capabilities.
- Do not confuse business file/doc work with Boris runtime/config mutation.
- Preserve business execution capability while removing Boris self-admin and self-break paths.

## What Boris must never modify

### Self-modification surfaces to deny
- `openclaw.json`
- `jobs.json`
- `model-strategy.json`
- `agents/*/models.json`
- `RULES.md`
- `SKILL.md`
- plugin configs
- hook configs
- runtime config / control files
- restart/config/debug/admin mutation surfaces
- any chat path that rewrites Boris model routing, rules, prompts, approvals or control-plane behavior

### Server-side only surfaces
- system core config
- model strategy and fallback policy
- cron/job topology
- plugins/hooks/control-plane config
- approvals and control boundaries
- monitoring / self-heal / restore contours
- filesystem permissions for Boris runtime/config

### What must not be conflated
- business work
- self-admin
- owner policy
- business memory
- session memory
- system core

## Layer model

### Layer 1: system core
- What belongs here:
  - `RULES.md`
  - critical `openclaw.json` keys
  - model/routing policy
  - jobs / cron topology
  - plugins/hooks/control-plane config
  - approvals and monitoring/self-heal boundaries
- Write path:
  - server-side only
  - approve-only
  - master-first
- Boris conversational access:
  - never chat-writable

### Layer 2: owner policy
- What belongs here:
  - persistent owner guidance about how Boris should work
  - who Boris should obey
  - who Boris should ignore
  - durable operational rules from Timur
- Write path:
  - owner-only persistent path
  - separate from system core
  - separate from business memory
- Boris conversational access:
  - owner-only
  - non-owner chat can propose candidate notes, not apply policy

### Layer 3: business memory
- What belongs here:
  - business facts
  - customer/vendor specifics
  - tender heuristics
  - templates
  - office/operational habits that are safe to recall
- Write path:
  - safe business-memory writer / upsert path
  - not direct editing of system core
- Boris conversational access:
  - may be writable through constrained business-memory tools

### Layer 4: session/task memory
- What belongs here:
  - transient task context
  - conversation summaries
  - `/new` output
- Write path:
  - session-local memory path only
- Boris conversational access:
  - writable, but non-normative
  - must not overwrite owner policy or system core

## Owner authority model
- Timur must be able to persistently define:
  - how Boris should work
  - whom Boris should listen to
  - whom Boris should not listen to
  - which operational rules Boris must follow
- This authority must persist through a separate owner-policy layer, not by rewriting system core.
- Owner policy is not normal semantic business memory.
- Non-owner shared chats must not gain a path to rewrite Layer 1 or Layer 2.

## Memory model
- System core is not business memory.
- Owner policy is not session memory.
- Business memory must be separated from system core and from owner policy.
- Session/task memory is useful, but it is transient and non-normative.
- Safe write paths must follow the layer boundary:
  - Layer 1 -> server-side only
  - Layer 2 -> owner-only
  - Layer 3 -> constrained business-memory writer
  - Layer 4 -> session/task memory writer only

## Remaining shared-risk
- Wave 0 closed the official chat-admin surfaces correctly, but broader architecture hardening is still required.
- Current shared trust boundary remains:
  - shared conversational access still lives on a runtime that also contains control-plane and mixed memory surfaces
  - Boris still operates on one shared gateway/runtime model that is not a strong multi-tenant trust boundary
- Current architecture still lacks:
  - formal separation between owner policy and business memory
  - formal separation between business file work and Boris system-core mutation surfaces
  - a dedicated employee workspace/safe business file tooling contour
  - stronger per-agent hardening of `main` without collateral impact to cron
- Stronger per-agent hardening of `main` must wait until cron is split off `main`.

## Next architecture waves
- `cron split off main`
- `owner policy layer`
- `business memory writer`
- `employee workspace / safe business file tooling`
- `self-modification deny without killing employee capabilities`
- later model exposure narrowing for shared chats

## Key decisions to preserve
- Boris must keep employee hands.
- Boris must not keep self-admin hands.
- Owner authority must persist through a separate owner-policy layer.
- Business memory must be separated from system core.
- `cron split off main` is required before stronger per-agent hardening of `main`.
- Shared trust boundary remains until business workspace separation and control-plane separation are completed.

## Status
- Architecture/security analysis: documented.
- Live apply: not performed.
- Next server-side work: separate approved waves only.
