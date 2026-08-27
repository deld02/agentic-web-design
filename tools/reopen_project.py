#!/usr/bin/env python3
"""Invalidate a causal gate and every downstream gate/checkpoint as owner 00."""

from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import tempfile


ORDER = ("G0", "G1", "G2", "G3", "G4", "G5")
GATE_STAGE = {
    "G0": "definition", "G1": "research-strategy", "G2": "direction-divergence",
    "G3": "visual-experience", "G4": "technology-selection", "G5": "release",
}
GATE_AGENT = {"G0": "00", "G1": "01", "G2": "03", "G3": "04", "G4": "06", "G5": "00"}
GATE_MODE = {
    "G0": "definition", "G1": "research-strategy", "G2": "direction-divergence",
    "G3": "visual-experience", "G4": "technology-selection", "G5": "release",
}
GATE_ENTRY_CHECKPOINT = {"G1": "research-strategy", "G2": "direction-divergence", "G4": "technology-selection"}
CHECKPOINT_GATE = {
    "research-strategy": "G1", "direction-divergence": "G2", "direction-review": "G2",
    "design-review": "G3", "technology-selection": "G4", "production-plan": "G4",
    "build-review": "G4",
}


def reopen(project_dir: Path, gate_id: str, reason: str, owner: str) -> None:
    if owner != "00":
        raise ValueError("only owner 00 may reopen official project state")
    if gate_id not in ORDER:
        raise ValueError(f"unknown gate {gate_id}")
    if len(reason.split()) < 3:
        raise ValueError("reopening requires a concrete causal reason")
    path = project_dir / "status.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    start = ORDER.index(gate_id)
    for current in ORDER[start:]:
        item = data["gates"][current]
        item.update(status="PENDING", evidence=[], blockers=[f"REOPENED_FROM_{gate_id}: {reason}"], last_decision=None)
    for checkpoint, parent in CHECKPOINT_GATE.items():
        if ORDER.index(parent) >= start:
            item = data["checkpoints"][checkpoint]
            item.update(status="PENDING", evidence=[], blockers=[f"REOPENED_FROM_{gate_id}: {reason}"], last_decision=None)
            if "review_context" in item:
                item["review_context"] = "PENDING"
    target = data["gates"][gate_id]
    target.update(blockers=[reason], last_decision=f"00 reopened {gate_id}: {reason}")
    active_checkpoint = GATE_ENTRY_CHECKPOINT.get(gate_id)
    if active_checkpoint:
        data["checkpoints"][active_checkpoint].update(status="ACTIVE", blockers=[reason])
        active_gate = None
    else:
        target["status"] = "ACTIVE"
        active_gate = gate_id
    data.update(
        active_stage=GATE_STAGE[gate_id], active_gate=active_gate, active_agent=GATE_AGENT[gate_id],
        active_mode=GATE_MODE[gate_id], status="ACTIVE",
    )
    data["release"] = {"eligible": False, "reason": f"{gate_id} reopened: {reason}"}
    handle, temporary_name = tempfile.mkstemp(prefix="status-", suffix=".json", dir=project_dir)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Reopen one causal gate and invalidate all downstream approvals.")
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--from-gate", required=True, choices=ORDER)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--owner", required=True, choices=("00",))
    args = parser.parse_args()
    reopen(args.project_dir.resolve(), args.from_gate, args.reason, args.owner)
    print(f"Reopened {args.from_gate}; downstream state invalidated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
