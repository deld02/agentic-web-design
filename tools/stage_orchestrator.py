#!/usr/bin/env python3
"""Build the bounded stage packet consumed by chat clients.

The pipeline remains the ordering authority. Agent contracts remain the source
of role knowledge. This module only assembles the active slice so a client does
not need repository access or a large prompt containing the whole system.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from validation_common import load_json


STAGE_GUIDANCE: dict[str, list[str]] = {
    "definition": ["docs/methods/progressive-intake.md", "docs/methods/bounded-execution.md"],
    "research-strategy": ["docs/methods/progressive-intake.md", "docs/methods/reference-to-principle.md", "docs/methods/resource-selection.md"],
    "content-architecture": ["docs/methods/experience-spine.md"],
    "direction-divergence": ["docs/methods/scene-visual-production.md", "docs/methods/material-decisions.md"],
    "direction-review": ["docs/architecture/review-isolation.md", "docs/standards/landing-quality.md"],
    "creative-master": ["docs/methods/scene-visual-production.md", "docs/methods/color-direction.md"],
    "visual-experience": ["docs/methods/typography-spacing.md", "docs/methods/color-direction.md", "docs/methods/scene-color-system.md", "docs/methods/scene-visual-production.md", "docs/methods/effect-selection.md", "docs/methods/spatial-experience.md"],
    "design-review": ["docs/architecture/review-isolation.md", "docs/standards/landing-quality.md", "docs/methods/typography-spacing.md"],
    "technology-selection": ["docs/methods/material-decisions.md", "docs/methods/spatial-experience.md"],
    "production-plan": ["docs/methods/image-decisions.md", "docs/methods/effect-selection.md", "docs/methods/spatial-experience.md"],
    "implementation": ["docs/methods/effect-selection.md", "docs/methods/spatial-experience.md", "docs/standards/accessibility-performance.md"],
    "build-review": ["docs/architecture/review-isolation.md", "docs/standards/landing-quality.md", "docs/methods/typography-spacing.md", "docs/standards/accessibility-performance.md"],
    "release": ["docs/methods/final-delivery.md", "docs/methods/bounded-execution.md"],
}

STAGE_INPUTS: dict[str, list[str]] = {
    "definition": [],
    "research-strategy": ["brief.md", "project.config.json"],
    "content-architecture": ["brief.md", "research-strategy.md"],
    "direction-divergence": ["brief.md", "research-strategy.md", "content-architecture.md"],
    "direction-review": ["brief.md", "research-strategy.md", "content-architecture.md", "creative-direction.md"],
    "creative-master": ["creative-direction.md", "content-architecture.md", "research-strategy.md"],
    "visual-experience": ["creative-direction.md", "content-architecture.md", "research-strategy.md"],
    "design-review": ["creative-direction.md", "content-architecture.md", "visual-system.md"],
    "technology-selection": ["project.config.json", "visual-system.md"],
    "production-plan": ["creative-direction.md", "content-architecture.md", "visual-system.md", "technology-decision.md"],
    "implementation": ["content-architecture.md", "visual-system.md", "technology-decision.md", "production-plan.md"],
    "build-review": ["content-architecture.md", "visual-system.md", "technology-decision.md", "production-plan.md", "qa-release.md"],
    "release": ["project.config.json", "decision-log.md", "qa-release.md"],
}


def _agent_contract(root: Path, agent_id: str) -> Path:
    matches = sorted((root / "agents").glob(f"{agent_id}-*.md"))
    if len(matches) != 1:
        raise ValueError(f"agent {agent_id} must resolve to exactly one contract")
    return matches[0]


def _linked_guidance(root: Path, stage_id: str) -> list[Path]:
    """Resolve only the small guidance set routed to this exact stage."""
    paths = [(root / relative).resolve() for relative in STAGE_GUIDANCE.get(stage_id, [])]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise ValueError(f"stage guidance is missing: {', '.join(missing)}")
    return paths


def _capability_packet(root: Path, stage_id: str) -> dict[str, Any]:
    config = load_json(root / "config" / "design-capabilities.json")
    automatic: list[dict[str, str]] = []
    conditional: list[dict[str, str]] = []
    loaded_references: set[Path] = set()
    for item in config.get("capabilities", []):
        if stage_id not in item.get("allowed_stages", []):
            continue
        summary = {
            "id": item["id"],
            "slot": item["slot"],
            "activation": item["activation"],
            "fallback": item.get("fallback", "none"),
        }
        if item.get("tier") == "core" and item.get("activation") == "automatic":
            reference = (root / item["reference"]).resolve()
            summary["guidance"] = reference.read_text(encoding="utf-8")
            automatic.append(summary)
            loaded_references.add(reference)
        else:
            conditional.append(summary)
    return {
        "automatic": automatic,
        "conditional_candidates": conditional,
        "loaded_reference_paths": loaded_references,
    }


def capability_guidance(root: Path, stage_id: str, capability_id: str) -> dict[str, str]:
    """Return one registered capability only when it belongs to the active stage."""
    config = load_json(root / "config" / "design-capabilities.json")
    item = next((entry for entry in config.get("capabilities", []) if entry.get("id") == capability_id), None)
    if not item or stage_id not in item.get("allowed_stages", []):
        raise ValueError("capability is unknown or unavailable in the active stage")
    reference = (root / item["reference"]).resolve()
    return {
        "id": item["id"],
        "activation": item["activation"],
        "reference": reference.relative_to(root).as_posix(),
        "guidance": reference.read_text(encoding="utf-8"),
    }


def build_stage_packet(
    root: Path,
    project: Path,
    stage: dict[str, Any],
    writable_files: set[str],
) -> dict[str, Any]:
    contract_path = _agent_contract(root, stage["agent"])
    contract = contract_path.read_text(encoding="utf-8")
    capabilities = _capability_packet(root, stage["id"])
    guidance: list[dict[str, str]] = []
    for path in _linked_guidance(root, stage["id"]):
        if path in capabilities["loaded_reference_paths"]:
            continue
        guidance.append({
            "path": path.relative_to(root).as_posix(),
            "text": path.read_text(encoding="utf-8"),
        })
    current: dict[str, str] = {}
    for relative in sorted(writable_files):
        candidate = project / relative
        if candidate.is_file() and candidate.suffix.lower() in {".md", ".json"}:
            current[relative] = candidate.read_text(encoding="utf-8")
    inputs: dict[str, str] = {}
    for relative in STAGE_INPUTS.get(stage["id"], []):
        candidate = project / relative
        if candidate.is_file():
            inputs[relative] = candidate.read_text(encoding="utf-8")
    return {
        "orchestrator": "00 · Design Director",
        "rule": "Execute only this packet. Do not assume or perform work from another stage.",
        "stage": stage["id"],
        "specialist": stage["agent"],
        "mode": stage["mode"],
        "gate": stage.get("gate"),
        "depends_on": stage.get("depends_on", []),
        "writable_files": sorted(writable_files),
        "state_owner": "HARNESS_ORCHESTRATOR",
        "contract": {
            "path": contract_path.relative_to(root).as_posix(),
            "text": contract,
        },
        "linked_guidance": guidance,
        "capabilities": {
            "automatic": capabilities["automatic"],
            "conditional_candidates": capabilities["conditional_candidates"],
        },
        "current_artifacts": current,
        "required_inputs": inputs,
        "completion_protocol": [
            "Edit only writable_files or the implementation root when explicitly allowed.",
            "Create physical evidence required by the contract; a written claim is not evidence.",
            "Call advance_stage once. If it returns REVISE, correct only its findings once.",
            "Do not announce completion unless verify_run returns verified=true.",
        ],
    }


def complete_stage_status(project: Path, stage: dict[str, Any], evidence: list[str]) -> None:
    """Apply the candidate transition as the harness-owned state writer."""
    path = project / "status.json"
    status = load_json(path)
    stage_id = stage["id"]
    gate_id = stage.get("gate")
    decision = "APPROVED"
    if stage_id in {"visual-experience", "implementation"}:
        decision = "REVIEW"
    if gate_id:
        item = status["gates"][gate_id]
    else:
        item = status["checkpoints"][stage_id]
    item.update(status=decision, evidence=sorted(set(evidence)), blockers=[], last_decision=f"{stage_id} validated by harness")
    if stage_id in {"direction-review", "design-review", "build-review"}:
        item["review_context"] = "ISOLATED"
    review_gate = {"design-review": "G3", "build-review": "G4"}.get(stage_id)
    if review_gate:
        status["gates"][review_gate].update(
            status="APPROVED",
            blockers=[],
            last_decision=f"{stage_id} approved by independent review",
        )
    status["status"] = decision
    status["release"]["eligible"] = all(status["gates"][f"G{i}"]["status"] == "APPROVED" for i in range(5))
    status["release"]["reason"] = None if status["release"]["eligible"] else f"{stage_id} completed; pipeline continues"
    path.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def activate_stage_status(project: Path, stage: dict[str, Any]) -> None:
    """Open exactly one successor after the previous stage validates."""
    path = project / "status.json"
    status = load_json(path)
    status.update(
        active_stage=stage["id"],
        active_gate=stage.get("gate"),
        active_agent=stage["agent"],
        active_mode=stage["mode"],
        status="ACTIVE",
    )
    target = status["gates"][stage["gate"]] if stage.get("gate") else status["checkpoints"][stage["id"]]
    target.update(status="ACTIVE", blockers=[], last_decision=None)
    status["release"]["eligible"] = all(status["gates"][f"G{i}"]["status"] == "APPROVED" for i in range(5))
    status["release"]["reason"] = None if status["release"]["eligible"] else f"{stage['id']} active"
    path.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
