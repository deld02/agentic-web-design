#!/usr/bin/env python3
"""Conditional enforcement for selected rendered or interactive spatial work."""

from __future__ import annotations

from pathlib import Path
import re

from validation_common import section, table_rows, valid_signature
from validation_release_integrity import implementation_digest


SPATIAL_MODES = {"FLAT_2D", "LAYERED_2D", "RENDERED_3D", "INTERACTIVE_3D"}
PLACEHOLDERS = {"", "TBD", "TODO", "NONE", "N/A", "PENDING", "UNDETERMINED"}


def _text(project_dir: Path, name: str) -> str:
    path = Path(project_dir) / name
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _named_value(text: str, heading: str, name: str) -> str:
    match = re.search(rf"(?mi)^\s*{re.escape(name)}\s*:\s*(.*?)\s*$", section(text, heading))
    return match.group(1).strip().strip("`") if match else ""


def selected_spatial_mode(project_dir: Path) -> str:
    return _named_value(
        _text(project_dir, "visual-system.md"),
        "### Spatial modality decision (conditional)",
        "SPATIAL_MODE",
    )


def _selected_scenes(project_dir: Path) -> set[str]:
    value = _named_value(
        _text(project_dir, "visual-system.md"),
        "### Spatial modality decision (conditional)",
        "SELECTED_SCENE_IDS",
    )
    return set(re.findall(r"SCN-[0-9]{3,}", value))


def _spatial_claims(project_dir: Path) -> set[str]:
    visual = _text(project_dir, "visual-system.md")
    claims: set[str] = set()
    for row in table_rows(visual, "### Scene visual opportunities", "Scene"):
        if len(row) >= 4:
            claims.update(re.findall(r"(?:RENDERED_3D|INTERACTIVE_3D|REAL_3D)", row[3]))
    for row in table_rows(visual, "### Effect opportunity map", "FX ID / scene"):
        if len(row) >= 5:
            claims.update(re.findall(r"(?:RENDERED_3D|INTERACTIVE_3D|REAL_3D)", row[4]))
    return claims


def spatial_selection_errors(project_dir: Path) -> list[str]:
    """G3: select a medium on physical comparison before technology."""
    project_dir = Path(project_dir)
    visual = _text(project_dir, "visual-system.md")
    heading = "### Spatial modality decision (conditional)"
    mode = selected_spatial_mode(project_dir)
    claims = _spatial_claims(project_dir)
    body = section(visual, heading)
    untouched = not mode or "|" in mode or mode.upper() in PLACEHOLDERS
    if not claims and (not body or untouched):
        return []
    errors: list[str] = []
    if mode not in SPATIAL_MODES:
        errors.append("G3 spatial candidate needs one valid SPATIAL_MODE decision")
        return errors
    if "INTERACTIVE_3D" in claims and mode != "INTERACTIVE_3D":
        errors.append("G3 selected INTERACTIVE_3D mechanism conflicts with SPATIAL_MODE")
    if claims.intersection({"REAL_3D", "RENDERED_3D"}) and mode not in {"RENDERED_3D", "INTERACTIVE_3D"}:
        errors.append("G3 selected real-3D production conflicts with SPATIAL_MODE")

    scenes = _selected_scenes(project_dir)
    outline = {
        row[0] for row in table_rows(
            _text(project_dir, "content-architecture.md"),
            "## Sitemap / page or section outline", "Scene ID",
        ) if len(row) >= 5 and re.fullmatch(r"SCN-[0-9]{3,}", row[0])
    }
    if not scenes:
        errors.append("G3 spatial modality needs SELECTED_SCENE_IDS")
    for scene_id in sorted(scenes - outline):
        errors.append(f"G3 spatial modality names unknown scene {scene_id}")
    if len(_named_value(visual, heading, "WHY_SIMPLER_FAILS")) < 12:
        errors.append("G3 spatial modality needs project-specific WHY_SIMPLER_FAILS")

    rows = table_rows(visual, heading, "Candidate mode")
    seen: set[str] = set()
    selected: list[str] = []
    for row in rows:
        if len(row) < 7 or any(cell.strip().upper() in PLACEHOLDERS for cell in row[:7]):
            errors.append("G3 spatial modality comparison contains an incomplete row")
            continue
        candidate, job, gain, necessity, cost, equivalence, verdict = row[:7]
        if candidate not in SPATIAL_MODES:
            errors.append(f"G3 spatial modality has invalid candidate {candidate}")
            continue
        if candidate in seen:
            errors.append(f"G3 spatial modality duplicates candidate {candidate}")
        seen.add(candidate)
        if min(len(job), len(gain), len(necessity), len(cost), len(equivalence)) < 8:
            errors.append(f"G3 spatial candidate {candidate} lacks substantive comparison evidence")
        if verdict == "SELECTED":
            selected.append(candidate)
        elif verdict != "REJECTED":
            errors.append(f"G3 spatial candidate {candidate} has invalid verdict")
    required = {"FLAT_2D", "LAYERED_2D", "RENDERED_3D"}
    if mode == "INTERACTIVE_3D":
        required.add("INTERACTIVE_3D")
    for missing in sorted(required - seen):
        errors.append(f"G3 spatial modality comparison missing {missing}")
    if selected != [mode]:
        errors.append("G3 spatial modality must select exactly the declared SPATIAL_MODE")
    if _named_value(visual, heading, "SPATIAL_REVIEW") != "PASS":
        errors.append("G3 spatial modality needs independent SPATIAL_REVIEW PASS")
    evidence = _named_value(visual, heading, "SPATIAL_REVIEW_EVIDENCE")
    candidate = (project_dir / evidence).resolve() if evidence else project_dir
    if not evidence or not candidate.is_file() or not valid_signature(candidate):
        errors.append("G3 spatial modality needs physical SPATIAL_REVIEW_EVIDENCE")
    return errors


