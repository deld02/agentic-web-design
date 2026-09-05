"""Create and verify the managed-execution receipt presented to the user."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any
import json
import re

from validation_common import load_json
from validation_project_paths import implementation_root_for
from validation_release_integrity import implementation_digest
from validation_image_generation import is_image_generation_event


SCHEMA_VERSION = 1
RECEIPT_NAME = "execution-receipt.json"
REVIEW_CHECKPOINTS = ("direction-review", "design-review", "build-review")


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _set_field(text: str, name: str, value: str) -> str:
    pattern = rf"(?m)^{re.escape(name)}:\s*.*$"
    replacement = f"{name}: {value}"
    return re.sub(pattern, lambda _match: replacement, text, count=1) if re.search(pattern, text) else text + f"\n{replacement}\n"


def _completed_stages(events: list[dict[str, Any]]) -> list[str]:
    return [item["stage"] for item in events if item.get("event") == "stage_complete"]


def write_execution_receipt(run_dir: Path, repository_root: Path) -> Path:
    """Write proof only after a managed run has actually completed and passed."""
    run_dir, repository_root = run_dir.resolve(), repository_root.resolve()
    run = load_json(run_dir / "run.json")
    report = load_json(run_dir / "report.json")
    pipeline = load_json(repository_root / "config" / "pipeline.json")
    project_dir = run_dir / "project"
    project_status = load_json(project_dir / "status.json")
    events_path = run_dir / "events.jsonl"
    events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    expected_stages = [item["id"] for item in pipeline["stages"]]
    completed = _completed_stages(events)
    master_generated = any(is_image_generation_event(item) and item.get("stage") == "creative-master" for item in events)
    mode = run.get("execution_mode")
    if mode not in {"CHAT_INTERACTIVE", "HEADLESS_MANAGED"}:
        raise ValueError("execution receipt requires a managed execution mode")
    if run.get("status") != "COMPLETE" or report.get("status") != "PASS":
        raise ValueError("execution receipt requires COMPLETE/PASS")
    if completed != expected_stages:
        raise ValueError("execution receipt requires every pipeline stage exactly once and in order")
    if not master_generated:
        raise ValueError("execution receipt requires recorded artistic-master generation")
    if any(item.get("status") != "APPROVED" for item in project_status.get("gates", {}).values()):
        raise ValueError("execution receipt requires all gates approved")
    reviews = project_status.get("checkpoints", {})
    if any(reviews.get(name, {}).get("status") != "APPROVED" or reviews[name].get("review_context") != "ISOLATED" for name in REVIEW_CHECKPOINTS):
        raise ValueError("execution receipt requires approved isolated reviews")

    config = load_json(project_dir / "project.config.json")
    implementation_root = implementation_root_for(project_dir, repository_root, config.get("implementation_root", "undetermined"))
    if not implementation_root.is_dir():
        raise ValueError("execution receipt requires a physical implementation")
    receipt_path = run_dir / RECEIPT_NAME
    qa_path = project_dir / "qa-release.md"
    qa = qa_path.read_text(encoding="utf-8")
    for name, value in (
        ("EXECUTION_MODE", mode), ("HARNESS_RUN_ID", run["run_id"]),
        ("HARNESS_STATUS", "COMPLETE"), ("STAGES_COMPLETED", f"{len(completed)}/{len(expected_stages)}"),
        ("VALIDATION_REPORT", "PASS"), ("EXECUTION_RECEIPT", str(receipt_path.resolve())),
    ):
        qa = _set_field(qa, name, value)
    qa_path.write_text(qa, encoding="utf-8")

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "system_version": pipeline["version"],
        "run_id": run["run_id"],
        "execution_mode": mode,
        "harness_status": "COMPLETE",
        "validation_report": "PASS",
        "stages_completed": completed,
        "gates_approved": sorted(project_status["gates"]),
        "isolated_reviews": list(REVIEW_CHECKPOINTS),
        "artistic_master_generated": master_generated,
        "implementation_sha256": implementation_digest(implementation_root),
        "events_sha256": _sha(events_path),
        "report_sha256": _sha(run_dir / "report.json"),
        "qa_release_sha256": _sha(qa_path),
    }
    payload["receipt_sha256"] = sha256(_canonical(payload)).hexdigest()
    receipt_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt_path


def execution_receipt_errors(receipt_path: Path, repository_root: Path) -> list[str]:
    """Recompute every mutable digest instead of trusting receipt declarations."""
    receipt_path, repository_root = receipt_path.resolve(), repository_root.resolve()
    run_dir = receipt_path.parent
    try:
        receipt = load_json(receipt_path)
        run = load_json(run_dir / "run.json")
        report = load_json(run_dir / "report.json")
        pipeline = load_json(repository_root / "config" / "pipeline.json")
        project_dir = run_dir / "project"
        project_status = load_json(project_dir / "status.json")
        config = load_json(project_dir / "project.config.json")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"execution receipt cannot be read: {exc}"]
    errors: list[str] = []
    if receipt_path.name != RECEIPT_NAME or receipt.get("schema_version") != SCHEMA_VERSION:
        errors.append("execution receipt has an invalid path or schema")
    claimed_digest = receipt.get("receipt_sha256")
    unsigned = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    if claimed_digest != sha256(_canonical(unsigned)).hexdigest():
        errors.append("execution receipt content digest does not match")
    expected_stages = [item["id"] for item in pipeline["stages"]]
    events_path = run_dir / "events.jsonl"
    try:
        events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()] if events_path.is_file() else []
    except (OSError, json.JSONDecodeError) as exc:
        return [f"execution event ledger cannot be read: {exc}"]
    if receipt.get("system_version") != pipeline.get("version"):
        errors.append("execution receipt system version is stale")
    if receipt.get("harness_status") != "COMPLETE" or receipt.get("validation_report") != "PASS":
        errors.append("execution receipt does not declare COMPLETE/PASS")
    if run.get("status") != "COMPLETE" or report.get("status") != "PASS":
        errors.append("managed run is not COMPLETE/PASS")
    if receipt.get("run_id") != run.get("run_id") or receipt.get("execution_mode") != run.get("execution_mode"):
        errors.append("execution receipt does not match the managed run")
    if receipt.get("stages_completed") != expected_stages or _completed_stages(events) != expected_stages:
        errors.append("execution receipt does not prove all pipeline stages in order")
    if receipt.get("gates_approved") != sorted(project_status.get("gates", {})) or receipt.get("isolated_reviews") != list(REVIEW_CHECKPOINTS):
        errors.append("execution receipt approval inventory does not match the project")
    if receipt.get("artistic_master_generated") is not True or not any(is_image_generation_event(item) and item.get("stage") == "creative-master" for item in events):
        errors.append("execution receipt lacks artistic-master generation proof")
    if any(item.get("status") != "APPROVED" for item in project_status.get("gates", {}).values()):
        errors.append("execution receipt project gates are no longer approved")
    reviews = project_status.get("checkpoints", {})
    if any(reviews.get(name, {}).get("status") != "APPROVED" or reviews[name].get("review_context") != "ISOLATED" for name in REVIEW_CHECKPOINTS):
        errors.append("execution receipt isolated reviews are incomplete")
    implementation_root = implementation_root_for(project_dir, repository_root, config.get("implementation_root", "undetermined"))
    checks = (
        (events_path, "events_sha256", "events changed after receipt"),
        (run_dir / "report.json", "report_sha256", "report changed after receipt"),
        (project_dir / "qa-release.md", "qa_release_sha256", "final contract changed after receipt"),
    )
    for path, key, message in checks:
        if not path.is_file() or receipt.get(key) != _sha(path):
            errors.append(message)
    if not implementation_root.is_dir() or receipt.get("implementation_sha256") != implementation_digest(implementation_root):
        errors.append("implementation changed after execution receipt")
    return errors
