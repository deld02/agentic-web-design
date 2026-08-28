#!/usr/bin/env python3
"""Route and verify design capabilities that the registry marks as automatic."""

from __future__ import annotations

import json
from pathlib import Path
import re

from validation_common import table_rows


STAGE_ARTIFACT = {
    "content-architecture": "content-architecture.md",
    "direction-divergence": "creative-direction.md",
    "creative-master": "creative-direction.md",
    "visual-experience": "visual-system.md",
    "design-review": "visual-system.md",
    "production-plan": "production-plan.md",
    "build-review": "qa-release.md",
}
GATE_STAGES = {
    "G1": ("content-architecture",),
    "G2": ("direction-divergence", "creative-master"),
    "G3": ("visual-experience", "design-review"),
    "G4": ("production-plan", "build-review"),
    "G5": ("build-review",),
}


def _registry(root: Path) -> dict:
    return json.loads((root / "config" / "design-capabilities.json").read_text(encoding="utf-8"))


def automatic_for_stage(root: Path, stage_id: str) -> list[dict]:
    return [
        item for item in _registry(root).get("capabilities", [])
        if item.get("tier") == "core" and item.get("activation") == "automatic"
        and stage_id in item.get("allowed_stages", [])
    ]


def stage_capability_instruction(root: Path, stage_id: str) -> str:
    registry = _registry(root)
    router = root / registry["policy"]["skill_entrypoint"]
    required = automatic_for_stage(root, stage_id)
    details = "; ".join(f"{item['id']} via {root / item['reference']}" for item in required) or "none"
    conditional = ", ".join(item["id"] for item in registry.get("capabilities", []) if item.get("activation") != "automatic" and stage_id in item.get("allowed_stages", [])) or "none"
    return f"Capability router: {router}. Read it before work. Required core capabilities: {details}. Conditional candidates to test only by their registered trigger: {conditional}. Log every activation with Mode={stage_id}; use the registered fallback if an external source is unavailable."


def _logged_modes(project_dir: Path, artifact: str) -> set[tuple[str, str]]:
    path = project_dir / artifact
    if not path.is_file():
        return set()
    text = path.read_text(encoding="utf-8")
    rows = table_rows(text, "## Design capability log", "Capability")
    return {(row[0], row[1]) for row in rows if len(row) >= 2 and row[0] and row[1]}


def _has_material_motion(project_dir: Path) -> bool:
    path = project_dir / "production-plan.md"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    rows = table_rows(text, "## Page visual narrative map", "Scene ID")
    return any(len(row) >= 6 and row[5] != "STATIC" for row in rows)


def stage_activation_errors(project_dir: Path, root: Path, stage_id: str) -> list[str]:
    artifact = STAGE_ARTIFACT.get(stage_id)
    if not artifact:
        return []
    logged = _logged_modes(project_dir, artifact)
    errors = [
        f"{stage_id} must log automatic capability {item['id']} with Mode={stage_id}"
        for item in automatic_for_stage(root, stage_id)
        if (item["id"], stage_id) not in logged
    ]
    if stage_id == "production-plan" and _has_material_motion(project_dir):
        if ("emil-motion-craft", stage_id) not in logged:
            errors.append("production-plan material motion must log emil-motion-craft with Mode=production-plan")
    path = project_dir / artifact
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if stage_id in {"visual-experience", "design-review", "build-review"} and re.search(
        r"\b(?:GENERIC|FLAT|SAFE|OVERDESIGNED|WEAK_HIERARCHY|INTERCHANGEABLE)\b", text,
    ) and ("impeccable-craft-correction", stage_id) not in logged:
        errors.append(f"{stage_id} classified craft failure must log impeccable-craft-correction with Mode={stage_id}")
    return errors


def gate_capability_errors(project_dir: Path, root: Path, gate_id: str) -> list[str]:
    errors: list[str] = []
    for stage_id in GATE_STAGES.get(gate_id, ()):
        errors.extend(stage_activation_errors(project_dir, root, stage_id))
    return errors
