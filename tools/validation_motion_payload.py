#!/usr/bin/env python3
"""Enforce deliberate implemented motion without prescribing a library."""

from pathlib import Path

from validation_common import table_rows
from validation_user_authority import explicit_static_only_authorized


NON_STATIC = {"HOVER", "STICKY", "PARALLAX", "PINNED_SCROLL", "VIDEO_PLAYBACK", "INTERACTIVE_3D"}


def reviewed_static_direction(project_dir: Path) -> bool:
    """Static is a reviewed design choice, never an owner-authored waiver."""
    import json
    import re
    visual = project_dir / 'visual-system.md'
    if not visual.is_file() or not re.search(r'(?m)^MOTION_POLICY:\s*STATIC\s*$', visual.read_text(encoding='utf-8')):
        return False
    try:
        record = json.loads((project_dir / '.reviews/design-review.json').read_text(encoding='utf-8'))
        from harness_review import review_record_errors
        return not review_record_errors(project_dir, 'design-review') and record['result']['axes'].get('motion_value', {}).get('status') == 'PASS'
    except (OSError, ValueError, KeyError, TypeError):
        return False


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
        if reviewed_static_direction(project_dir):
            return []
        return ["G4 static direction requires independent motion_value review or explicit user authority"]
    effects = table_rows(text, "### Material effect decisions", "Effect ID / scene")
    if not any(len(row) >= 11 and row[9] == "FINAL" and row[10] for row in effects):
        return ["G4 requires at least one implemented FINAL motion mechanism; a static winner cannot waive the whole landing"]
    return []
