#!/usr/bin/env python3
"""Validation for the semantic experience progression owned by agent 02."""

from __future__ import annotations

import re
from pathlib import Path

from validation_common import table_rows


FUNCTIONS = {
    "OPENING", "ORIENTATION", "DEMONSTRATION", "CONTRAST", "PROOF",
    "DEEPENING", "REST", "CLIMAX", "RESOLUTION", "ACTION",
}
PLACEHOLDERS = {"", "tbd", "todo", "none", "undetermined", "pending"}


def experience_spine_errors(project_dir: Path) -> list[str]:
    """Require one substantive Experience Spine row for every outlined scene."""
    path = project_dir / "content-architecture.md"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    outline = table_rows(text, "## Sitemap / page or section outline", "Scene ID")
    expected = {
        row[0] for row in outline
        if len(row) >= 5 and re.fullmatch(r"SCN-[0-9]{3,}", row[0])
    }
    rows = table_rows(text, "## Experience spine", "Scene ID")
    errors: list[str] = []
    seen: set[str] = set()
    if not rows:
        return ["G1 requires an Experience Spine for every outlined scene"]
    for row in rows:
        if len(row) < 8 or any(cell.strip().casefold() in PLACEHOLDERS for cell in row[:8]):
            errors.append("G1 Experience Spine contains an incomplete row")
            continue
        scene_id, entry, question, meaning, proof, shift, next_step, function = row[:8]
        if not re.fullmatch(r"SCN-[0-9]{3,}", scene_id):
            errors.append(f"G1 invalid Experience Spine scene ID: {scene_id or '<empty>'}")
            continue
        if scene_id in seen:
            errors.append(f"G1 duplicate Experience Spine scene: {scene_id}")
        seen.add(scene_id)
        if scene_id not in expected:
            errors.append(f"G1 Experience Spine {scene_id} is absent from the scene outline")
        if function not in FUNCTIONS:
            errors.append(f"G1 {scene_id} has invalid narrative function {function}")
        if min(len(entry), len(question), len(meaning), len(proof), len(shift), len(next_step)) < 8:
            errors.append(f"G1 {scene_id} Experience Spine is not project-specific enough")
    for scene_id in sorted(expected - seen):
        errors.append(f"G1 Experience Spine is missing scene {scene_id}")
    return errors