def spatial_technology_errors(project_dir: Path) -> list[str]:
    """Technology: prove one bounded runtime spike for interactive 3D."""
    project_dir = Path(project_dir)
    if selected_spatial_mode(project_dir) != "INTERACTIVE_3D":
        return []
    technology = _text(project_dir, "technology-decision.md")
    heading = "### Spatial runtime decision (conditional)"
    errors: list[str] = []
    for field in (
        "SPATIAL_RUNTIME_SELECTION", "SIMPLEST_SPATIAL_OPTION_TESTED",
        "SPATIAL_SPIKE_EVIDENCE", "SPATIAL_KILL_CRITERION",
    ):
        if _named_value(technology, heading, field).upper() in PLACEHOLDERS:
            errors.append(f"G4 interactive 3D technology missing {field}")
    options = [row for row in table_rows(technology, "## Options compared", "Option") if len(row) >= 4 and all(row[:4])]
    if len(options) < 2:
        errors.append("G4 interactive 3D technology needs two viable architecture options")
    evidence = _named_value(technology, heading, "SPATIAL_SPIKE_EVIDENCE")
    candidate = (project_dir / evidence).resolve() if evidence else project_dir
    if not evidence or not candidate.is_file() or not valid_signature(candidate):
        errors.append("G4 interactive 3D needs physical SPATIAL_SPIKE_EVIDENCE")
    return errors


def _spatial_states(project_dir: Path) -> list[list[str]]:
    return table_rows(
        _text(project_dir, "production-plan.md"),
        "### Spatial experience contract (conditional)", "State ID",
    )


def spatial_plan_errors(project_dir: Path) -> list[str]:
    """Production plan: require semantic states and one bounded resource policy."""
    project_dir = Path(project_dir)
    mode = selected_spatial_mode(project_dir)
    if mode not in {"RENDERED_3D", "INTERACTIVE_3D"}:
        return []
    plan = _text(project_dir, "production-plan.md")
    heading = "### Spatial experience contract (conditional)"
    errors: list[str] = []
    for field in ("ASSET_BUDGET", "RUNTIME_BUDGET", "LOADING_STRATEGY", "LOW_POWER_POLICY", "FAILURE_FALLBACK"):
        if _named_value(plan, heading, field).upper() in PLACEHOLDERS:
            errors.append(f"G4 spatial experience missing {field}")
    selected_scenes = _selected_scenes(project_dir)
    rows = _spatial_states(project_dir)
    if not rows:
        errors.append("G4 selected spatial medium needs at least one SPT-* state")
        return errors
    seen: set[str] = set()
    for row in rows:
        if len(row) < 10 or any(cell.strip().upper() in PLACEHOLDERS for cell in row[:10]):
            errors.append("G4 spatial experience contains an incomplete state")
            continue
        state_id, scene_id, job, trigger, camera, world, html, transition, fallback, evidence = row[:10]
        if not re.fullmatch(r"SPT-[0-9]{3,}", state_id):
            errors.append(f"G4 invalid spatial state ID {state_id or '<empty>'}")
            continue
        if state_id in seen:
            errors.append(f"G4 duplicate spatial state {state_id}")
        seen.add(state_id)
        if scene_id not in selected_scenes:
            errors.append(f"G4 spatial state {state_id} uses unselected scene {scene_id}")
        if min(len(job), len(trigger), len(camera), len(world), len(html), len(transition), len(fallback), len(evidence)) < 8:
            errors.append(f"G4 spatial state {state_id} lacks buildable detail")
    return errors


