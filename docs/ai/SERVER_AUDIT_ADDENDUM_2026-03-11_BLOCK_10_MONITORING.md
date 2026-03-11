# SERVER AUDIT ADDENDUM 2026-03-11 BLOCK 10 MONITORING

Docs-only фиксация результата narrow read-only audit по:
- Block 10. `Monitoring, self-healing, doctor, heartbeat`

Изменения в live не выполнялись.
Это не apply changelog и не live fix.

## Block 10. Monitoring / doctor / self-heal contour

Статус:
- `OK with WARN`
- active outage not confirmed
- working control plane with legacy monitoring drift
- not pure docs-only drift

### Что проверено

- Repo canon и dated audit docs:
  - `docs/ai/BORIS_DETAIL_SCHEMA_CHECKLIST_v2.md`
  - `docs/ai/BASELINE_2026-03-10.md`
  - `docs/ai/OPERATING_CONSENSUS.md`
  - `docs/ai/SOURCE_OF_TRUTH.md`
  - `docs/ai/CONFIG_WRITERS_AND_ENFORCERS.md`
  - `docs/ai/DOCTOR_AND_SELFHEAL_AUDIT_2026-03-11.md`
  - `docs/ai/KNOWN_BUGS_AND_WORKAROUNDS.md`
- Read-only live checks on `S1`:
  - `systemctl is-active/show` for:
    - `infra-monitor.service`
    - `boris-doctor.service`
    - `guard-webhook.service`
    - `n8n-watchdog.service`
    - `monitor-safe.service`
    - legacy `chief-doctor.service`, `chief-doctor.timer`, `boris-email-router.timer`
  - `systemctl --failed`
  - freshness of:
    - `/var/lib/apps-data/infra-monitor/state/heartbeat.json`
    - `/var/lib/apps-data/infra-monitor/state/heartbeat-safe.json`
    - `/var/lib/apps-data/boris-doctor/heartbeat`
    - `/var/lib/apps-data/boris-doctor/last-health-check.ts`
  - relevant crontab lines
  - `python3 /opt/apps/infra-monitor/service-guard.py status`
- Read-only live checks on `S2`:
  - `systemctl is-active/show` for:
    - `infra-monitor.service`
    - `n8n-doctor.service`
    - `guard-webhook.service`
    - `monitor-safe.service`
  - `systemctl --failed`
  - freshness of:
    - `/var/lib/apps-data/infra-monitor/state/heartbeat.json`
    - `/var/lib/apps-data/infra-monitor/state/heartbeat-safe.json`
    - business heartbeats:
      - `sla-check.hb`
      - `nudge-send.hb`
      - `followup-scan.hb`
      - `followup-send.hb`
      - `dispatch-reminders.hb`
  - relevant crontab lines
  - `python3 /opt/apps/infra-monitor/service-guard.py status`

### Что ок

- Core monitoring contour is alive on both servers.
- On `S1` active:
  - `infra-monitor`
  - `boris-doctor`
  - `guard-webhook`
  - `n8n-watchdog`
- On `S2` active:
  - `infra-monitor`
  - `n8n-doctor`
  - `guard-webhook`
- Core heartbeats are fresh and stop condition by inactive monitoring is not confirmed.
- `monitor-safe.service` on both `S1` and `S2` is `disabled/inactive`.
- Stale `heartbeat-safe.json` is explained by disabled `monitor-safe` and is not a standalone incident.
- Business heartbeat files on `S2` are readable and consistent with current cron cadence.

### Что drift

- This is not a pure docs-only drift, because current monitoring-space still contains live legacy noise on `S1`.
- This is also not a confirmed active outage:
  - core monitoring units are active
  - restart loops are not confirmed
  - heartbeat freshness is present
- Current drift class = live monitoring-space drift / legacy noise on `S1`.
- Stale monitored contours on `S1` still visible in health/baseline space:
  - `pg-tunnel-s2`
  - `okdesk-pipeline`

### Что risky

- Main risk = monitoring / self-heal stack remains a writer-enforcer layer.
- It must not be treated as product truth or safe default for business contours.
- Active dangerous contours still overlap with runtime/config/workflow surfaces:
  - `infra-monitor`
  - `service-guard`
  - `n8n-watchdog`
  - `n8n-doctor`
  - `watchdog-meta`
- `S1` legacy monitored contours can still mislead future repair planning if health space is taken as canonical runtime truth.
- Live repair is not required for the current contour.

### Что требует owner decision

- Future cleanup of stale monitored contours on `S1`:
  - `pg-tunnel-s2`
  - `okdesk-pipeline`
- Any decision to demote a contour to legacy, or to promote it back to required runtime, inside monitoring/self-heal space.
- Any future cleanup remains separate from this audit and requires owner decision first.

### Что требует approve

- Any live changes to:
  - self-healing logic
  - doctor scripts
  - `sudoers`
  - auto-enroll / baseline / registry lists
  - monitoring configs
  - systemd/crontab/service-guard state for this contour
- Any cleanup of stale monitored contours requires explicit approve after owner decision.

### Вердикт

- `OK with WARN`
- core monitoring/doctor contour is alive on both servers
- active outage is not confirmed
- current issue class = working control plane with legacy monitoring drift on `S1`
- this is not pure docs drift and not a confirmed outage
- live repair is not required now
- future cleanup is possible only as separate owner-decision + approve flow
