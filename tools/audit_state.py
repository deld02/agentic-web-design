#!/usr/bin/env python3
"""Detect project status drift without mutating project state."""

from __future__ import annotations

from pathlib import Path
import argparse
import sys

from project_validation import ROOT, load_json, review_checkpoint_errors


def audit(project_dir: Path) -> list[str]:
    status = load_json(project_dir / "status.json")
    pipeline = load_json(ROOT / "config" / "pipeline.json")
    stages = {item["id"]: item for item in pipeline["stages"]}
    gates = status.get("gates", {})
    checkpoints = status.get("checkpoints", {})
    errors = review_checkpoint_errors(status)
    active = status.get("active_stage")
    stage = stages.get(active)
    if not stage:
        errors.append(f"unknown active_stage {active}")
    else:
        if status.get("active_agent") != stage.get("agent") or status.get("active_gate") != stage.get("gate") or status.get("active_mode") != stage.get("mode"):
            errors.append("active stage metadata does not match pipeline")
        item = gates.get(stage["gate"], {}) if stage.get("gate") else checkpoints.get(active, {})
        if status.get("status") == "ACTIVE" and item.get("status") != "ACTIVE":
            errors.append("active stage does not point to an ACTIVE gate/checkpoint")
    for item in stages.values():
        target = gates.get(item["gate"], {}) if item.get("gate") else checkpoints.get(item["id"], {})
        if target.get("status") not in {"ACTIVE", "REVIEW", "APPROVED"}:
            continue
        for gate_id, allowed in item.get("entry_requires", {}).get("gates", {}).items():
            if gates.get(gate_id, {}).get("status") not in allowed:
                errors.append(f"{item['id']} advanced before {gate_id} satisfied {allowed}")
        for checkpoint_id, allowed in item.get("entry_requires", {}).get("checkpoints", {}).items():
            if checkpoints.get(checkpoint_id, {}).get("status") not in allowed:
                errors.append(f"{item['id']} advanced before {checkpoint_id} satisfied {allowed}")
    eligible = all(gates.get(f"G{i}", {}).get("status") == "APPROVED" for i in range(5))
    if status.get("release", {}).get("eligible") != eligible:
        errors.append("release.eligible has drifted from G0–G4")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir")
    parser.add_argument("--all-projects", action="store_true")
    args = parser.parse_args()
    if args.all_projects:
        projects = sorted(path.parent for path in (ROOT / "projects").glob("*/status.json"))
    elif args.project_dir:
        projects = [Path(args.project_dir).resolve()]
    else:
        raise SystemExit("Provide --project-dir or --all-projects")
    failures: list[str] = []
    for project in projects:
        for error in audit(project):
            failures.append(f"{project.name}: {error}")
    if failures:
        print("STATE AUDIT FAILED")
        for failure in failures:
            print("-", failure)
        return 1
    print("OK — project state is coherent with the pipeline.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

