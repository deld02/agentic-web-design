#!/usr/bin/env python3
"""Parse generated-image targets owned by the production-plan subloop."""

from pathlib import Path
import re

from validation_common import section
from validation_common import load_json, valid_signature
from validation_project_paths import implementation_root_for

IMAGE_TOOLS = {"CHATGPT_GENERATE", "IMAGE_GEN", "IMAGEGEN", "CHATGPT_IMAGE"}


def is_image_generation_event(item: dict) -> bool:
    tool = re.sub(r"[^A-Z0-9]+", "_", str(item.get("tool", "")).upper()).strip("_")
    return item.get("event") == "tool_call" and tool in IMAGE_TOOLS


def generated_asset_targets(project_dir: Path) -> dict[str, str]:
    plan = project_dir / "production-plan.md"
    if not plan.is_file():
        return {}
    targets: dict[str, str] = {}
    body = section(plan.read_text(encoding="utf-8"), "## Asset inventory and readiness")
    for line in body.splitlines():
        if not line.startswith("|") or "---" in line or re.search(r"\|\s*ID\s*\|", line):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if len(cells) < 8 or not re.fullmatch(r"IMG-[0-9]{3,}", cells[0]):
            continue
        asset_id, role_method, status, final_file = cells[0], cells[3], cells[4], cells[5]
        if role_method.endswith(":EXTERNAL_IMAGE_LOOP") and status in {"RETURNED", "FINAL"} and final_file:
            targets[asset_id] = final_file
    return targets


def generated_asset_file_errors(project_dir: Path, repository_root: Path) -> list[str]:
    config = load_json(project_dir / "project.config.json")
    root = implementation_root_for(project_dir, repository_root, config.get("implementation_root", "undetermined"))
    errors: list[str] = []
    for asset_id, reference in generated_asset_targets(project_dir).items():
        asset = (root / reference).resolve()
        try:
            asset.relative_to(root)
        except ValueError:
            errors.append(f"{asset_id} generated file is outside implementation_root")
            continue
        if asset.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".avif"}:
            errors.append(f"{asset_id} generated output must be a raster image")
        elif not asset.is_file() or not valid_signature(asset):
            errors.append(f"{asset_id} generated output is missing or invalid: {reference}")
    return errors


def missing_generation_receipts(project_dir: Path, events: list[dict], image_tools: set[str]) -> list[str]:
    required = set(generated_asset_targets(project_dir))
    recorded = {
        item.get("target") for item in events
        if item.get("event") == "tool_call" and item.get("stage") == "production-plan"
        and re.sub(r"[^A-Z0-9]+", "_", str(item.get("tool", "")).upper()).strip("_") in image_tools
    }
    return sorted(required - recorded)
