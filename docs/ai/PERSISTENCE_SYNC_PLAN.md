# PERSISTENCE SYNC PLAN

Дата: 2026-03-11
Статус: docs-only persistence assessment

## Слой

- host-level server-side persistence
- writer / enforcer / restorer risk around already applied live changes
- only repo-visible facts from dated audits and changelogs

## Source of truth

- `docs/ai/OPERATING_CONSENSUS.md`
- `docs/ai/SOURCE_OF_TRUTH.md`
- `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md`
- `docs/ai/DOCTOR_AND_SELFHEAL_AUDIT_2026-03-11.md`
- `docs/ai/FINAL_REMAINING_ACTIONS.md`
- `docs/ai/SERVER_REMEDIATION_BACKLOG.md`
- `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_S1_S2_ALIAS.md`
- `docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_CRON_TIMERS.md`
- `docs/ai/SERVER_CHANGELOG_2026-03-10_DISABLE_STALE_TIMERS.md`
- `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`

## Риск

- `WARN`
- Главный риск здесь не в уже сделанных low-risk applies, а в том, что future planning может ошибочно считать их либо:
  - полностью immortal без проверки writer chain;
  - либо, наоборот, зависимыми от Boris fixers, хотя repo-visible evidence этого не подтверждает.
- Эта оценка repo-visible only.
- Если нужен ответ про host reprovision, package management или иной вне-repo bootstrap, это уже не repo-visible truth и требует `SERVER_AUDIT_REQUIRED`.

## Какие изменения уже были сделаны

Подтверждённые server-side applies в этих сессиях:

1. На `S1` в `/root/.ssh/config` добавлен alias block:
   - `Host s2`
   - `HostName 72.56.98.52`
   - `User root`
2. На `S1` выполнен `safe disable` для `boris-email-router.timer`.
3. На `S1` выполнен `safe disable` для `chief-doctor.timer`.

Что не включено в этот persistence plan как server-side change:

- docs-only updates в repo;
- repo implementation `observer-doctor`;
- ephemeral live-checks через `ssh s1 ... < scripts/observer_doctor.py`, потому что это report-only запуск без deploy и без persistent target.

## Matrix

| change | target | master/runtime | overwritten by | survives restart? | what must be synced |
|---|---|---|---|---|---|
| `S1 ssh alias s2` | `/root/.ssh/config` block `Host s2` | live host file itself is current master; not repo-derived and not Boris runtime | no repo-visible active writer/enforcer confirmed; only future manual SSH config edits, host bootstrap/reprovision, or external config management outside repo | `Boris restart=yes`; `startup fixer=yes`; `doctor/monitor/self-heal=yes` repo-visible; `full host reprovision=unknown` | nothing to sync into Boris startup/fixer/doctor/monitor/service-guard layers; only optional sync into host bootstrap/config-management outside repo if owner wants rebuild persistence |
| `disable boris-email-router.timer` | `S1` systemd enablement/state for `boris-email-router.timer` | persistent host systemd state; unit definition itself was not changed; not Boris runtime | no repo-visible Boris writer/enforcer confirmed; future manual `systemctl`, unit/package management, or external host bootstrap outside repo may re-enable | `Boris restart=yes`; `startup fixer=yes`; `doctor/monitor/self-heal=likely yes`; `full host reboot=likely yes because disabled state is persistent`; `host reprovision=unknown` | no sync into `jobs.json`, `crontab`, service files, startup fixers, doctor/monitor, or `service-guard` baseline is repo-confirmed; if drift appears, sync only at host systemd/bootstrap layer |
| `disable chief-doctor.timer` | `S1` systemd enablement/state for `chief-doctor.timer` | persistent host systemd state; unit definition itself was not changed; not Boris runtime | no repo-visible Boris writer/enforcer confirmed; future manual `systemctl`, unit/package management, or external host bootstrap outside repo may re-enable | `Boris restart=yes`; `startup fixer=yes`; `doctor/monitor/self-heal=likely yes`; `full host reboot=likely yes because disabled state is persistent`; `host reprovision=unknown` | no sync into `jobs.json`, `crontab`, service files, startup fixers, doctor/monitor, or `service-guard` baseline is repo-confirmed; if drift appears, sync only at host systemd/bootstrap layer |

## Already persistent

### `S1 ssh alias s2`

- Current target is a host-level master file, not runtime/derived.
- `CONFIG_WRITERS_AND_ENFORCERS` does not identify any startup fixer, doctor, monitor, self-heal or sync contour that rewrites `/root/.ssh/config`.
- Therefore repo-visible evidence says this change already survives:
  - Boris restart
  - startup fixer
  - doctor / monitor / self-heal

