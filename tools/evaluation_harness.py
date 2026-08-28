#!/usr/bin/env python3
"""Active, reproducible evaluation harness for the landing-design OS.

The harness supervises a real external executor one pipeline stage at a time.
It is not a ninth agent and never grants design or state authority of its own.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_state import audit as audit_state
from project_validation import (
    ROOT,
    artistic_master_errors,
    creative_master_confirmation_errors,
    creative_master_errors,
    load_json,
    project_quality_bar_errors,
)
from validate_gate import validate_gate
from ui_quality_scan import scan_implementation
from validation_capability_activation import stage_capability_instruction
from validation_common import valid_signature
from validation_image_generation import generated_asset_targets, missing_generation_receipts
from validation_project_paths import implementation_root_for
from validation_spatial_experience import spatial_stage_instruction
from validation_stage_readiness import stage_readiness_errors
CONFIG_PATH = ROOT / "harness" / "scenarios.json"
EVENT_TYPES = {
    "stage_start", "stage_complete", "tool_call", "artifact_write",
    "correction", "render", "heartbeat",
}
REVIEW_VALUES = {"PASS", "REVISE"}
IMAGE_TOOLS = {"CHATGPT_GENERATE", "IMAGE_GEN", "IMAGEGEN", "CHATGPT_IMAGE"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    return load_json(path)


def validate_harness_config(data: dict[str, Any], system_version: str | None = None) -> list[str]:
    errors: list[str] = []
    if system_version and data.get("system_version") != system_version:
        errors.append("harness system_version mismatch")
    limits = data.get("limits", {})
    required_limits = {
        "max_total_minutes", "max_stage_minutes",
        "max_corrections_per_stage", "max_repeated_progress",
    }
    if set(limits) != required_limits:
        errors.append("harness limits contract mismatch")
    for key in required_limits:
        if not isinstance(limits.get(key), (int, float)) or limits.get(key, 0) <= 0:
            errors.append(f"harness limit {key} must be positive")
    axes = data.get("visual_review_axes", [])
    if not isinstance(axes, list) or len(axes) < 8 or len(axes) != len(set(axes)):
        errors.append("harness visual_review_axes must contain at least 8 unique axes")
    scenarios = data.get("scenarios", [])
    if not isinstance(scenarios, list) or len(scenarios) < 5:
        errors.append("harness needs at least five scenarios")
        scenarios = []
    seen: set[str] = set()
    required = {"id", "title", "brief", "assets", "identity", "risk_focus"}
    for item in scenarios:
        sid = item.get("id", "")
        if set(item) != required:
            errors.append(f"scenario {sid or '<unknown>'} fields mismatch")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", sid):
            errors.append(f"invalid scenario id {sid}")
        if sid in seen:
            errors.append(f"duplicate scenario id {sid}")
        seen.add(sid)
        if not all(isinstance(item.get(key), str) and item[key].strip() for key in required - {"risk_focus"}):
            errors.append(f"scenario {sid} has empty text fields")
        if not isinstance(item.get("risk_focus"), list) or not item["risk_focus"]:
            errors.append(f"scenario {sid} needs risk_focus")
    return errors


def scenario(data: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    for item in data["scenarios"]:
        if item["id"] == scenario_id:
            return item
    raise ValueError(f"unknown scenario {scenario_id}")


def default_review(axes: list[str]) -> dict[str, Any]:
    return {
        "reviewer": "07",
        "context": "PENDING",
        "verdict": "PENDING",
        "axes": {axis: {"status": "PENDING", "evidence": "", "finding": ""} for axis in axes},
        "blocking_findings": [],
        "reviewed_at": None,
    }


def create_run(
    scenario_id: str,
    runs_root: Path | None = None,
    run_id: str | None = None,
    custom_scenario: dict[str, Any] | None = None,
) -> Path:
    config = load_config()
    errors = validate_harness_config(config)
    if errors:
        raise ValueError("; ".join(errors))
    selected = custom_scenario or scenario(config, scenario_id)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = run_id or f"{stamp}-{scenario_id}"
    if not re.fullmatch(r"[A-Za-z0-9._-]+", run_id):
        raise ValueError("run_id contains unsafe characters")
    runs_root = (runs_root or ROOT / ".harness" / "runs").resolve()
    run_dir = (runs_root / run_id).resolve()
    if run_dir.exists():
        raise FileExistsError(run_dir)
    project_dir = run_dir / "project"
    shutil.copytree(ROOT / "templates" / "project", project_dir)
    for path in project_dir.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".json"}:
            text = path.read_text(encoding="utf-8").replace("replace-me", run_id)
            path.write_text(text, encoding="utf-8")
    brief = project_dir / "brief.md"
    brief.write_text(
        brief.read_text(encoding="utf-8")
        + "\n## Harness scenario\n\n"
        + f"- Scenario: `{selected['id']}` — {selected['title']}\n"
        + f"- Brief: {selected['brief']}\n"
        + f"- Available assets: `{selected['assets']}`\n"
        + f"- Identity mode: `{selected['identity']}`\n"
        + f"- Risks under test: {', '.join(selected['risk_focus'])}\n",
        encoding="utf-8",
    )
    write_json(run_dir / "scenario.json", selected)
    write_json(run_dir / "run.json", {
        "run_id": run_id,
        "scenario": scenario_id,
        "created_at": utc_now(),
        "project_dir": str(project_dir),
        "status": "READY",
    })
    (run_dir / "events.jsonl").write_text("", encoding="utf-8")
    write_json(run_dir / "visual-review.json", default_review(config["visual_review_axes"]))
    (run_dir / "control").mkdir()
    return run_dir


def executor_doctor(command: list[str] | None = None) -> dict[str, Any]:
    """Report whether a genuinely invocable headless executor is available."""
    candidates = [command] if command else [["codex", "--help"], ["claude", "--help"]]
    checks: list[dict[str, Any]] = []
    for candidate in candidates:
        if not candidate:
            continue
        executable = shutil.which(candidate[0])
        item: dict[str, Any] = {"command": candidate, "resolved": executable, "status": "UNAVAILABLE"}
        if executable:
            try:
                probe = subprocess.run(candidate, capture_output=True, text=True, timeout=8, check=False)
                item.update(status="READY" if probe.returncode == 0 else "UNUSABLE", exit_code=probe.returncode)
                if probe.returncode != 0:
                    item["error"] = (probe.stderr or probe.stdout).strip()[:500]
            except (OSError, subprocess.SubprocessError) as exc:
                item.update(status="UNUSABLE", error=str(exc))
        checks.append(item)
    return {
        "status": "READY" if any(item["status"] == "READY" for item in checks) else "NO_EXECUTOR",
        "executors": checks,
        "browser": str(find_browser()) if find_browser() else None,
    }


def _file_snapshot(project_dir: Path) -> dict[str, tuple[int, int]]:
    result: dict[str, tuple[int, int]] = {}
    for path in project_dir.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            stat = path.stat()
            result[str(path.relative_to(project_dir))] = (stat.st_mtime_ns, stat.st_size)
    return result


def _save_chat_snapshot(run_dir: Path) -> None:
    write_json(
        run_dir / "control" / "chat-snapshot.json",
        {name: list(value) for name, value in _file_snapshot(run_dir / "project").items()},
    )


def _current_open_stage(run_dir: Path) -> dict[str, Any]:
    stages, stage_map = _pipeline()
    events = read_events(run_dir)
    completed = {item["stage"] for item in events if item.get("event") == "stage_complete"}
    open_starts = [
        item for item in events
        if item.get("event") == "stage_start" and item.get("stage") not in completed
    ]
    if len(open_starts) != 1:
        raise ValueError(f"interactive run needs exactly one open stage; found {len(open_starts)}")
    stage_id = open_starts[0]["stage"]
    if stage_id not in stage_map:
        raise ValueError(f"unknown interactive stage {stage_id}")
    return stage_map[stage_id]


def start_chat_run(
    scenario_id: str | None,
    runs_root: Path | None = None,
    run_id: str | None = None,
    brief_text: str | None = None,
) -> dict[str, Any]:
    """Start a harness-managed run whose executor is the current ChatGPT conversation."""
    if brief_text and brief_text.strip():
        scenario_id = scenario_id or "custom-landing"
        custom = {
            "id": scenario_id,
            "title": "Custom landing brief",
            "brief": brief_text.strip(),
            "assets": "Use only assets explicitly supplied or produced through the system",
            "identity": "Determine from research and supplied material",
            "risk_focus": ["brief_specificity", "generic_ai_output", "missing_visual_payload"],
        }
    else:
        if not scenario_id:
            raise ValueError("chat-start needs --scenario or --brief-file")
        custom = None
    run_dir = create_run(scenario_id, runs_root, run_id, custom)
    first = _pipeline()[0][0]
    run = load_json(run_dir / "run.json")
    run.update(status="RUNNING", execution_mode="CHAT_INTERACTIVE", active_stage=first["id"], executor_started_at=utc_now())
    write_json(run_dir / "run.json", run)
    append_event(run_dir, {"event": "stage_start", "stage": first["id"], "agent": first["agent"]})
    _save_chat_snapshot(run_dir)
    return chat_status(run_dir)


def _require_chat_run(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    run = load_json(run_dir / "run.json")
    if run.get("execution_mode") != "CHAT_INTERACTIVE":
        raise ValueError("run is not a CHAT_INTERACTIVE execution")
    if run.get("status") not in {"RUNNING", "NEEDS_USER"}:
        raise ValueError(f"interactive run is not active: {run.get('status')}")
    return run


def chat_status(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    run = _require_chat_run(run_dir)
    stage = _current_open_stage(run_dir)
    return {
        "status": run["status"],
        "execution_mode": "CHAT_INTERACTIVE",
        "run_dir": str(run_dir),
        "project_dir": str((run_dir / "project").resolve()),
        "stage": stage["id"],
        "agent": stage["agent"],
        "mode": stage["mode"],
        "instruction": " ".join(filter(None, (
            "Complete only this stage, then call chat-next. Do not work ahead.",
            stage_capability_instruction(ROOT, stage["id"]),
            spatial_stage_instruction(run_dir / "project", stage["id"]),
        ))),
    }


def confirm_chat_image(run_dir: Path, image_path: Path, asset_id: str | None = None) -> dict[str, Any]:
    """Record a real generated master or production-plan image."""
    run_dir = run_dir.resolve()
    _require_chat_run(run_dir)
    stage = _current_open_stage(run_dir)
    if stage["id"] not in {"creative-master", "production-plan"}:
        raise ValueError("chat-image is valid only during creative-master or production-plan")
    project_dir = (run_dir / "project").resolve()
    base = project_dir
    if stage["id"] == "production-plan":
        targets = generated_asset_targets(project_dir)
        if not asset_id or asset_id not in targets:
            raise ValueError("production-plan chat-image needs a declared generated --asset-id")
        config = load_json(project_dir / "project.config.json")
        base = implementation_root_for(project_dir, ROOT, config.get("implementation_root", "undetermined"))
    candidate = image_path if image_path.is_absolute() else base / image_path
    candidate = candidate.resolve()
    if not _inside(candidate, base):
        raise ValueError("generated image must be inside its managed output root")
    if stage["id"] == "production-plan" and candidate != (base / targets[asset_id]).resolve():
        raise ValueError("generated image path does not match the declared IMG final file")
    if candidate.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".avif"}:
        raise ValueError("generated master must be a raster image")
    if not candidate.is_file() or not valid_signature(candidate):
        raise ValueError("generated master is missing or is not a valid raster file")
    relative = str(candidate.relative_to(project_dir if _inside(candidate, project_dir) else base))
    append_event(run_dir, {"event": "tool_call", "stage": stage["id"], "agent": stage["agent"], "tool": "CHATGPT_IMAGE", "target": asset_id})
    append_event(run_dir, {"event": "artifact_write", "stage": stage["id"], "agent": stage["agent"], "target": relative})
    return {"status": "RECORDED", "stage": stage["id"], "file": relative}


def advance_chat_run(run_dir: Path) -> dict[str, Any]:
    """Validate the open chat stage and open exactly one successor."""
    run_dir = run_dir.resolve()
    run = _require_chat_run(run_dir)
    stage = _current_open_stage(run_dir)
    snapshot_path = run_dir / "control" / "chat-snapshot.json"
    previous_raw = load_json(snapshot_path) if snapshot_path.is_file() else {}
    previous = {name: tuple(value) for name, value in previous_raw.items()}
    current = _file_snapshot(run_dir / "project")
    already_recorded = {
        item.get("target") for item in read_events(run_dir)
        if item.get("event") == "artifact_write" and item.get("stage") == stage["id"]
    }
    for target in sorted(name for name, value in current.items() if previous.get(name) != value and name not in already_recorded):
        append_event(run_dir, {"event": "artifact_write", "stage": stage["id"], "agent": stage["agent"], "target": target})

    readiness = stage_readiness_errors(run_dir, stage, ROOT)
    if stage["id"] == "creative-master":
        generated = any(
            item.get("event") == "tool_call" and item.get("stage") == "creative-master"
            and re.sub(r"[^A-Z0-9]+", "_", str(item.get("tool", "")).upper()).strip("_") in IMAGE_TOOLS
            for item in read_events(run_dir)
        )
        if not generated:
            readiness.append("creative-master needs a physical image registered with chat-image after real generation")
    if stage["id"] == "production-plan":
        for generated_id in missing_generation_receipts(run_dir / "project", read_events(run_dir), IMAGE_TOOLS):
            readiness.append(f"production-plan generated asset {generated_id} lacks a real image-generation receipt")
    if readiness:
        if any("artistic master confirmation is PENDING" in item for item in readiness):
            run.update(status="NEEDS_USER", active_stage=stage["id"], findings=readiness)
            write_json(run_dir / "run.json", run)
            _save_chat_snapshot(run_dir)
            return chat_status(run_dir) | {"findings": readiness}
        corrections = sum(
            item.get("event") == "correction" and item.get("stage") == stage["id"]
            for item in read_events(run_dir)
        )
        if corrections < load_config()["limits"]["max_corrections_per_stage"]:
            append_event(run_dir, {"event": "correction", "stage": stage["id"], "agent": stage["agent"], "progress_key": "chat-validator-correction"})
            run.update(status="RUNNING", active_stage=stage["id"], findings=readiness)
            write_json(run_dir / "run.json", run)
            _save_chat_snapshot(run_dir)
            return chat_status(run_dir) | {"status": "REVISE", "findings": readiness}
        run.update(status="FAILED", active_stage=stage["id"], findings=readiness, executor_finished_at=utc_now())
        write_json(run_dir / "run.json", run)
        return {"status": "FAILED", "stage": stage["id"], "findings": readiness}

    append_event(run_dir, {"event": "stage_complete", "stage": stage["id"], "agent": stage["agent"]})
    stages, _stage_map = _pipeline()
    index = next(i for i, item in enumerate(stages) if item["id"] == stage["id"])
    if index == len(stages) - 1:
        report = evaluate(run_dir)
        run = load_json(run_dir / "run.json")
        run.update(status="COMPLETE" if report["status"] == "PASS" else "FAILED", executor_finished_at=utc_now(), report_status=report["status"])
        write_json(run_dir / "run.json", run)
        return {"status": run["status"], "run_dir": str(run_dir), "report": report["status"], "findings": report["findings"]}
    next_stage = stages[index + 1]
    append_event(run_dir, {"event": "stage_start", "stage": next_stage["id"], "agent": next_stage["agent"]})
    run = load_json(run_dir / "run.json")
    run.update(status="RUNNING", active_stage=next_stage["id"], findings=[])
    write_json(run_dir / "run.json", run)
    _save_chat_snapshot(run_dir)
    return chat_status(run_dir)


def _stage_prompt(run_dir: Path, stage: dict[str, Any], correction: list[str] | None = None) -> str:
    scenario_data = load_json(run_dir / "scenario.json")
    contract = ROOT / "agents" / f"{stage['agent']}-"
    matching = sorted((ROOT / "agents").glob(f"{stage['agent']}-*.md"))
    contract_path = matching[0] if matching else contract
    lines = [
        "Execute exactly one Agentic Web Design OS stage.",
        "Execution mode: MANAGED. The HARNESS_* environment values supplied with this prompt are mandatory proof of that mode.",
        f"Stage: {stage['id']}",
        f"Owner: {stage['agent']}",
        f"Mode: {stage['mode']}",
        f"Project directory: {(run_dir / 'project').resolve()}",
        f"Scenario: {scenario_data['brief']}",
        f"Agent contract: {contract_path}",
        f"Pipeline authority: {ROOT / 'config' / 'pipeline.json'}",
        stage_capability_instruction(ROOT, stage["id"]),
        spatial_stage_instruction(run_dir / "project", stage["id"]),
        "Work only inside the isolated project and its configured implementation root.",
        "Complete only this stage, update its owned artifact, and let agent 00 update official state as required by the pipeline.",
        "Do not publish, push, create GitHub content or skip a dependency.",
        "For a real master image call, emit after success: HARNESS_EVENT {\"event\":\"tool_call\",\"tool\":\"IMAGE_GEN\"}. During production-plan also include the declared asset target, for example \"target\":\"IMG-001\".",
        "Exit non-zero if the stage cannot be completed honestly.",
    ]
    if correction:
        lines.extend(["This is the single allowed correction pass. Resolve these validator findings:"] + [f"- {item}" for item in correction])
    return "\n".join(lines) + "\n"


def _parse_executor_events(run_dir: Path, stage: dict[str, Any], stdout: str) -> None:
    prefix = "HARNESS_EVENT "
    for line in stdout.splitlines():
        if not line.startswith(prefix):
            continue
        try:
            payload = json.loads(line[len(prefix):])
            payload.update(stage=stage["id"], agent=stage["agent"])
            append_event(run_dir, payload)
        except (ValueError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid executor event: {line}: {exc}") from exc


def _run_stage_process(run_dir: Path, stage: dict[str, Any], command: list[str], correction: list[str] | None = None, timeout_seconds: float | None = None) -> tuple[int, str, str]:
    config = load_config()
    prompt = _stage_prompt(run_dir, stage, correction)
    prompt_path = run_dir / "control" / f"{stage['id']}{'-correction' if correction else ''}.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    environment = os.environ.copy()
    environment.update({
        "HARNESS_RUN_DIR": str(run_dir.resolve()),
        "HARNESS_PROJECT_DIR": str((run_dir / "project").resolve()),
        "HARNESS_SCENARIO": load_json(run_dir / "scenario.json")["id"],
        "HARNESS_STAGE": stage["id"],
        "HARNESS_AGENT": stage["agent"],
        "HARNESS_MODE": stage["mode"],
        "HARNESS_PROMPT_FILE": str(prompt_path.resolve()),
    })
    try:
        completed = subprocess.run(
            command, cwd=run_dir / "project", env=environment, input=prompt,
            capture_output=True, text=True,
            timeout=timeout_seconds or config["limits"]["max_stage_minutes"] * 60, check=False,
        )
        return completed.returncode, completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", exc.stderr or "stage timeout"
    except OSError as exc:
        return 127, "", f"executor could not start: {exc}"


def run_active(run_dir: Path, command: list[str], until: str | None = None) -> dict[str, Any]:
    """Actively execute and validate pipeline stages through a headless adapter."""
    if not command:
        raise ValueError("active run needs an executor command after --")
    run_dir = run_dir.resolve()
    if not (run_dir / "run.json").is_file():
        raise ValueError("run directory is not initialized")
    stages, _stage_map = _pipeline()
    config = load_config()
    run_started = time.monotonic()
    existing_events = read_events(run_dir)
    completed = {event["stage"] for event in existing_events if event.get("event") == "stage_complete"}
    started = {event["stage"] for event in existing_events if event.get("event") == "stage_start"}
    run = load_json(run_dir / "run.json")
    run.update(status="RUNNING", executor_command=command, executor_started_at=utc_now())
    write_json(run_dir / "run.json", run)
    for stage in stages:
        if stage["id"] in completed:
            if stage["id"] == until:
                break
            continue
        if stage["id"] not in started:
            append_event(run_dir, {"event": "stage_start", "stage": stage["id"], "agent": stage["agent"]})
        elif not stage_readiness_errors(run_dir, stage, ROOT):
            append_event(run_dir, {"event": "stage_complete", "stage": stage["id"], "agent": stage["agent"]})
            if stage["id"] == until:
                run = load_json(run_dir / "run.json")
                run.update(status="PARTIAL", active_stage=stage["id"], executor_finished_at=utc_now())
                write_json(run_dir / "run.json", run)
                return run
            continue
        readiness: list[str] = []
        for attempt in range(2):
            remaining_total = config["limits"]["max_total_minutes"] * 60 - (time.monotonic() - run_started)
            if remaining_total <= 0:
                readiness = ["run exceeded total execution budget"]
                break
            before = _file_snapshot(run_dir / "project")
            code, stdout, stderr = _run_stage_process(
                run_dir, stage, command, readiness or None,
                min(config["limits"]["max_stage_minutes"] * 60, remaining_total),
            )
            suffix = "-correction" if attempt else ""
            (run_dir / f"executor-{stage['id']}{suffix}.stdout.log").write_text(stdout, encoding="utf-8")
            (run_dir / f"executor-{stage['id']}{suffix}.stderr.log").write_text(stderr, encoding="utf-8")
            _parse_executor_events(run_dir, stage, stdout)
            after = _file_snapshot(run_dir / "project")
            for target in sorted(name for name, value in after.items() if before.get(name) != value):
                append_event(run_dir, {"event": "artifact_write", "stage": stage["id"], "agent": stage["agent"], "target": target})
            if code != 0:
                readiness = [f"executor exited {code}: {(stderr or stdout).strip()[:1000]}"]
            else:
                readiness = stage_readiness_errors(run_dir, stage, ROOT)
            if not readiness:
                break
            if any("artistic master confirmation is PENDING" in item for item in readiness):
                run = load_json(run_dir / "run.json")
                run.update(status="NEEDS_USER", active_stage=stage["id"], findings=readiness)
                write_json(run_dir / "run.json", run)
                return run
            if attempt == 0:
                append_event(run_dir, {"event": "correction", "stage": stage["id"], "agent": stage["agent"], "progress_key": "validator-correction"})
        if readiness:
            run = load_json(run_dir / "run.json")
            run.update(status="FAILED", active_stage=stage["id"], findings=readiness, executor_finished_at=utc_now())
            write_json(run_dir / "run.json", run)
            return run
        append_event(run_dir, {"event": "stage_complete", "stage": stage["id"], "agent": stage["agent"]})
        if stage["id"] == until:
            run = load_json(run_dir / "run.json")
            run.update(status="PARTIAL", active_stage=stage["id"], executor_finished_at=utc_now())
            write_json(run_dir / "run.json", run)
            return run
    report = evaluate(run_dir)
    run = load_json(run_dir / "run.json")
    run.update(status="COMPLETE" if report["status"] == "PASS" else "FAILED", executor_finished_at=utc_now(), report_status=report["status"])
    write_json(run_dir / "run.json", run)
    return run


def _pipeline() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    stages = load_json(ROOT / "config" / "pipeline.json")["stages"]
    return stages, {item["id"]: item for item in stages}


def read_events(run_dir: Path) -> list[dict[str, Any]]:
    path = run_dir / "events.jsonl"
    events: list[dict[str, Any]] = []
    if not path.is_file():
        return events
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid event JSON at line {number}: {exc}") from exc
        events.append(event)
    return events


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def append_event(run_dir: Path, event: dict[str, Any]) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    if event.get("event") not in EVENT_TYPES:
        raise ValueError(f"unknown event type {event.get('event')}")
    _stages, stage_map = _pipeline()
    stage_id = event.get("stage")
    if stage_id not in stage_map:
        raise ValueError(f"unknown stage {stage_id}")
    if event.get("agent") != stage_map[stage_id]["agent"]:
        raise ValueError(f"agent {event.get('agent')} does not own {stage_id}")
    if event["event"] == "tool_call" and not str(event.get("tool", "")).strip():
        raise ValueError("tool_call needs tool")
    if event["event"] == "artifact_write":
        target = event.get("target")
        if not target:
            raise ValueError("artifact_write needs target")
        project_dir = run_dir / "project"
        candidate = Path(target)
        if not candidate.is_absolute():
            candidate = project_dir / candidate
        allowed = [project_dir]
        project_config = load_json(project_dir / "project.config.json")
        implementation = project_config.get("implementation_root")
        if implementation and implementation != "undetermined":
            implementation_path = Path(implementation)
            if not implementation_path.is_absolute():
                implementation_path = project_dir / implementation_path
            if _inside(implementation_path, project_dir):
                allowed.append(implementation_path)
        if not any(_inside(candidate, root) for root in allowed):
            raise ValueError("artifact target is outside the isolated project/implementation roots")
    events = read_events(run_dir)
    item = dict(event)
    item["seq"] = len(events) + 1
    item["at"] = event.get("at") or utc_now()
    with (run_dir / "events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    return item


def event_findings(run_dir: Path, now: datetime | None = None) -> list[dict[str, str]]:
    config = load_config()
    limits = config["limits"]
    stages, stage_map = _pipeline()
    order = {item["id"]: index for index, item in enumerate(stages)}
    events = read_events(run_dir)
    findings: list[dict[str, str]] = []

    def add(code: str, message: str, severity: str = "BLOCKING") -> None:
        findings.append({"code": code, "severity": severity, "message": message})

    started: dict[str, dict[str, Any]] = {}
    completed: dict[str, dict[str, Any]] = {}
    correction_count: dict[str, int] = {}
    previous_time: datetime | None = None
    progress_key = None
    repeated = 0
    image_generation_seen = False
    for item in events:
        event_type = item.get("event")
        stage_id = item.get("stage")
        if event_type not in EVENT_TYPES or stage_id not in stage_map:
            add("EVENT_CONTRACT", f"event {item.get('seq')} has invalid type or stage")
            continue
        if item.get("agent") != stage_map[stage_id]["agent"]:
            add("OWNERSHIP", f"{stage_id} was acted on by {item.get('agent')}")
        try:
            moment = parse_time(item["at"])
        except (KeyError, ValueError):
            add("EVENT_TIME", f"event {item.get('seq')} has invalid timestamp")
            continue
        if previous_time and moment < previous_time:
            add("EVENT_TIME", "event timestamps are not monotonic")
        previous_time = moment
        key = item.get("progress_key")
        if key and key == progress_key:
            repeated += 1
        elif key:
            progress_key, repeated = key, 1
        if repeated > limits["max_repeated_progress"]:
            add("STALL", f"progress {key} repeated more than {limits['max_repeated_progress']} times")
        if event_type == "stage_start":
            if stage_id in started:
                add("STAGE_REPEAT", f"{stage_id} started more than once")
            for dependency in stage_map[stage_id].get("depends_on", []):
                if dependency not in completed:
                    add("PIPELINE_ORDER", f"{stage_id} started before {dependency} completed")
            preceding = [s["id"] for s in stages[:order[stage_id]]]
            missing = [sid for sid in preceding if sid not in completed]
            if missing:
                add("PIPELINE_SKIP", f"{stage_id} skipped preceding stages: {', '.join(missing)}")
            if stage_id == "visual-experience" and not image_generation_seen:
                physical_master_exists = not artistic_master_errors(run_dir / "project")
                if not physical_master_exists:
                    add("MASTER_NOT_GENERATED", "visual-experience started without a recorded image-generation call or valid physical master")
            started[stage_id] = item
        elif event_type == "stage_complete":
            if stage_id not in started:
                add("STAGE_LIFECYCLE", f"{stage_id} completed without start")
            if stage_id in completed:
                add("STAGE_REPEAT", f"{stage_id} completed more than once")
            completed[stage_id] = item
        elif event_type == "correction":
            correction_count[stage_id] = correction_count.get(stage_id, 0) + 1
            if correction_count[stage_id] > limits["max_corrections_per_stage"]:
                add("CORRECTION_LIMIT", f"{stage_id} exceeded its correction budget")
        elif event_type == "tool_call" and stage_id == "creative-master":
            normalized = re.sub(r"[^A-Z0-9]+", "_", str(item.get("tool", "")).upper()).strip("_")
            if normalized in IMAGE_TOOLS or "IMAGE_GEN" in normalized or "IMAGEGEN" in normalized:
                image_generation_seen = True

    for stage_id, start in started.items():
        end = completed.get(stage_id)
        end_time = parse_time(end["at"]) if end else (now or datetime.now(timezone.utc))
        minutes = (end_time - parse_time(start["at"])).total_seconds() / 60
        if minutes > limits["max_stage_minutes"]:
            add("STAGE_TIMEOUT", f"{stage_id} took {minutes:.1f} min (limit {limits['max_stage_minutes']})")
    if events:
        total = ((now or datetime.now(timezone.utc)) - parse_time(events[0]["at"])).total_seconds() / 60
        if completed.get("release"):
            total = (parse_time(completed["release"]["at"]) - parse_time(events[0]["at"])).total_seconds() / 60
        if total > limits["max_total_minutes"]:
            add("RUN_TIMEOUT", f"run took {total:.1f} min (limit {limits['max_total_minutes']})")
    return findings


def visual_review_findings(run_dir: Path) -> list[dict[str, str]]:
    events = read_events(run_dir)
    review_required = any(
        item.get("stage") in {"build-review", "release"} and item.get("event") in {"stage_start", "stage_complete"}
        for item in events
    )
    if not review_required:
        return []
    findings: list[dict[str, str]] = []
    path = run_dir / "visual-review.json"
    if not path.is_file():
        return [{"code": "VISUAL_REVIEW", "severity": "BLOCKING", "message": "visual-review.json is missing"}]
    review = load_json(path)
    axes = load_config()["visual_review_axes"]
    if review.get("reviewer") != "07" or review.get("context") != "ISOLATED":
        findings.append({"code": "REVIEW_ISOLATION", "severity": "BLOCKING", "message": "final visual review must be by 07 in ISOLATED context"})
    values: list[str] = []
    for axis in axes:
        item = review.get("axes", {}).get(axis, {})
        values.append(item.get("status"))
        if item.get("status") not in REVIEW_VALUES or not str(item.get("evidence", "")).strip():
            findings.append({"code": "VISUAL_AXIS", "severity": "BLOCKING", "message": f"{axis} needs PASS|REVISE and concrete evidence"})
    verdict = review.get("verdict")
    if verdict not in REVIEW_VALUES:
        findings.append({"code": "VISUAL_VERDICT", "severity": "BLOCKING", "message": "visual verdict must be PASS or REVISE"})
    if verdict == "PASS" and ("REVISE" in values or review.get("blocking_findings")):
        findings.append({"code": "FALSE_PASS", "severity": "BLOCKING", "message": "visual review PASS conflicts with findings"})
    return findings


def evaluate(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    project_dir = run_dir / "project"
    findings = event_findings(run_dir)
    for message in audit_state(project_dir):
        findings.append({"code": "STATE_DRIFT", "severity": "BLOCKING", "message": message})
    status = load_json(project_dir / "status.json")
    for gate_id, item in status.get("gates", {}).items():
        if item.get("status") == "APPROVED":
            for message in validate_gate(project_dir, gate_id):
                findings.append({"code": f"{gate_id}_INVALID", "severity": "BLOCKING", "message": message})
    completed = {item.get("stage") for item in read_events(run_dir) if item.get("event") == "stage_complete"}
    if "release" not in completed:
        findings.append({"code": "PIPELINE_INCOMPLETE", "severity": "BLOCKING", "message": "release has not completed; this run cannot pass"})
    if "creative-master" in completed:
        for validator in (
            project_quality_bar_errors,
            artistic_master_errors,
            creative_master_confirmation_errors,
            creative_master_errors,
        ):
            for message in validator(project_dir):
                findings.append({"code": "CREATIVE_DIRECTION", "severity": "BLOCKING", "message": message})
    findings.extend(visual_review_findings(run_dir))
    project_config = load_json(project_dir / "project.config.json")
    implementation_value = project_config.get("implementation_root")
    if implementation_value not in {None, "", "undetermined"}:
        implementation_root = Path(implementation_value)
        if not implementation_root.is_absolute():
            implementation_root = project_dir / implementation_root
        if _inside(implementation_root, project_dir) and implementation_root.is_dir():
            quality = scan_implementation(implementation_root)
            write_json(run_dir / "quality-scan.json", quality)
            for item in quality["findings"]:
                findings.append({
                    "code": f"STATIC_{item['rule']}",
                    "severity": "BLOCKING" if item["severity"] == "CRITICAL" else "ADVISORY",
                    "message": f"{item['file']}:{item.get('line', 1)} — {item['message']}",
                })
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in findings:
        key = (item["code"], item["message"])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    events = read_events(run_dir)
    report = {
        "run_id": load_json(run_dir / "run.json")["run_id"],
        "evaluated_at": utc_now(),
        "status": "PASS" if not any(item["severity"] == "BLOCKING" for item in unique) else "FAIL",
        "metrics": {
            "events": len(events),
            "stages_started": len({e["stage"] for e in events if e.get("event") == "stage_start"}),
            "stages_completed": len({e["stage"] for e in events if e.get("event") == "stage_complete"}),
            "corrections": sum(e.get("event") == "correction" for e in events),
            "renders": sum(e.get("event") == "render" for e in events),
        },
        "findings": unique,
    }
    write_json(run_dir / "report.json", report)
    lines = [f"# Harness report — {report['run_id']}", "", f"Status: **{report['status']}**", "", "## Findings", ""]
    lines.extend(f"- **{item['code']}** — {item['message']}" for item in unique)
    if not unique:
        lines.append("- No blocking findings.")
    (run_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def find_browser() -> Path | None:
    for name in ("msedge", "chrome", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return Path(found)
    candidates = [
        Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft/Edge/Application/msedge.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Google/Chrome/Application/chrome.exe",
    ]
    return next((path for path in candidates if path.is_file()), None)


def capture(run_dir: Path, url: str, label: str = "final") -> list[Path]:
    if not re.fullmatch(r"[A-Za-z0-9._-]+", label):
        raise ValueError("unsafe capture label")
    browser = find_browser()
    if not browser:
        raise RuntimeError("Chrome/Edge not found; provide physical renders manually")
    evidence = run_dir / "project" / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for viewport, size in (("desktop", "1440,1200"), ("mobile", "390,844")):
        output = (evidence / f"harness-{label}-{viewport}.png").resolve()
        command = [
            str(browser), "--headless=new", "--disable-gpu", "--hide-scrollbars",
            f"--window-size={size}", f"--screenshot={output}", url,
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)
        if completed.returncode != 0 or not output.is_file():
            raise RuntimeError(f"browser capture failed: {completed.stderr.strip()}")
        append_event(run_dir, {
            "event": "render", "stage": "implementation", "agent": "06",
            "target": str(output.relative_to(run_dir / "project")), "viewport": viewport,
        })
        outputs.append(output)
    return outputs


def _referenced_files(project_dir: Path) -> list[Path]:
    extensions = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".mp4", ".webm"}
    found: set[Path] = set()
    for document in project_dir.rglob("*.md"):
        text = document.read_text(encoding="utf-8", errors="replace")
        for token in re.findall(r"(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?:png|jpe?g|webp|avif|gif|mp4|webm)", text, re.I):
            candidate = project_dir / token
            if candidate.is_file() and _inside(candidate, project_dir):
                found.add(candidate.resolve())
    for path in (project_dir / "evidence").glob("*") if (project_dir / "evidence").is_dir() else []:
        if path.is_file() and path.suffix.lower() in extensions:
            found.add(path.resolve())
    return sorted(found)


def create_packet(run_dir: Path) -> Path:
    run_dir = run_dir.resolve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    packet = run_dir / "review-packets" / stamp
    suffix = 1
    while packet.exists():
        packet = run_dir / "review-packets" / f"{stamp}-{suffix}"
        suffix += 1
    artifacts = packet / "artifacts"
    evidence = packet / "evidence"
    artifacts.mkdir(parents=True)
    evidence.mkdir(parents=True)
    project_dir = run_dir / "project"
    manifest: list[dict[str, str]] = []

    def copy(source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        manifest.append({"source": str(source), "snapshot": str(destination.relative_to(packet)), "sha256": digest})

    for source in sorted(project_dir.rglob("*")):
        if source.is_file() and source.suffix.lower() in {".md", ".json"}:
            copy(source, artifacts / source.relative_to(project_dir))
    for index, source in enumerate(_referenced_files(project_dir), 1):
        copy(source, evidence / f"{index:03d}-{source.name}")
    for name in ("scenario.json", "run.json", "events.jsonl", "report.json", "report.md", "visual-review.json", "quality-scan.json"):
        source = run_dir / name
        if source.is_file():
            copy(source, packet / "harness" / name)
    write_json(packet / "manifest.json", {"created_at": utc_now(), "files": manifest})
    review_lines = [
        "# Isolated visual-review packet", "",
        "Reviewer: agent `07`; context must be `ISOLATED`.", "",
        "Inspect the artistic master, current references, executable renders, transitions, responsive evidence and all configured axes. Do not infer quality from gate status.", "",
        "## Required axes", "",
    ]
    review_lines.extend(f"- {axis}" for axis in load_config()["visual_review_axes"])
    (packet / "review.md").write_text("\n".join(review_lines) + "\n", encoding="utf-8")
    return packet


def execute(run_dir: Path, command: list[str]) -> int:
    if not command:
        raise ValueError("execute needs a command after --")
    config = load_config()
    environment = os.environ.copy()
    environment.update({
        "HARNESS_RUN_DIR": str(run_dir.resolve()),
        "HARNESS_PROJECT_DIR": str((run_dir / "project").resolve()),
        "HARNESS_SCENARIO": load_json(run_dir / "scenario.json")["id"],
    })
    started = utc_now()
    try:
        result = subprocess.run(
            command, cwd=run_dir / "project", env=environment,
            capture_output=True, text=True,
            timeout=config["limits"]["max_total_minutes"] * 60,
            check=False,
        )
        code = result.returncode
        stdout, stderr = result.stdout, result.stderr
        status = "COMPLETE" if code == 0 else "FAILED"
    except subprocess.TimeoutExpired as exc:
        code, status = 124, "TIMEOUT"
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
    (run_dir / "executor.stdout.log").write_text(stdout, encoding="utf-8")
    (run_dir / "executor.stderr.log").write_text(stderr, encoding="utf-8")
    run = load_json(run_dir / "run.json")
    run.update({"executor_started_at": started, "executor_finished_at": utc_now(), "executor_status": status, "executor_exit_code": code})
    write_json(run_dir / "run.json", run)
    return code


def main() -> int:
    from harness_cli import run_cli

    return run_cli(sys.modules[__name__])


if __name__ == "__main__":
    sys.exit(main())