def spatial_qa_errors(project_dir: Path, implementation_root: Path | None = None) -> list[str]:
    """G4/G5: review the selected medium and every interactive spatial state."""
    project_dir = Path(project_dir)
    mode = selected_spatial_mode(project_dir)
    if mode not in {"RENDERED_3D", "INTERACTIVE_3D"}:
        return []
    qa = _text(project_dir, "qa-release.md")
    errors: list[str] = []
    required = {
        "SPATIAL_DIRECTION_FIDELITY", "HTML_LEGIBILITY", "MATERIAL_LIGHTING_COHERENCE",
        "ASSET_INTEGRITY", "FALLBACK_EQUIVALENCE",
    }
    if mode == "INTERACTIVE_3D":
        required.update({"CAMERA_CONTINUITY", "OBJECT_INTERSECTIONS", "RUNTIME_SMOOTHNESS"})
    seen: set[str] = set()
    for row in table_rows(qa, "### Spatial QA (conditional)", "Axis"):
        if len(row) < 4 or not all(row[:4]):
            errors.append("G4 spatial QA contains an incomplete row")
            continue
        axis, evidence, _finding, verdict = row[:4]
        if axis not in required:
            errors.append(f"G4 spatial QA has unknown axis {axis}")
            continue
        seen.add(axis)
        if len(evidence) < 8:
            errors.append(f"G4 spatial QA {axis} lacks rendered/runtime evidence")
        if verdict != "PASS":
            errors.append(f"G4 spatial QA {axis} is not PASS")
    for axis in sorted(required - seen):
        errors.append(f"G4 spatial QA missing {axis}")
    if mode == "INTERACTIVE_3D":
        errors.extend(_spatial_traversal_errors(project_dir, implementation_root))
    return errors


def _spatial_traversal_errors(project_dir: Path, implementation_root: Path | None) -> list[str]:
    states = {row[0]: row[1] for row in _spatial_states(project_dir) if len(row) >= 2 and re.fullmatch(r"SPT-[0-9]{3,}", row[0])}
    qa = _text(project_dir, "qa-release.md")
    rows = table_rows(qa, "### Spatial state traversal (conditional)", "State ID")
    errors: list[str] = []
    covered: set[tuple[str, str]] = set()
    evidence_paths: set[str] = set()
    digest = implementation_digest(implementation_root) if implementation_root and Path(implementation_root).is_dir() else None
    for row in rows:
        if len(row) < 9 or not all(row[:9]):
            errors.append("G4 spatial state traversal contains an incomplete row")
            continue
        state_id, scene_id, viewport, trigger, expected, observed, evidence, verdict, source_digest = row[:9]
        if state_id not in states or states.get(state_id) != scene_id:
            errors.append(f"G4 spatial traversal has unknown state/scene {state_id}/{scene_id}")
        if viewport not in {"DESKTOP", "MOBILE"}:
            errors.append(f"G4 spatial traversal {state_id} has invalid viewport")
        if min(len(trigger), len(expected), len(observed)) < 8:
            errors.append(f"G4 spatial traversal {state_id}/{viewport} lacks state detail")
        if verdict != "PASS":
            errors.append(f"G4 spatial traversal {state_id}/{viewport} is not PASS")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", source_digest):
            errors.append(f"G4 spatial traversal {state_id}/{viewport} lacks source SHA-256")
        elif digest and source_digest != f"sha256:{digest}":
            errors.append(f"G4 spatial traversal {state_id}/{viewport} is stale")
        candidate = (project_dir / evidence).resolve()
        if not candidate.is_file() or not valid_signature(candidate):
            errors.append(f"G4 spatial traversal evidence is missing or invalid: {evidence}")
        if evidence in evidence_paths:
            errors.append(f"G4 spatial traversal reuses evidence file: {evidence}")
        evidence_paths.add(evidence)
        covered.add((state_id, viewport))
    for state_id in sorted(states):
        for viewport in ("DESKTOP", "MOBILE"):
            if (state_id, viewport) not in covered:
                errors.append(f"G4 spatial traversal missing {state_id}/{viewport}")
    return errors


def spatial_stage_instruction(project_dir: Path, stage_id: str) -> str:
    """Return routing only; the method remains the single source of rules."""
    relevant = {"visual-experience", "design-review", "technology-selection", "production-plan", "implementation", "build-review", "release"}
    if stage_id not in relevant:
        return ""
    mode = selected_spatial_mode(project_dir)
    if stage_id in {"visual-experience", "design-review"}:
        return "Spatial routing: evaluate credible spatial candidates with docs/methods/spatial-experience.md before G3; premium language alone is not a trigger."
    if mode in {"RENDERED_3D", "INTERACTIVE_3D"}:
        return f"Spatial routing: G3 selected {mode}; load docs/methods/spatial-experience.md and complete only this stage's part of its contract."
    return "Spatial routing: no selected real-3D mode; do not introduce a 3D stack or reopen the medium decision."
