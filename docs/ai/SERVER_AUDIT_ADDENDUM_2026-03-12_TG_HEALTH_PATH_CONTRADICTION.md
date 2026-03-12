# SERVER AUDIT ADDENDUM 2026-03-12: TG HEALTH PATH CONTRADICTION ON S1

## Scope
- Docs-only correction after a read-only audit of the Telegram runtime telemetry contradiction on `S1`.
- No live apply.
- No backup.
- No post-change verification.
- Focus only:
  - exact implementation and data source for Telegram health/status paths
  - authoritative runtime proof for Telegram inbound on `S1`
  - reason of contradiction
  - docs correction needed to avoid future false incident diagnosis

## Executive summary
- Telegram restore apply is not required.
- Current issue class = telemetry issue, not confirmed live outage.
- `openclaw gateway call health --json` is not authoritative for Telegram inbound runtime on `S1`.
- Exact authoritative path for Telegram inbound runtime on `S1`:
  - `openclaw channels status --json --probe`
  - only in successful authenticated gateway context
  - without config-only fallback
- Exact reason of contradiction:
  - `channels.status` reads live runtime snapshot
  - `gateway health` builds a coarse cached summary
  - Telegram runtime fields there are not runtime truth and default to `false/null/none`
- `channels status --probe` config-only fallback is not runtime proof.
- CLI auth/device-signature issues can produce false diagnosis by forcing config-only fallback or by blocking direct gateway RPC checks.
- Telegram restore contour is closed as not needed.
- Next active hardening contour = `/route` closure.

## What was checked
- Repo canon and dated Telegram hardening docs.
- Read-only inspection of live OpenClaw package code on `S1`:
  - `/usr/local/lib/node_modules/openclaw/extensions/telegram/src/channel.ts`
  - `/usr/local/lib/node_modules/openclaw/dist/channels-cli-*.js`
  - `/usr/local/lib/node_modules/openclaw/dist/gateway-cli-*.js`
  - `/usr/local/lib/node_modules/openclaw/dist/health-*.js`
  - `/usr/local/lib/node_modules/openclaw/dist/plugin-sdk/index.js`
  - `/usr/local/lib/node_modules/openclaw/dist/plugins-*.js`
- Read-only live command behavior on `S1` in the current CLI context on `2026-03-12`:
  - `openclaw channels status --json --probe`
  - `openclaw gateway call health --json`
  - direct `channels.status` RPC attempt

## Exact implementation and data source

### `openclaw channels status --json --probe`
- CLI path calls gateway method `channels.status`.
- Gateway method `channels.status` reads `context.getRuntimeSnapshot()`.
- For Telegram, account snapshots are built through Telegram plugin `buildAccountSnapshot()`.
- This path uses live channel-manager runtime state for:
  - `running`
  - `lastStartAt`
  - `lastError`
  - `lastInboundAt`
  - `lastOutboundAt`
- This path uses resolved config/account state for:
  - `enabled`
  - `configured`
  - `tokenSource`
- `mode` comes from runtime when present, with config fallback `webhook|polling`.

### `openclaw gateway call health --json`
- CLI path calls gateway method `health`.
- Gateway method `health` reads `getHealthSnapshot()`.
- `getHealthSnapshot()` builds a gateway-wide coarse channel summary through `buildTokenChannelStatusSummary()`.
- For Telegram on this path, the health snapshot only carries coarse summary inputs such as:
  - `configured`
  - `probe`
  - `lastProbeAt`
- Telegram runtime fields are not populated as runtime truth there, so summary defaults apply:
  - `running=false`
  - `mode=null`
  - `tokenSource=none`
  - `lastStartAt=null`
  - `lastError=null`
- `health` also has a cache path with `HEALTH_REFRESH_INTERVAL_MS = 60000` when `probe` is not requested.

## Exact field meaning for Telegram on S1
- `configured`
  - authoritative in `channels.status`
  - derived from resolved Telegram account/token state and duplicate-token checks
- `enabled`
  - authoritative in `channels.status`
  - derived from `channels.telegram.enabled !== false` plus account-level enable flag
- `running`
  - authoritative only in `channels.status`
  - comes from live runtime snapshot
- `mode`
  - authoritative only in `channels.status`
  - runtime value when present, otherwise config fallback
- `tokenSource`
  - authoritative only in `channels.status`
  - derived from `resolveTelegramToken()` and can be `config|env|tokenFile|none`
- `lastStartAt`
  - authoritative only in `channels.status`
  - comes from live runtime snapshot
- `lastError`
  - authoritative only in `channels.status`
  - comes from live runtime snapshot, with plugin-specific fallback only in account snapshot building

## Exact authoritative health check for Telegram inbound on S1
- Use:
  - `openclaw channels status --json --probe`
- Conditions:
  - the command must successfully reach the authenticated gateway
  - it must not degrade into config-only fallback
- Negative rule:
  - if output says `Gateway not reachable; showing config-only status.`, that output is config visibility only and not runtime proof

## Exact reason of contradiction
- The two paths do not read the same object.
- `channels.status` reads live runtime snapshot for Telegram accounts.
- `gateway health` reads a gateway-wide coarse summary snapshot.
- Telegram runtime lifecycle fields inside `gateway health` are not runtime truth there and therefore default to `false/null/none`.
- Because of that, `gateway health` can show `configured=true` together with `running=false`, `mode=null`, `tokenSource=none` even when Telegram inbound runtime is currently healthy on the authoritative status path.

## CLI auth and false diagnosis
- In the current container CLI context on `2026-03-12`, direct gateway calls hit:
  - `device signature invalid`
- In the same context, `channels status --probe` degraded into config-only status.
- Therefore:
  - CLI auth/device-signature state is a separate operator-context issue
  - it can create false diagnosis if config-only fallback is misread as runtime proof

## Planning result
- Telegram restore contour on `S1` is closed as not needed.
- Current issue class = telemetry issue, not confirmed live outage.
- Do not use `openclaw gateway call health --json` as Telegram runtime proof on `S1`.
- Use `openclaw channels status --json --probe` only in successful authenticated gateway context and without config-only fallback.
- Next active hardening contour = `/route` closure.

## Verdict
- `DOCS_ONLY_CORRECTION`
- `TELEMETRY_ISSUE_CONFIRMED`
- `RESTORE_APPLY_NOT_REQUIRED`
