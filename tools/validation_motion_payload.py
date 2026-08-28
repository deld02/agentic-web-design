#!/usr/bin/env python3
"""Enforce deliberate implemented motion without prescribing a library."""

from pathlib import Path

from validation_common import table_rows
from validation_user_authority import explicit_static_only_authorized


NON_STATIC = {"HOVER", "STICKY", "PARALLAX", "PINNED_SCROLL", "VIDEO_PLAYBACK", "INTERACTIVE_3D"}


def motion_payload_errors(project_dir: Path) -> list[str]:
    project_dir = Path(project_dir)
    if explicit_static_only_authorized(project_dir):
        return []
    plan = project_dir / "production-plan.md"
    if not plan.is_file():
        return ["G4 motion payload cannot be verified without production-plan.md"]
    text = plan.read_text(encoding="utf-8")
    narrative = table_rows(text, "## Page visual narrative map", "Scene ID")
    if not any(len(row) >= 6 and row[5] in NON_STATIC for row in narrative):
        return ["G4 requires at least one selected non-static scene behavior; static-only needs immutable explicit user authority"]
    effects = table_rows(text, "### Material effect decisions", "Effect ID / scene")
    if not any(len(row) >= 11 and row[9] == "FINAL" and row[10] for row in effects):
        return ["G4 requires at least one implemented FINAL motion mechanism; a static winner cannot waive the whole landing"]
    return []
