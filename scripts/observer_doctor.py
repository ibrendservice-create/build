#!/usr/bin/env python3
"""Observer-only doctor report for Boris/OpenClaw.

This collector is intentionally:
- manual only
- read-only
- report only
- no auto-repair
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit


MODE_INFRA = "infra"
MODE_BUSINESS = "business"
MODE_FULL = "full"
STATUS_OK = "OK"
STATUS_WARN = "WARN"
STATUS_FAIL = "FAIL"
STATUS_UNKNOWN = "UNKNOWN"

DEFAULT_S2_TARGET = "root@72.56.98.52"
DEFAULT_TIMEOUT_SEC = 5.0
DEFAULT_SSH_CONNECT_TIMEOUT_SEC = 5
BRIDGE_HA_URL = "https://n8n.brendservice24.ru/bridge-ha/health"
BRIDGE_HA_CANONICAL_SCHEME = "https"
BRIDGE_HA_CANONICAL_HOST = "n8n.brendservice24.ru"
BRIDGE_HA_CANONICAL_PATH = "/bridge-ha/health"
BUSINESS_HEARTBEAT_THRESHOLD_SEC = 3600
BUSINESS_HEARTBEAT_THRESHOLD_NOTE = (
    "Conservative 1h freshness threshold derived from the audited S2 "
    "check-cron-health.sh cadence */15; exact per-job cadence is not "
    "repo-confirmed, so stale or missing business heartbeats remain WARN, not FAIL."
)

SOURCE_REF = (
    "docs/ai/DOCTOR_AGENT_DECISION.md + "
    "docs/ai/DOCTOR_AND_SELFHEAL_AUDIT_2026-03-11.md + "
    "docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-11_BRIDGE_HA.md + "
    "docs/ai/BORIS_DETAIL_SCHEMA_CHECKLIST_v2.md + "
    "docs/ai/SERVER_AUDIT_ADDENDUM_2026-03-10_WORKFLOWS.md"
)

NOT_COVERED = [
    "semantic business correctness",
    "classification quality",
    "matching quality",
    "QC quality",
    "rating / XP correctness",
    "promise correctness",
]

S1_SERVICES = [
    "boris-doctor",
    "infra-monitor",
    "claude-bridge",
    "nginx",
]

S2_SERVICES = [
    "caddy",
    "n8n-doctor",
    "okdesk-pipeline",
]

S1_HEARTBEAT_PATHS = {
    "s1.heartbeat.boris_doctor": "/var/lib/apps-data/boris-doctor/heartbeat",
    "s1.heartbeat.infra_monitor": "/var/lib/apps-data/infra-monitor/state/heartbeat.json",
    "s1.heartbeat.infra_monitor_safe": "/var/lib/apps-data/infra-monitor/state/heartbeat-safe.json",
}

S2_BUSINESS_HEARTBEATS = {
    "s2.hb.sla_check": "/var/lib/apps-data/infra-monitor/heartbeats/sla-check.hb",
    "s2.hb.nudge_send": "/var/lib/apps-data/infra-monitor/heartbeats/nudge-send.hb",
    "s2.hb.followup_scan": "/var/lib/apps-data/infra-monitor/heartbeats/followup-scan.hb",
    "s2.hb.followup_send": "/var/lib/apps-data/infra-monitor/heartbeats/followup-send.hb",
    "s2.hb.dispatch_reminders": "/var/lib/apps-data/infra-monitor/heartbeats/dispatch-reminders.hb",
}

S2_CONTAINERS = [
    "app-n8n-1",
    "app-db-1",
    "app-cache-1",
    "app-docling-1",
]

WORKFLOW_EXPECTATIONS = {
    "eHRHeiYttQgUgkHK": ("WF3", "active"),
    "0iwcXPWA3XKGknLz": ("WF8 relay", "active"),
    "VxaGd6LaPHOg3KHi": ("WF10", "active"),
    "kCZriGsWrWFVd3pG": ("Telegram Logger", "active"),
    "wvVidk9SZJ1n0DAN": ("WF Watchdog", "active"),
    "qWKnu4iqTspEsCxi": ("WF11", "inactive"),
    "0Qj2ZeBsz5UtlZps": ("WF8 Watchdog", "inactive"),
    "VufRh7hHufiddQZQ": ("Email Attachment Parser", "inactive"),
}

ALLOWED_REMOTE_PREFIXES = (
    ("systemctl", "is-active"),
    ("systemctl", "show"),
    ("ss", "-ltn"),
    ("docker", "inspect", "-f"),
    ("stat", "-c", "%Y"),
    ("docker", "exec", "app-db-1", "psql", "-U", "postgres", "-d", "n8n", "-Atc"),
)


@dataclass
class CommandResult:
    returncode: int | None
    stdout: str
    stderr: str
    error: str | None = None


@dataclass
class CheckResult:
    id: str
    layer: str
    target: str
    status: str
    expected: str
    observed: str
    probe: str
    evidence: str
    source: str
    human_follow_up: str
    touch_boundary: str = "observer-only"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manual read-only observer-doctor report")
    parser.add_argument("--mode", choices=[MODE_INFRA, MODE_BUSINESS, MODE_FULL], default=MODE_FULL)
    parser.add_argument("--format", choices=["json", "pretty"], default="json")
    parser.add_argument("--timeout-sec", type=float, default=DEFAULT_TIMEOUT_SEC)
    parser.add_argument("--ssh-target", default=DEFAULT_S2_TARGET)
    parser.add_argument("--ssh-connect-timeout-sec", type=int, default=DEFAULT_SSH_CONNECT_TIMEOUT_SEC)
    return parser.parse_args()


def run_command(argv: list[str], timeout_sec: float) -> CommandResult:
    try:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        return CommandResult(
            returncode=completed.returncode,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
        )
    except subprocess.TimeoutExpired as exc:
        return CommandResult(
            returncode=None,
            stdout=(exc.stdout or "").strip(),
            stderr=(exc.stderr or "").strip(),
            error=f"timeout after {timeout_sec}s",
        )
    except FileNotFoundError as exc:
        return CommandResult(returncode=None, stdout="", stderr="", error=str(exc))


def is_env_mismatch(command: CommandResult) -> bool:
    stderr = command.stderr.lower()
    error = (command.error or "").lower()
    markers = [
        "system has not been booted with systemd",
        "no such file or directory",
        "command not found",
        "failed to connect to bus",
        "operation not permitted",
    ]
    return any(marker in stderr or marker in error for marker in markers)


def is_remote_transport_issue(command: CommandResult) -> bool:
    text = " ".join(part for part in [command.stdout, command.stderr, command.error or ""] if part).lower()
    markers = [
        "operation not permitted",
        "could not resolve hostname",
        "name or service not known",
        "network is unreachable",
        "connection refused",
        "connection timed out",
        "no route to host",
        "permission denied",
        "connection closed",
        "connection reset",
    ]
    return command.returncode == 255 or any(marker in text for marker in markers)


def safe_json_dumps(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def command_evidence(command: CommandResult) -> str:
    payload = {
        "returncode": command.returncode,
        "stdout": command.stdout,
        "stderr": command.stderr,
        "error": command.error,
    }
    return safe_json_dumps(payload)


def is_json_content_type(content_type: str) -> bool:
    media_type = content_type.split(";", 1)[0].strip().lower()
    return media_type == "application/json" or media_type.endswith("+json")


def canonical_bridge_ha_issue(url: str) -> str | None:
    parsed = urlsplit(url)
    if parsed.scheme.lower() != BRIDGE_HA_CANONICAL_SCHEME:
        return f"non-canonical scheme={parsed.scheme or 'missing'}"
    if parsed.netloc.lower() != BRIDGE_HA_CANONICAL_HOST:
        return f"non-canonical host={parsed.netloc or 'missing'}"
    if parsed.path != BRIDGE_HA_CANONICAL_PATH:
        return f"non-canonical path={parsed.path or 'missing'}"
    if parsed.query:
        return f"non-canonical query={parsed.query}"
    return None


def bridge_ha_expected() -> str:
    return f"canonical {BRIDGE_HA_URL} returning application/json JSON body"


def business_heartbeat_expected() -> str:
    minutes = BUSINESS_HEARTBEAT_THRESHOLD_SEC // 60
    return (
        "existing heartbeat file fresh within conservative "
        f"<= {BUSINESS_HEARTBEAT_THRESHOLD_SEC}s ({minutes}m) threshold"
    )


def business_heartbeat_status(age_seconds: int) -> str:
    if age_seconds <= BUSINESS_HEARTBEAT_THRESHOLD_SEC:
        return STATUS_OK
    return STATUS_WARN


def run_remote_command(
    ssh_target: str,
    remote_argv: list[str],
    timeout_sec: float,
    ssh_connect_timeout_sec: int,
) -> CommandResult:
    if not any(tuple(remote_argv[: len(prefix)]) == prefix for prefix in ALLOWED_REMOTE_PREFIXES):
        return CommandResult(
            returncode=None,
            stdout="",
            stderr="",
            error=f"remote command not in allowlist: {remote_argv!r}",
        )

    ssh_argv = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={ssh_connect_timeout_sec}",
        ssh_target,
        shlex.join(remote_argv),
    ]
    return run_command(ssh_argv, timeout_sec)


def service_probe(
    check_id: str,
    layer: str,
    target: str,
    service: str,
    timeout_sec: float,
    ssh_target: str | None = None,
    ssh_connect_timeout_sec: int | None = None,
) -> CheckResult:
    base_cmd = ["systemctl", "is-active", service]
    if ssh_target:
        command = run_remote_command(
            ssh_target,
            base_cmd,
            timeout_sec,
            ssh_connect_timeout_sec or DEFAULT_SSH_CONNECT_TIMEOUT_SEC,
        )
        probe = f"ssh {ssh_target} -- {shlex.join(base_cmd)}"
    else:
        command = run_command(base_cmd, timeout_sec)
        probe = shlex.join(base_cmd)

    observed = command.stdout or command.error or "no output"
    status = STATUS_UNKNOWN
    follow_up = f"Inspect systemd unit {service} manually."

    if command.error and not is_env_mismatch(command):
        status = STATUS_FAIL
    elif command.error and is_env_mismatch(command):
        status = STATUS_UNKNOWN
    elif observed == "active":
        status = STATUS_OK
    elif observed in {"activating", "reloading"}:
        status = STATUS_WARN
    elif observed in {"inactive", "failed", "unknown", "deactivating"}:
        status = STATUS_FAIL
    else:
        status = STATUS_UNKNOWN

    return CheckResult(
        id=check_id,
        layer=layer,
        target=target,
        status=status,
        expected="active",
        observed=observed,
        probe=probe,
        evidence=command_evidence(command),
        source=SOURCE_REF,
        human_follow_up=follow_up,
    )


def local_path_probe(check_id: str, layer: str, path: str) -> CheckResult:
    candidate = Path(path)
    probe = f"python pathlib stat {path}"
    if not candidate.exists():
        return CheckResult(
            id=check_id,
            layer=layer,
            target="S1",
            status=STATUS_FAIL,
            expected="existing heartbeat/state file",
            observed="missing",
            probe=probe,
            evidence=safe_json_dumps({"path": path, "exists": False}),
            source=SOURCE_REF,
            human_follow_up=f"Confirm why {path} is absent on S1.",
        )

    age_seconds = max(0, int(time.time() - candidate.stat().st_mtime))
    return CheckResult(
        id=check_id,
        layer=layer,
        target="S1",
        status=STATUS_UNKNOWN,
        expected="existing heartbeat/state file with reviewed freshness",
        observed=f"present age_seconds={age_seconds}",
        probe=probe,
        evidence=safe_json_dumps({"path": path, "age_seconds": age_seconds}),
        source=SOURCE_REF,
        human_follow_up=f"Review heartbeat age for {path}; MVP does not encode freshness thresholds.",
    )


def remote_path_probe(
    check_id: str,
    layer: str,
    path: str,
    ssh_target: str,
    timeout_sec: float,
    ssh_connect_timeout_sec: int,
) -> CheckResult:
    remote_cmd = ["stat", "-c", "%Y", path]
    command = run_remote_command(ssh_target, remote_cmd, timeout_sec, ssh_connect_timeout_sec)
    probe = f"ssh {ssh_target} -- {shlex.join(remote_cmd)}"
    expected = business_heartbeat_expected()

    if command.error:
        return CheckResult(
            id=check_id,
            layer=layer,
            target="S2",
            status=STATUS_UNKNOWN,
            expected=expected,
            observed=command.error,
            probe=probe,
            evidence=command_evidence(command),
            source=SOURCE_REF,
            human_follow_up=f"Verify SSH access to S2 and inspect {path} manually before grading heartbeat freshness.",
        )

    if is_remote_transport_issue(command):
        return CheckResult(
            id=check_id,
            layer=layer,
            target="S2",
            status=STATUS_UNKNOWN,
            expected=expected,
            observed=command.stderr or "remote transport issue",
            probe=probe,
            evidence=command_evidence(command),
            source=SOURCE_REF,
            human_follow_up=f"Verify SSH access to S2 before interpreting {path} as missing.",
        )

    if command.returncode != 0:
        return CheckResult(
            id=check_id,
            layer=layer,
            target="S2",
            status=STATUS_WARN,
            expected=expected,
            observed="missing or unreadable",
            probe=probe,
            evidence=safe_json_dumps(
                {
                    "path": path,
                    "threshold_seconds": BUSINESS_HEARTBEAT_THRESHOLD_SEC,
                    "threshold_note": BUSINESS_HEARTBEAT_THRESHOLD_NOTE,
                    "command": json.loads(command_evidence(command)),
                }
            ),
            source=SOURCE_REF,
            human_follow_up=(
                f"Confirm why {path} is missing or unreadable on S2; treat this as a business-liveness warning, "
                "not automatic product failure."
            ),
        )

    try:
        mtime = int(command.stdout)
    except ValueError:
        return CheckResult(
            id=check_id,
            layer=layer,
            target="S2",
            status=STATUS_UNKNOWN,
            expected="epoch mtime",
            observed=command.stdout or "invalid stat output",
            probe=probe,
            evidence=command_evidence(command),
            source=SOURCE_REF,
            human_follow_up=f"Inspect raw stat output for {path} on S2.",
        )

    age_seconds = max(0, int(time.time() - mtime))
    status = business_heartbeat_status(age_seconds)
    observed = f"present age_seconds={age_seconds} threshold_seconds={BUSINESS_HEARTBEAT_THRESHOLD_SEC}"
    if status == STATUS_OK:
        human_follow_up = (
            "If dispatch behavior still looks wrong, inspect executions directly; heartbeat freshness is only a liveness signal."
        )
    else:
        human_follow_up = (
            f"Age {age_seconds}s exceeds the conservative {BUSINESS_HEARTBEAT_THRESHOLD_SEC}s freshness threshold; "
            "treat this as a liveness warning until cadence is live-confirmed."
        )
    return CheckResult(
        id=check_id,
        layer=layer,
        target="S2",
        status=status,
        expected=expected,
        observed=observed,
        probe=probe,
        evidence=safe_json_dumps(
            {
                "path": path,
                "age_seconds": age_seconds,
                "threshold_seconds": BUSINESS_HEARTBEAT_THRESHOLD_SEC,
                "threshold_note": BUSINESS_HEARTBEAT_THRESHOLD_NOTE,
                "command": json.loads(command_evidence(command)),
            }
        ),
        source=SOURCE_REF,
        human_follow_up=human_follow_up,
    )


def http_json_probe(url: str, timeout_sec: float) -> CheckResult:
    probe = f"GET {url}"
    expected = bridge_ha_expected()
    canonical_issue = canonical_bridge_ha_issue(url)
    if canonical_issue:
        return CheckResult(
            id="public.bridge_ha.json",
            layer="infra",
            target="public",
            status=STATUS_WARN,
            expected=expected,
            observed=canonical_issue,
            probe=probe,
            evidence=safe_json_dumps({"requested_url": url, "canonical_issue": canonical_issue}),
            source=SOURCE_REF,
            human_follow_up="Use the exact canonical n8n bridge-ha URL; do not probe ops domain or alternate paths.",
        )

    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Accept": "application/json",
            "User-Agent": "observer-doctor/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_sec) as response:
            body = response.read().decode("utf-8", errors="replace")
            content_type = response.headers.get("Content-Type", "")
            final_url = response.geturl()
            observed = (
                f"http={response.status} final_url={final_url} "
                f"content_type={content_type or 'missing'}"
            )
            final_issue = canonical_bridge_ha_issue(final_url)
            if final_issue:
                return CheckResult(
                    id="public.bridge_ha.json",
                    layer="infra",
                    target="public",
                    status=STATUS_WARN,
                    expected=expected,
                    observed=observed,
                    probe=probe,
                    evidence=safe_json_dumps(
                        {
                            "requested_url": url,
                            "final_url": final_url,
                            "canonical_issue": final_issue,
                            "content_type": content_type,
                            "body_preview": body[:200],
                        }
                    ),
                    source=SOURCE_REF,
                    human_follow_up="Inspect public ingress route; canonical bridge-ha probe must stay on the n8n URL without redirects.",
                )
            try:
                payload = json.loads(body)
            except json.JSONDecodeError as exc:
                return CheckResult(
                    id="public.bridge_ha.json",
                    layer="infra",
                    target="public",
                    status=STATUS_WARN,
                    expected=expected,
                    observed=observed,
                    probe=probe,
                    evidence=safe_json_dumps(
                        {
                            "requested_url": url,
                            "final_url": final_url,
                            "content_type": content_type,
                            "json_error": str(exc),
                            "body_preview": body[:200],
                        }
                    ),
                    source=SOURCE_REF,
                    human_follow_up="Canonical public probe did not return JSON; inspect bridge-ha ingress and body manually.",
                )
            if not is_json_content_type(content_type):
                return CheckResult(
                    id="public.bridge_ha.json",
                    layer="infra",
                    target="public",
                    status=STATUS_WARN,
                    expected=expected,
                    observed=observed,
                    probe=probe,
                    evidence=safe_json_dumps(
                        {
                            "requested_url": url,
                            "final_url": final_url,
                            "content_type": content_type,
                            "body": payload,
                        }
                    ),
                    source=SOURCE_REF,
                    human_follow_up="Canonical public probe returned JSON body without a JSON content type; inspect ingress/header handling manually.",
                )
            return CheckResult(
                id="public.bridge_ha.json",
                layer="infra",
                target="public",
                status=STATUS_OK,
                expected=expected,
                observed=observed,
                probe=probe,
                evidence=safe_json_dumps(
                    {
                        "requested_url": url,
                        "final_url": final_url,
                        "body": payload,
                        "content_type": content_type,
                    }
                ),
                source=SOURCE_REF,
                human_follow_up="If semantics look wrong, inspect bridge-ha upstream manually.",
            )
    except urllib.error.HTTPError as exc:
        content_type = exc.headers.get("Content-Type", "") if exc.headers else ""
        final_url = exc.geturl() or url
        body = exc.read().decode("utf-8", errors="replace")
        observed = (
            f"http={exc.code} final_url={final_url} "
            f"content_type={content_type or 'missing'}"
        )
        status = STATUS_FAIL if 500 <= exc.code <= 599 else STATUS_WARN
        follow_up = (
            "Inspect canonical public bridge-ha route manually."
            if status == STATUS_FAIL
            else "Inspect canonical public bridge-ha route and confirm the host/path/protocol are still canonical."
        )
        evidence = safe_json_dumps(
            {
                "requested_url": url,
                "final_url": final_url,
                "content_type": content_type,
                "error": str(exc),
                "body_preview": body[:200],
            }
        )
        return CheckResult(
            id="public.bridge_ha.json",
            layer="infra",
            target="public",
            status=status,
            expected=expected,
            observed=observed,
            probe=probe,
            evidence=evidence,
            source=SOURCE_REF,
            human_follow_up=follow_up,
        )
    except (urllib.error.URLError, TimeoutError) as exc:
        return CheckResult(
            id="public.bridge_ha.json",
            layer="infra",
            target="public",
            status=STATUS_FAIL,
            expected=expected,
            observed=str(exc),
            probe=probe,
            evidence=safe_json_dumps({"error": str(exc)}),
            source=SOURCE_REF,
            human_follow_up="Inspect canonical public bridge-ha route and JSON body manually.",
        )


def listener_probe(
    check_id: str,
    layer: str,
    target: str,
    port: int,
    timeout_sec: float,
    ssh_target: str,
    ssh_connect_timeout_sec: int,
) -> CheckResult:
    remote_cmd = ["ss", "-ltn"]
    command = run_remote_command(ssh_target, remote_cmd, timeout_sec, ssh_connect_timeout_sec)
    probe = f"ssh {ssh_target} -- {shlex.join(remote_cmd)}"
    needle = f":{port}"

    if command.error:
        return CheckResult(
            id=check_id,
            layer=layer,
            target=target,
            status=STATUS_UNKNOWN,
            expected=f"listener {needle}",
            observed=command.error,
            probe=probe,
            evidence=command_evidence(command),
            source=SOURCE_REF,
            human_follow_up=f"Verify SSH access and inspect listener {needle} manually.",
        )

    if is_remote_transport_issue(command):
        return CheckResult(
            id=check_id,
            layer=layer,
            target=target,
            status=STATUS_UNKNOWN,
            expected=f"listener {needle}",
            observed=command.stderr or "remote transport issue",
            probe=probe,
            evidence=command_evidence(command),
            source=SOURCE_REF,
            human_follow_up=f"Verify SSH access before interpreting listener {needle} as absent.",
        )

    observed = "present" if needle in command.stdout else "absent"
    status = STATUS_OK if observed == "present" else STATUS_FAIL
    return CheckResult(
        id=check_id,
        layer=layer,
        target=target,
        status=status,
        expected=f"listener {needle}",
        observed=observed,
        probe=probe,
        evidence=command_evidence(command),
        source=SOURCE_REF,
        human_follow_up=f"Inspect port {port} binding on {target} manually.",
    )


def container_probe(
    check_id: str,
    container: str,
    ssh_target: str,
    timeout_sec: float,
    ssh_connect_timeout_sec: int,
) -> CheckResult:
    remote_cmd = [
        "docker",
        "inspect",
        "-f",
        "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}",
        container,
    ]
    command = run_remote_command(ssh_target, remote_cmd, timeout_sec, ssh_connect_timeout_sec)
    probe = f"ssh {ssh_target} -- docker inspect -f status {container}"

    if command.error:
        status = STATUS_UNKNOWN
        observed = command.error
    elif is_remote_transport_issue(command):
        status = STATUS_UNKNOWN
        observed = command.stderr or "remote transport issue"
    elif command.returncode != 0:
        status = STATUS_FAIL
        observed = command.stderr or "inspect failed"
    else:
        observed = command.stdout or "empty"
        if observed in {"healthy", "running"}:
            status = STATUS_OK
        elif observed in {"restarting", "starting"}:
            status = STATUS_WARN
        else:
            status = STATUS_FAIL

    return CheckResult(
        id=check_id,
        layer="infra",
        target="S2",
        status=status,
        expected="healthy or running",
        observed=observed,
        probe=probe,
        evidence=command_evidence(command),
        source=SOURCE_REF,
        human_follow_up=f"Inspect container {container} manually on S2.",
    )


def workflow_probe(
    ssh_target: str,
    timeout_sec: float,
    ssh_connect_timeout_sec: int,
) -> CheckResult:
    workflow_ids = sorted(WORKFLOW_EXPECTATIONS)
    joined = ", ".join(f"'{workflow_id}'" for workflow_id in workflow_ids)
    sql = (
        "SELECT id || '|' || CASE WHEN active THEN 'active' ELSE 'inactive' END "
        "FROM workflow_entity "
        f"WHERE id IN ({joined}) "
        "ORDER BY id;"
    )
    remote_cmd = [
        "docker",
        "exec",
        "app-db-1",
        "psql",
        "-U",
        "postgres",
        "-d",
        "n8n",
        "-Atc",
        sql,
    ]
    command = run_remote_command(ssh_target, remote_cmd, timeout_sec, ssh_connect_timeout_sec)
    probe = "ssh S2 -- docker exec app-db-1 psql -U postgres -d n8n -Atc '<workflow query>'"

    if command.error:
        return CheckResult(
            id="s2.workflows.canonical",
            layer="business",
            target="S2",
            status=STATUS_UNKNOWN,
            expected="canonical workflow state by exact IDs",
            observed=command.error,
            probe=probe,
            evidence=command_evidence(command),
            source=SOURCE_REF,
            human_follow_up="Verify SSH/DB access and rerun the read-only workflow query manually.",
        )

    if is_remote_transport_issue(command):
        return CheckResult(
            id="s2.workflows.canonical",
            layer="business",
            target="S2",
            status=STATUS_UNKNOWN,
            expected="canonical workflow state by exact IDs",
            observed=command.stderr or "remote transport issue",
            probe=probe,
            evidence=command_evidence(command),
            source=SOURCE_REF,
            human_follow_up="Verify SSH access to S2 before interpreting workflow state.",
        )

    if command.returncode != 0:
        return CheckResult(
            id="s2.workflows.canonical",
            layer="business",
            target="S2",
            status=STATUS_FAIL,
            expected="canonical workflow state by exact IDs",
            observed="workflow query failed",
            probe=probe,
            evidence=command_evidence(command),
            source=SOURCE_REF,
            human_follow_up="Inspect n8n DB availability and workflow_entity query manually.",
        )

    observed_rows = {}
    for line in filter(None, command.stdout.splitlines()):
        workflow_id, state = line.split("|", 1)
        observed_rows[workflow_id] = state

    mismatches = []
    missing = []
    rendered = {}
    for workflow_id, (label, expected_state) in WORKFLOW_EXPECTATIONS.items():
        observed_state = observed_rows.get(workflow_id)
        rendered[label] = {
            "id": workflow_id,
            "expected": expected_state,
            "observed": observed_state,
        }
        if observed_state is None:
            missing.append(workflow_id)
        elif observed_state != expected_state:
            mismatches.append({"id": workflow_id, "label": label, "expected": expected_state, "observed": observed_state})

    if missing or mismatches:
        status = STATUS_FAIL
        observed = "drift detected"
        follow_up = "Inspect workflow state by exact IDs; do not change flags without approve."
    else:
        status = STATUS_OK
        observed = "all canonical workflow states match"
        follow_up = "If business behavior still looks wrong, inspect executions manually; MVP does not judge semantic correctness."

    evidence = safe_json_dumps({"rendered": rendered, "missing": missing, "mismatches": mismatches})
    return CheckResult(
        id="s2.workflows.canonical",
        layer="business",
        target="S2",
        status=status,
        expected="canonical workflow state by exact IDs",
        observed=observed,
        probe=probe,
        evidence=evidence,
        source=SOURCE_REF,
        human_follow_up=follow_up,
    )


def rollup_probe(check_id: str, layer: str, target: str, expected: str, observed: str, inputs: Iterable[CheckResult]) -> CheckResult:
    statuses = [item.status for item in inputs]
    if any(status == STATUS_FAIL for status in statuses):
        status = STATUS_FAIL
    elif any(status == STATUS_WARN for status in statuses):
        status = STATUS_WARN
    elif any(status == STATUS_UNKNOWN for status in statuses):
        status = STATUS_WARN
    elif statuses and all(status == STATUS_OK for status in statuses):
        status = STATUS_OK
    else:
        status = STATUS_UNKNOWN

    evidence = safe_json_dumps(
        {
            "inputs": [
                {"id": item.id, "status": item.status, "observed": item.observed}
                for item in inputs
            ]
        }
    )
    return CheckResult(
        id=check_id,
        layer=layer,
        target=target,
        status=status,
        expected=expected,
        observed=observed,
        probe="derived rollup",
        evidence=evidence,
        source=SOURCE_REF,
        human_follow_up="Inspect the failing or unknown child probes manually.",
    )


def build_infra_checks(args: argparse.Namespace) -> list[CheckResult]:
    checks: list[CheckResult] = []
    for service in S1_SERVICES:
        checks.append(
            service_probe(
                check_id=f"s1.service.{service}",
                layer="infra",
                target="S1",
                service=service,
                timeout_sec=args.timeout_sec,
            )
        )
    for check_id, path in S1_HEARTBEAT_PATHS.items():
        checks.append(local_path_probe(check_id=check_id, layer="infra", path=path))
    checks.append(http_json_probe(BRIDGE_HA_URL, args.timeout_sec))
    for service in S2_SERVICES:
        checks.append(
            service_probe(
                check_id=f"s2.service.{service}",
                layer="infra",
                target="S2",
                service=service,
                timeout_sec=args.timeout_sec,
                ssh_target=args.ssh_target,
                ssh_connect_timeout_sec=args.ssh_connect_timeout_sec,
            )
        )
    checks.append(
        listener_probe(
            check_id="s2.listener.okdesk_pipeline_3200",
            layer="infra",
            target="S2",
            port=3200,
            timeout_sec=args.timeout_sec,
            ssh_target=args.ssh_target,
            ssh_connect_timeout_sec=args.ssh_connect_timeout_sec,
        )
    )
    for container in S2_CONTAINERS:
        checks.append(
            container_probe(
                check_id=f"s2.container.{container}",
                container=container,
                ssh_target=args.ssh_target,
                timeout_sec=args.timeout_sec,
                ssh_connect_timeout_sec=args.ssh_connect_timeout_sec,
            )
        )
    return checks


def build_business_checks(args: argparse.Namespace) -> list[CheckResult]:
    checks: list[CheckResult] = []
    for check_id, path in S2_BUSINESS_HEARTBEATS.items():
        checks.append(
            remote_path_probe(
                check_id=check_id,
                layer="business",
                path=path,
                ssh_target=args.ssh_target,
                timeout_sec=args.timeout_sec,
                ssh_connect_timeout_sec=args.ssh_connect_timeout_sec,
            )
        )
    checks.append(workflow_probe(args.ssh_target, args.timeout_sec, args.ssh_connect_timeout_sec))
    return checks


def build_dispatch_rollup(results: list[CheckResult]) -> CheckResult:
    wanted_ids = {
        "s2.service.okdesk-pipeline",
        "s2.listener.okdesk_pipeline_3200",
        "s2.workflows.canonical",
        "s2.hb.sla_check",
        "s2.hb.nudge_send",
        "s2.hb.followup_scan",
        "s2.hb.followup_send",
        "s2.hb.dispatch_reminders",
    }
    inputs = [result for result in results if result.id in wanted_ids]
    return rollup_probe(
        check_id="s2.dispatch_liveness",
        layer="business",
        target="S2",
        expected="pipeline up + listener :3200 + canonical workflow state + business heartbeat files fresh within conservative thresholds",
        observed="derived from infra and business probes",
        inputs=inputs,
    )


def overall_status(results: list[CheckResult]) -> str:
    statuses = [result.status for result in results]
    if any(status == STATUS_FAIL for status in statuses):
        return STATUS_FAIL
    if any(status == STATUS_WARN for status in statuses):
        return STATUS_WARN
    if any(status == STATUS_UNKNOWN for status in statuses):
        return STATUS_WARN
    if statuses and all(status == STATUS_OK for status in statuses):
        return STATUS_OK
    return STATUS_UNKNOWN


def build_report(args: argparse.Namespace) -> dict[str, object]:
    checks: list[CheckResult] = []
    if args.mode in {MODE_INFRA, MODE_FULL}:
        checks.extend(build_infra_checks(args))
    if args.mode in {MODE_BUSINESS, MODE_FULL}:
        business_checks = build_business_checks(args)
        checks.extend(business_checks)
    if args.mode in {MODE_BUSINESS, MODE_FULL}:
        checks.append(build_dispatch_rollup(checks))

    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": args.mode,
        "overall_status": overall_status(checks),
        "source_of_truth_date": "2026-03-10/2026-03-11 audits",
        "checks": [asdict(check) for check in checks],
        "summary": {
            STATUS_OK.lower(): sum(1 for check in checks if check.status == STATUS_OK),
            STATUS_WARN.lower(): sum(1 for check in checks if check.status == STATUS_WARN),
            STATUS_FAIL.lower(): sum(1 for check in checks if check.status == STATUS_FAIL),
            STATUS_UNKNOWN.lower(): sum(1 for check in checks if check.status == STATUS_UNKNOWN),
        },
        "not_covered": NOT_COVERED,
    }
    return payload


def render_pretty(report: dict[str, object]) -> str:
    lines = [
        f"Mode: {report['mode']}",
        f"Overall: {report['overall_status']}",
        f"Source: {report['source_of_truth_date']}",
        "",
    ]
    for check in report["checks"]:
        lines.append(f"[{check['status']}] {check['id']}")
        lines.append(f"  expected: {check['expected']}")
        lines.append(f"  observed: {check['observed']}")
        lines.append(f"  probe: {check['probe']}")
        lines.append(f"  follow-up: {check['human_follow_up']}")
        lines.append("")
    lines.append("Not covered:")
    for item in report["not_covered"]:
        lines.append(f"- {item}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report = build_report(args)
    if args.format == "pretty":
        print(render_pretty(report))
    else:
        print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
