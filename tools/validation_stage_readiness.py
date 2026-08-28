#!/usr/bin/env python3
"""Harness stage-exit checks kept separate from execution orchestration."""

from pathlib import Path

from audit_state import audit as audit_state
from project_validation import image_handoff_errors
from validate_gate import validate_gate
from validation_capability_activation import stage_activation_errors
from validation_common import load_json
from validation_image_generation import generated_asset_file_errors
from validation_spatial_experience import spatial_plan_errors, spatial_technology_errors


def stage_readiness_errors(run_dir: Path, stage: dict, root: Path) -> list[str]:
    project_dir = Path(run_dir) / "project"
    status = load_json(project_dir / "status.json")
    stage_id = stage["id"]
    errors = list(audit_state(project_dir))
    errors.extend(stage_activation_errors(project_dir, root, stage_id))
    gate_id = stage.get("gate")
    if gate_id:
        allowed = {"APPROVED"}
        if gate_id in {"G3", "G4"} and stage_id in {"visual-experience", "implementation"}:
            allowed.add("REVIEW")
        gate_status = status.get("gates", {}).get(gate_id, {}).get("status")
        if gate_status not in allowed:
            errors.append(f"{stage_id} left {gate_id} in {gate_status or 'missing'}; expected {sorted(allowed)}")
        if gate_status == "APPROVED":
            errors.extend(validate_gate(project_dir, gate_id))
    else:
        checkpoint = status.get("checkpoints", {}).get(stage_id, {})
        if checkpoint.get("status") != "APPROVED":
            errors.append(f"{stage_id} checkpoint is not APPROVED")
    review_gate = {"design-review": "G3", "build-review": "G4"}.get(stage_id)
    if review_gate:
        if status.get("gates", {}).get(review_gate, {}).get("status") != "APPROVED":
            errors.append(f"{stage_id} must close {review_gate} as APPROVED")
        else:
            errors.extend(validate_gate(project_dir, review_gate))
    if stage_id == "technology-selection":
        errors.extend(spatial_technology_errors(project_dir))
    if stage_id == "production-plan":
        errors.extend(image_handoff_errors(project_dir))
        errors.extend(spatial_plan_errors(project_dir))
        errors.extend(generated_asset_file_errors(project_dir, root))
    return errors