## Likely persistent

### `boris-email-router.timer` disabled

- The change was applied through persistent systemd enablement state, not through temporary Boris runtime state.
- Repo-visible docs do not confirm any Boris writer/enforcer that re-enables this timer.
- It should survive:
  - Boris restart
  - startup fixer
  - normal doctor / monitor / self-heal cycles
- It is still only `likely persistent`, not `proven immortal`, because repo docs do not prove absence of every possible host bootstrap or package-management layer outside the audited set.

### `chief-doctor.timer` disabled

- Same persistence profile as `boris-email-router.timer`.
- Repo-visible evidence points to persistent host systemd state, with no confirmed Boris-side re-enable contour.

## At risk of rollback

### Current verdict

- No confirmed already-applied server-side change currently sits behind an active repo-visible Boris writer/enforcer chain.
- In particular, none of the three applied changes are confirmed as being rewritten by:
  - `startup-cleanup.sh`
  - `fix-model-strategy.py`
  - `circuit-breaker-internal.py`
  - `boris-doctor`
  - `workspace-validator.py`
  - `infra-monitor`
  - `service-guard.py`
  - `watchdog-meta.sh`

### What would move a change into this bucket

- a new audit proving that:
  - `service-guard` tracks the exact timer units and restores their enabled state;
  - host bootstrap recreates `/root/.ssh/config` without the alias;
  - some package/deploy contour re-enables timers on boot;
  - some previously unaudited doctor/monitor logic mutates the same host targets.

## Definitely overwritten unless synced

- None confirmed for the already applied changes.
- This bucket currently applies to other contours in the project, but not to these three completed host-level changes.
- Examples of contours that do live in this bucket generally:
  - runtime `openclaw.json`
  - `jobs.json`
  - tracked configs behind `service-guard`
  - prompt/memory files behind `workspace-validator`
- Those are not already-applied changes from these sessions and are therefore excluded from this plan matrix.

## Sync priorities

### Priority 0

- No immediate persistence sync apply is repo-visible required for the three already applied changes.

### Priority 1

- Keep them on the next safe live audit checklist:
  - `ssh -G s2`
  - `ssh -o BatchMode=yes s2 "hostname -f"`
  - `systemctl is-enabled boris-email-router.timer chief-doctor.timer`
  - `systemctl is-active boris-email-router.timer chief-doctor.timer`

### Priority 2

- If future drift appears, audit the exact writer layer first.
- Safe diagnostic order:
  1. confirm current live state;
  2. check whether drift came from manual systemd/SSH changes;
  3. only then audit bootstrap/config-management outside repo;
  4. do not blame Boris startup fixer or self-heal without evidence.

### Priority 3

- If owner wants persistence across full host rebuild/reprovision, sync must happen outside current Boris runtime layers:
  - SSH alias -> host SSH bootstrap/config-management
  - disabled timers -> host systemd/bootstrap policy

## What requires owner decision

- Whether alias `s2` should remain just a local operator convenience or become mandatory host bootstrap standard on `S1`.
- Whether `boris-email-router.timer` and `chief-doctor.timer` should remain permanently disabled legacy contours, or later be fully removed from host baseline/config management.
- Whether any host bootstrap/config-management source of truth exists outside repo and should be updated to match these already-applied changes.

## What requires approve

- Any new server-side edits to:
  - `/root/.ssh/config`
  - `boris-email-router.timer`
  - `chief-doctor.timer`
  - related unit files
  - `daemon-reload`
  - any host bootstrap/config-management system outside repo
- Any attempt to sync these changes into:
  - startup scripts
  - fixers
  - doctor / monitor / self-heal layers
  - `service-guard` baselines
  without first proving that those layers actually own these targets.
- Any re-enable/start/restart of the disabled timers or changes to related services.

## Verdict

- Repo-visible confirmed server-side changes already applied in these sessions = `3`.
- `already persistent`:
  - `S1 ssh alias s2`
- `likely persistent`:
  - `boris-email-router.timer` disabled
  - `chief-doctor.timer` disabled
- `at risk of rollback`:
  - none confirmed right now
- `definitely overwritten unless synced`:
  - none confirmed right now
- Therefore current safe plan is:
  - do not change anything;
  - do not sync into Boris fixers/startup/doctor/monitor by default;
  - re-audit only if future drift appears or if owner wants persistence beyond current host state.
