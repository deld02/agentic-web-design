#!/usr/bin/env python3
"""Small, dependency-free checks shared by gate and state validators."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
import json
import re

from validation_common import load_json, section, table_rows, valid_signature
from validation_experience import experience_spine_errors
from validation_final_delivery import final_delivery_contract_errors


ROOT = Path(__file__).resolve().parents[1]


def nonempty_section(text: str, heading: str) -> bool:
    body = section(text, heading)
    meaningful = [
        line.strip()
        for line in body.splitlines()
        if line.strip() and not line.lstrip().startswith(("|---", "<!--"))
    ]
    return bool(meaningful)


def markdown(project_dir: Path, name: str) -> str:
    path = project_dir / name
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def claim_errors(project_dir: Path) -> list[str]:
    text = markdown(project_dir, "content-architecture.md")
    rows = table_rows(text, "## Claim ledger", "Claim ID")
    errors: list[str] = []
    seen: set[str] = set()
    for row in rows:
        if len(row) < 6:
            errors.append("G1 claim ledger contains a malformed row")
            continue
        claim_id, claim, kind, status, evidence, _use = row[:6]
        if not re.fullmatch(r"CLM-[0-9]{3,}", claim_id):
            errors.append(f"G1 invalid claim ID: {claim_id or '<empty>'}")
        elif claim_id in seen:
            errors.append(f"G1 duplicate claim ID: {claim_id}")
        seen.add(claim_id)
        if not claim:
            errors.append(f"G1 {claim_id or 'claim'} has no exact wording")
        if kind not in {"QUANTITATIVE", "TESTIMONIAL", "FACTUAL", "POSITIONING"}:
            errors.append(f"G1 {claim_id or 'claim'} has invalid kind")
        if status not in {"DOCUMENTED", "PROVISIONAL", "REMOVE"}:
            errors.append(f"G1 {claim_id or 'claim'} has invalid truth status")
        if status == "DOCUMENTED" and not evidence:
            errors.append(f"G1 {claim_id or 'claim'} is DOCUMENTED without evidence")
        if kind in {"QUANTITATIVE", "TESTIMONIAL", "FACTUAL"} and status == "PROVISIONAL":
            errors.append(f"G1 {claim_id or 'claim'} cannot ship while PROVISIONAL")

    # This is deliberately a forcing function, not an attempt to prove truth by regex.
    suspicious = re.findall(
        r"(?im)^.*(?:\b\d+(?:[.,]\d+)?\s*%|\b\d+\s+(?:clientes?|proyectos?|años?)\b|testimonial|testimonio).*$",
        section(text, "## Content and copy"),
    )
    if suspicious and not rows:
        errors.append("G1 possible quantitative/testimonial claim found but Claim ledger is empty")
    return errors


def technology_freshness_errors(root: Path = ROOT) -> list[str]:
    config = load_json(root / "config" / "technology-options.json")
    raw = config.get("last_revalidated")
    days = config.get("review_by_days")
    if not raw or not isinstance(days, int) or isinstance(days, bool) or days < 30:
        return ["technology options need last_revalidated and review_by_days >= 30"]
    try:
        checked = datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return ["technology options last_revalidated must be YYYY-MM-DD"]
    if date.today() > checked + timedelta(days=days):
        return [f"technology options are stale (last revalidated {raw})"]
    return []


def review_checkpoint_errors(status: dict) -> list[str]:
    errors: list[str] = []
    for checkpoint_id in ("direction-review", "design-review", "build-review"):
        item = status.get("checkpoints", {}).get(checkpoint_id, {})
        isolation = item.get("review_context")
        if isolation not in {"PENDING", "ISOLATED", "EXCEPTION_RECORDED"}:
            errors.append(f"{checkpoint_id} has invalid review_context")
        if item.get("status") == "APPROVED" and isolation != "ISOLATED":
            errors.append(f"{checkpoint_id} APPROVED without ISOLATED review context")
    return errors


def hero_stress_errors(project_dir: Path) -> list[str]:
    text = markdown(project_dir, "visual-system.md")
    rows = table_rows(text, "### Hero experience stress test", "Axis")
    required = {
        "THESIS", "TYPOGRAPHIC_VOICE", "COLOR_PROVENANCE",
        "COLOR_COMPOSITION", "MEDIA_INTEGRATION", "MECHANISM_SALIENCE", "DEPTH_RHYTHM_DETAIL",
        "DIRECTION_FIDELITY",
    }
    found = {row[0] for row in rows if row}
    errors = [f"G3 hero stress test missing axis {axis}" for axis in sorted(required - found)]
    for row in rows:
        if not row or row[0] not in required:
            continue
        if len(row) < 5 or not all(row[index] for index in (1, 2, 3)):
            errors.append(f"G3 hero stress axis {row[0]} lacks observable/countertest/render evidence")
        if len(row) < 5 or row[4] != "PASS":
            errors.append(f"G3 hero stress axis {row[0]} is not PASS")
    return errors


SCENE_PRODUCTION_MODES = {
    "CSS_NATIVE", "EXISTING_MEDIA", "EXTERNAL_IMAGE_LOOP", "CUSTOM_ILLUSTRATION",
    "VIDEO_RENDER", "3D", "HYBRID",
}
COMPOSITION_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".avif"}
WEB_IMAGE_OUTPUT_TYPES = {
    "SCENE_PLATE", "TRANSPARENT_ELEMENT", "TEXTURE", "DEPTH_LAYERS",
    "SECTION_ARTWORK", "MASK_OR_SHAPE", "MOTION_FRAMES", "DOCUMENTARY_MEDIA",
}


def _physical_composition_error(project_dir: Path, reference: str, label: str) -> str | None:
    candidate = Path(reference.strip().strip("`"))
    path = candidate.resolve() if candidate.is_absolute() else (project_dir / candidate).resolve()
    try:
        path.relative_to(project_dir.resolve())
    except ValueError:
        return f"{label} composition must be inside project evidence: {reference}"
    if path.suffix.lower() not in COMPOSITION_SUFFIXES:
        return f"{label} composition must use a supported raster format: {reference}"
    if not path.is_file() or not valid_signature(path):
        return f"{label} composition evidence is missing or invalid: {reference}"
    return None


def reference_benchmark_errors(project_dir: Path, minimum: int = 5) -> list[str]:
    """Require a current, balanced visual calibration against real inspected websites."""
    rows = table_rows(
        markdown(project_dir, "research-strategy.md"),
        "### Live website benchmark", "Website",
    )
    errors: list[str] = []
    valid = 0
    roles: set[str] = set()
    for index, row in enumerate(rows, start=1):
        if len(row) < 9 or not all(row[:9]):
            errors.append(f"G1 reference benchmark row {index} is incomplete")
            continue
        website, role, discovery, observation, fit, decision, source, checked_raw, capture = row[:9]
        if role not in {"DIRECT", "ADJACENT", "FRONTIER", "SIMPLE", "SATURATED"}:
            errors.append(f"G1 reference benchmark {website} has invalid role {role}")
            continue
        if not re.search(r"https?://\S+", source):
            errors.append(f"G1 reference benchmark {website} lacks an original URL")
            continue
        try:
            checked = datetime.strptime(checked_raw, "%Y-%m-%d").date()
        except ValueError:
            errors.append(f"G1 reference benchmark {website} has invalid checked date")
            continue
        age = (date.today() - checked).days
        if age < 0 or age > 30:
            errors.append(f"G1 reference benchmark {website} is stale; inspect it again")
            continue
        physical_error = _physical_composition_error(
            project_dir, capture, f"G1 reference benchmark {website}"
        )
        if physical_error:
            errors.append(physical_error)
            continue
        valid += 1
        roles.add(role)
    if valid < minimum:
        errors.append(f"G1 requires {minimum} current website references with physical captures")
    for role, label in (("DIRECT", "direct category"), ("ADJACENT", "adjacent"),
                        ("FRONTIER", "current frontier"), ("SIMPLE", "strong simple"),
                        ("SATURATED", "saturated-code")):
        if roles and role not in roles:
            errors.append(f"G1 visual calibration lacks a {label} reference")
    return errors


CONTEXT_FIELDS = (
    "BUSINESS_MODEL", "PRIMARY_ACTION", "AUDIENCE_SOPHISTICATION", "TRUST_REQUIREMENT",
    "HUMAN_PRESENCE", "AUTHORITY_WARMTH_BALANCE", "TECHNICALITY",
    "EXPERIMENTAL_TOLERANCE", "LOCALITY", "PROOF_DENSITY", "NARRATIVE_COMPLEXITY",
    "EMOTIONAL_TARGET", "MOBILE_IMPORTANCE",
)


def context_compiler_errors(project_dir: Path) -> list[str]:
    text = markdown(project_dir, "research-strategy.md")
    errors: list[str] = []
    for name in CONTEXT_FIELDS:
        value = _named_value(text, "## Context compiler", name)
        if not value or value.casefold() in {"tbd", "todo", "undetermined", "unknown"}:
            errors.append(f"G1 context compiler missing {name}")
    status = _named_value(text, "## Design memory comparison", "MEMORY_STATUS")
    prior_projects: set[str] = set()
    for candidate in project_dir.parent.glob("*"):
        if candidate.resolve() == project_dir.resolve() or not candidate.is_dir():
            continue
        status_path = candidate / "status.json"
        if not status_path.is_file():
            continue
        try:
            candidate_status = load_json(status_path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if candidate_status.get("gates", {}).get("G5", {}).get("status") == "APPROVED" \
                and not design_fingerprint_errors(candidate):
            prior_projects.add(candidate.name)
    if status not in {"NO_PRIOR_PROJECTS", "COMPARED"}:
        errors.append("G1 design memory has invalid MEMORY_STATUS")
    elif status == "NO_PRIOR_PROJECTS" and prior_projects:
        errors.append("G1 design memory must compare available completed project fingerprints")
    if status == "COMPARED":
        for name in ("NEAREST_PROJECT", "OVERLAP", "JUSTIFICATION_OR_DEPARTURE"):
            if not _named_value(text, "## Design memory comparison", name):
                errors.append(f"G1 design memory comparison missing {name}")
        nearest = _named_value(text, "## Design memory comparison", "NEAREST_PROJECT")
        if prior_projects and nearest not in prior_projects:
            errors.append("G1 design memory NEAREST_PROJECT is not an available completed fingerprint")
    return errors


def scene_outline(project_dir: Path) -> tuple[set[str], list[str]]:
    """Return the primary scene IDs defined by content architecture."""
    rows = table_rows(
        markdown(project_dir, "content-architecture.md"),
        "## Sitemap / page or section outline", "Scene ID",
    )
    errors: list[str] = []
    primary: set[str] = set()
    seen: set[str] = set()
    if not rows:
        return primary, ["G1 content architecture requires a scene outline"]
    for row in rows:
        if len(row) < 5 or not all(row[:5]):
            errors.append("G1 scene outline contains an incomplete row")
            continue
        scene_id, section_name, job, content, importance = row[:5]
        if not re.fullmatch(r"SCN-[0-9]{3,}", scene_id):
            errors.append(f"G1 invalid scene ID: {scene_id or '<empty>'}")
            continue
        if scene_id in seen:
            errors.append(f"G1 duplicate scene ID: {scene_id}")
        seen.add(scene_id)
        if importance not in {"PRIMARY", "UTILITY"}:
            errors.append(f"G1 {scene_id} has invalid scene importance")
        elif importance == "PRIMARY":
            primary.add(scene_id)
    if not primary:
        errors.append("G1 scene outline requires at least one PRIMARY scene")
    return primary, errors


def structure_challenge_errors(project_dir: Path) -> list[str]:
    text = markdown(project_dir, "content-architecture.md")
    heading = "## Structural interchangeability challenge"
    fields = (
        "TEMPLATE_FINGERPRINT", "PREDICTABLE_SEQUENCE_REMOVED", "SCENE_RHYTHM_DIFFERENCE",
        "HERO_CLICHE_CHALLENGE", "FINAL_NON_INTERCHANGEABILITY",
    )
    errors: list[str] = []
    alternatives_pos = text.find("## Narrative alternatives and decision evidence")
    challenge_pos = text.find(heading)
    outline_pos = text.find("## Sitemap / page or section outline")
    if min(alternatives_pos, challenge_pos, outline_pos) < 0 or not alternatives_pos < challenge_pos < outline_pos:
        errors.append("G1 structural challenge must occur after alternatives and before scene outline")
    for name in fields:
        value = _named_value(text, heading, name)
        if not value or value.casefold() in {"tbd", "todo", "none", "undetermined"}:
            errors.append(f"G1 structural challenge missing {name}")
    return errors


def scene_strategy_errors(project_dir: Path) -> list[str]:
    """Require every section to pass the high-value challenge before foundations."""
    _primary, errors = scene_outline(project_dir)
    outline_rows = table_rows(
        markdown(project_dir, "content-architecture.md"),
        "## Sitemap / page or section outline", "Scene ID",
    )
    expected = {
        row[0] for row in outline_rows
        if len(row) >= 5 and re.fullmatch(r"SCN-[0-9]{3,}", row[0])
    }
    text = markdown(project_dir, "visual-system.md")
    strategy_pos = text.find("## Scene strategy")
    foundations_pos = text.find("## Foundation alternatives and decision evidence")
    if strategy_pos < 0 or foundations_pos < 0 or strategy_pos > foundations_pos:
        errors.append("G3 Scene Strategy must appear before foundation selection")
    rows = table_rows(text, "## Scene strategy", "Scene ID")
    seen: set[str] = set()
    for row in rows:
        if len(row) < 8 or not all(row[:8]):
            errors.append("G3 Scene Strategy contains an incomplete row")
            continue
        scene_id, job_content, perceptual, baseline, opportunity, value_test, selected, master = row[:8]
        if not re.fullmatch(r"SCN-[0-9]{3,}", scene_id):
            errors.append(f"G3 invalid Scene Strategy ID: {scene_id or '<empty>'}")
            continue
        if scene_id in seen:
            errors.append(f"G3 duplicate Scene Strategy ID: {scene_id}")
        seen.add(scene_id)
        if scene_id not in expected:
            errors.append(f"G3 Scene Strategy {scene_id} is absent from G1 outline")
        if baseline.strip().casefold() == opportunity.strip().casefold():
            errors.append(f"G3 {scene_id} baseline and high-end opportunity are not distinct")
        for name in ("HIGH_VALUE", "SIMPLIFY", "EXPENSIVE_NOISE"):
            match = re.search(rf"(?i)(?:^|;)\s*{name}\s*=\s*([^;]+)", value_test)
            if not match or match.group(1).strip().lower() in {"", "tbd", "todo", "undetermined"}:
                errors.append(f"G3 {scene_id} value test missing {name}")
    for scene_id in sorted(expected - seen):
        errors.append(f"G3 missing Scene Strategy for scene {scene_id}")
    return errors


def scene_color_map_errors(project_dir: Path) -> list[str]:
    """Require an explicit usable color assignment for every outlined scene."""
    outline_rows = table_rows(
        markdown(project_dir, "content-architecture.md"),
        "## Sitemap / page or section outline", "Scene ID",
    )
    expected = {
        row[0] for row in outline_rows
        if len(row) >= 5 and re.fullmatch(r"SCN-[0-9]{3,}", row[0])
    }
    text = markdown(project_dir, "visual-system.md")
    rows = table_rows(text, "### Scene color map", "Scene ID")
    errors: list[str] = []
    seen: set[str] = set()
    if not rows:
        return ["G3 requires a color assignment for every scene"]

    color_pos = text.find("### Color direction territories")
    modes_pos = text.find("### Color primitives and semantic modes")
    map_pos = text.find("### Scene color map")
    if min(color_pos, modes_pos, map_pos) < 0 or not color_pos < modes_pos < map_pos:
        errors.append("G3 scene colors must be assigned after color direction and semantic modes")

    for row in rows:
        if len(row) < 7 or not all(row[:7]):
            errors.append("G3 Scene color map contains an incomplete row")
            continue
        scene_id, job, mode, roles, transition, continuity, contrast = row[:7]
        if not re.fullmatch(r"SCN-[0-9]{3,}", scene_id):
            errors.append(f"G3 invalid scene color ID: {scene_id or '<empty>'}")
            continue
        if scene_id in seen:
            errors.append(f"G3 duplicate scene color assignment: {scene_id}")
        seen.add(scene_id)
        if scene_id not in expected:
            errors.append(f"G3 scene color assignment {scene_id} is absent from G1 outline")

        for role in ("background", "foreground", "accent", "surface"):
            match = re.search(rf"(?i)(?:^|;)\s*{role}\s*=\s*([^;]+)", roles)
            if not match or match.group(1).strip().lower() in {"", "tbd", "todo", "none", "undetermined"}:
                errors.append(f"G3 {scene_id} color roles missing concrete {role} assignment")
        for boundary in ("IN", "OUT"):
            match = re.search(rf"(?i)(?:^|;)\s*{boundary}\s*=\s*([^;]+)", transition)
            if not match or match.group(1).strip().lower() in {"", "tbd", "todo", "undetermined"}:
                errors.append(f"G3 {scene_id} color transition missing {boundary}")

    for scene_id in sorted(expected - seen):
        errors.append(f"G3 missing color assignment for scene {scene_id}")
    return errors


def page_rhythm_errors(project_dir: Path) -> list[str]:
    text = markdown(project_dir, "visual-system.md")
    heading = "## Global page rhythm"
    errors: list[str] = []
    for name in ("RHYTHM_SEQUENCE", "PEAKS_AND_RESTS", "REPETITION_CONTROL", "HERO_TO_BODY_CONTINUITY"):
        if not _named_value(text, heading, name):
            errors.append(f"G3 global page rhythm missing {name}")
    return errors


MASTER_FIELDS = (
    "SOURCE_DIRECTION", "VISUAL_THESIS", "INVARIANTS", "FLEX", "CONTEXTUAL",
    "SCENE_GRAMMAR", "SIGNATURE_MECHANISM", "ANTI_RULES", "DECOMPOSITION_RISKS",
)
MASTER_INVARIANTS = {"TYPE", "COLOR", "COMPOSITION", "MEDIA", "SPACE", "DEPTH", "MOTION"}
GRAMMAR_RELATIONS = {"DOMINANT", "COUNTERPOINT", "TENSION", "SIGNAL", "REST", "TRANSITION"}
CONFIRMATION_CLOSED = {"APPROVED", "DELEGATED"}


def _named_value(text: str, heading: str, name: str) -> str:
    body = section(text, heading)
    match = re.search(rf"(?m)^[ \t]*{re.escape(name)}:[ \t]*(.+?)[ \t]*$", body)
    return match.group(1).strip() if match else ""


def project_quality_bar_errors(project_dir: Path) -> list[str]:
    """Require a project-grounded quality threshold before image generation."""
    text = markdown(project_dir, "creative-direction.md")
    heading = "## Project-specific quality bar"
    fields = (
        "PREMIUM_MEANS_HERE", "CATEGORY_BASELINE_TO_EXCEED", "MUST_BE_AUTHORED",
        "MUST_AVOID", "MASTER_MUST_PROVE", "LANDING_MUST_PRESERVE",
    )
    errors: list[str] = []
    bar_pos = text.find(heading)
    master_pos = text.find("## Artistic master")
    if bar_pos < 0 or master_pos < 0 or bar_pos > master_pos:
        errors.append("G2 project-specific quality bar must appear before the artistic master")
    generic = {
        "premium", "modern", "beautiful", "clean", "impactful", "elegant",
        "moderno", "bonito", "limpio", "impactante", "elegante",
    }
    for name in fields:
        value = _named_value(text, heading, name)
        if not value:
            errors.append(f"G2 project-specific quality bar missing {name}")
            continue
        tokens = set(re.findall(r"[a-záéíóúñ]+", value.casefold()))
        if tokens and tokens.issubset(generic):
            errors.append(f"G2 {name} is only a generic quality label")
    return errors


def direction_divergence_errors(project_dir: Path) -> list[str]:
    """Require three physically evidenced and structurally distant territories."""
    text = markdown(project_dir, "creative-direction.md")
    rows = table_rows(text, "## Direction divergence", "Direction ID")
    errors: list[str] = []
    if len(rows) != 3:
        errors.append("G2 requires exactly three divergent direction territories")
    valid_rows: list[list[str]] = []
    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    for row in rows:
        if len(row) < 8 or not all(row[:8]):
            errors.append("G2 direction divergence contains an incomplete territory")
            continue
        direction_id = row[0]
        if not re.fullmatch(r"DIR-[0-9]{3,}", direction_id):
            errors.append(f"G2 invalid direction ID: {direction_id or '<empty>'}")
        if direction_id in seen_ids:
            errors.append(f"G2 duplicate direction ID: {direction_id}")
        seen_ids.add(direction_id)
        if row[7] in seen_files:
            errors.append("G2 divergent territories cannot reuse the same physical board")
        seen_files.add(row[7])
        physical_error = _physical_composition_error(project_dir, row[7], f"G2 direction {direction_id}")
        if physical_error:
            errors.append(physical_error)
        valid_rows.append(row)
    for left_index in range(len(valid_rows)):
        for right_index in range(left_index + 1, len(valid_rows)):
            left, right = valid_rows[left_index], valid_rows[right_index]
            differences = sum(
                left[index].strip().casefold() != right[index].strip().casefold()
                for index in range(1, 7)
            )
            if differences < 4:
                errors.append(
                    f"G2 directions {left[0]} and {right[0]} differ in only {differences} dimensions; four are required"
                )
    selected = _named_value(text, "## Direction selection handoff", "SELECTED_DIRECTION")
    if selected not in seen_ids:
        errors.append("G2 selected direction must match one divergent territory")
    if _named_value(text, "## Direction selection handoff", "DIRECTION_REVIEW_CHECKPOINT") != "direction-review":
        errors.append("G2 direction selection must come from direction-review")
    for name in ("SELECTION_EVIDENCE", "REJECTED_DIFFERENCE"):
        if not _named_value(text, "## Direction selection handoff", name):
            errors.append(f"G2 direction selection missing {name}")
    return errors


def creative_master_confirmation_errors(project_dir: Path) -> list[str]:
    """Validate the single user-facing artistic-master checkpoint inside G2."""
    text = markdown(project_dir, "creative-direction.md")
    heading = "## Artistic master confirmation"
    status = _named_value(text, heading, "STATUS")
    if status not in CONFIRMATION_CLOSED:
        if status in {"PENDING", "ADJUST"}:
            return [f"G2 artistic master confirmation is {status}"]
        return ["G2 artistic master confirmation has invalid STATUS"]
    errors: list[str] = []
    master = _named_value(text, "## Artistic master", "ARTISTIC_MASTER")
    if _named_value(text, heading, "PRESENTED_MASTER") != master:
        errors.append("G2 confirmation must present the artistic master")
    if not _named_value(text, heading, "USER_SIGNAL"):
        errors.append("G2 artistic master confirmation missing USER_SIGNAL")
    return errors


def artistic_master_errors(project_dir: Path) -> list[str]:
    """Require one generated, research-grounded styleframe before webpage design."""
    text = markdown(project_dir, "creative-direction.md")
    heading = "## Artistic master"
    artistic_id = _named_value(text, heading, "ARTISTIC_MASTER")
    errors: list[str] = []
    if not re.fullmatch(r"AM-[0-9]{3,}", artistic_id):
        errors.append("G2 requires ARTISTIC_MASTER: AM-###")
    selected = _named_value(text, "## Direction selection handoff", "SELECTED_DIRECTION")
    source = _named_value(text, heading, "SOURCE_DIRECTION")
    if source != selected:
        errors.append("G2 artistic master SOURCE_DIRECTION must match the reviewed direction")
    for name in ("ARTISTIC_INTENT", "PROJECT_GROUNDS", "WEB_TRANSLATION_BOUNDARY"):
        if not _named_value(text, heading, name):
            errors.append(f"G2 artistic master missing {name}")
    rows = table_rows(text, heading, "Evidence ID")
    if len(rows) != 1:
        errors.append("G2 requires exactly one artistic master evidence row")
    matching = [row for row in rows if len(row) >= 4 and row[0] == artistic_id]
    if artistic_id and len(matching) != 1:
        errors.append(f"G2 artistic master {artistic_id} must match exactly one evidence row")
    elif matching:
        row = matching[0]
        if not all(row[:4]):
            errors.append(f"G2 artistic master {artistic_id} evidence is incomplete")
        if row[2] != "CHATGPT_GENERATE":
            errors.append(
                f"G2 artistic master {artistic_id} must use CHATGPT_GENERATE; "
                "a webpage/UI screenshot is not an artistic master"
            )
        physical_error = _physical_composition_error(project_dir, row[3], f"G2 artistic master {artistic_id}")
        if physical_error:
            errors.append(physical_error)
    return errors


def structural_build_errors(project_dir: Path) -> list[str]:
    """Require the structural implementation and renders owned by technology-selection."""
    technology = markdown(project_dir, "technology-decision.md")
    heading = "## Structural build handoff"
    errors: list[str] = []
    if _named_value(technology, heading, "STRUCTURAL_BUILD_STATUS") != "READY":
        errors.append("technology-selection requires STRUCTURAL_BUILD_STATUS: READY")
    implementation_root = _named_value(technology, heading, "IMPLEMENTATION_ROOT")
    if not implementation_root:
        errors.append("technology-selection structural build is missing IMPLEMENTATION_ROOT")
    else:
        config_path = project_dir / "project.config.json"
        configured = load_json(config_path).get("implementation_root") if config_path.is_file() else ""
        if implementation_root != configured:
            errors.append("technology-selection structural IMPLEMENTATION_ROOT does not match project.config.json")
        root = Path(implementation_root)
        root = root.resolve() if root.is_absolute() else (ROOT / root).resolve()
        if not root.is_dir():
            errors.append("technology-selection structural implementation root does not exist")
        elif not any(
            path.is_file() and path.suffix.lower() in {".html", ".css", ".js", ".ts", ".tsx", ".jsx", ".astro", ".vue", ".svelte"}
            for path in root.rglob("*")
        ):
            errors.append("technology-selection structural build has no implementation source")
    for viewport in ("DESKTOP", "MOBILE"):
        reference = _named_value(technology, heading, f"STRUCTURAL_RENDER_{viewport}")
        if not reference:
            errors.append(f"technology-selection requires STRUCTURAL_RENDER_{viewport}")
            continue
        physical_error = _physical_composition_error(
            project_dir, reference, f"technology-selection structural {viewport.lower()} render"
        )
        if physical_error:
            errors.append(physical_error)
    return errors


def final_render_errors(project_dir: Path) -> list[str]:
    """Require the independent build review to receive real final desktop/mobile renders."""
    qa = markdown(project_dir, "qa-release.md")
    heading = "## Visual and responsive verification"
    errors: list[str] = []
    for viewport in ("DESKTOP", "MOBILE"):
        reference = _named_value(qa, heading, f"FINAL_RENDER_{viewport}")
        if not reference:
            errors.append(f"G4 requires FINAL_RENDER_{viewport}")
            continue
        physical_error = _physical_composition_error(
            project_dir, reference, f"G4 final {viewport.lower()} render"
        )
        if physical_error:
            errors.append(physical_error)
    return errors


def visual_narrative_review_errors(project_dir: Path) -> list[str]:
    """Require independent whole-page media/effect review on final renders."""
    qa = markdown(project_dir, "qa-release.md")
    rows = table_rows(qa, "### Visual narrative verification", "Axis")
    required = {
        "WHOLE_PAGE_RHYTHM", "HERO_TARGET_FIDELITY", "EXPERIENCE_CONTINUITY", "ASSET_NECESSITY", "FORMAT_FIT", "FOCAL_VISUAL_AUTHORITY",
        "MECHANISM_ELIGIBILITY", "TRANSITION_CONTINUITY", "MOBILE_FALLBACK", "TEXT_SPACING_CRAFT",
    }
    seen: set[str] = set()
    errors: list[str] = []
    if _named_value(qa, "## Visual and responsive verification", "FINAL_TEXT_SPACING_CAPABILITY") != "jakub-interface-polish":
        errors.append("G4 final text-spacing review must use jakub-interface-polish")
    if _named_value(qa, "## Visual and responsive verification", "FINAL_TEXT_SPACING_MODE") != "FULL":
        errors.append("G4 final text-spacing review must run in FULL mode")
    for row in rows:
        if len(row) < 4 or not all(row[:4]):
            errors.append("G4 visual narrative review contains an incomplete row")
            continue
        axis, evidence, _finding, verdict = row[:4]
        if axis not in required:
            errors.append(f"G4 visual narrative review has unknown axis {axis}")
            continue
        seen.add(axis)
        if verdict != "PASS":
            errors.append(f"G4 visual narrative review {axis} is not PASS")
        if len(evidence.strip()) < 8:
            errors.append(f"G4 visual narrative review {axis} lacks rendered evidence")
        if axis == "TEXT_SPACING_CRAFT" and not all(token in evidence.upper() for token in ("DESKTOP", "MOBILE", "SCN-")):
            errors.append("G4 TEXT_SPACING_CRAFT evidence must name SCN-* locations and desktop/mobile renders")
        if axis == "HERO_TARGET_FIDELITY" and not all(token in evidence.upper() for token in ("CMP-", "DESKTOP", "MOBILE")):
            errors.append("G4 HERO_TARGET_FIDELITY must compare the approved CMP-* with final desktop and mobile renders")
        if axis == "FOCAL_VISUAL_AUTHORITY" and not all(token in evidence.upper() for token in ("SCN-", "DESKTOP", "MOBILE", "REMOV", "PRODUC")):
            errors.append("G4 FOCAL_VISUAL_AUTHORITY must name SCN-* and compare removal with a produced alternative in desktop/mobile renders")
    for axis in sorted(required - seen):
        errors.append(f"G4 visual narrative review missing {axis}")
    return errors


def visual_narrative_errors(project_dir: Path) -> list[str]:
    """Require a page-level visual rhythm before counting or briefing assets."""
    production = markdown(project_dir, "production-plan.md")
    errors: list[str] = []
    heading = "## Page visual narrative map"
    for field in ("ASSET_SET_RATIONALE", "FLAT_STRETCH_CHECK", "DUPLICATE_JOB_CHECK"):
        if not _named_value(production, heading, field):
            errors.append(f"G4 visual narrative missing {field}")
    outline_rows = table_rows(
        markdown(project_dir, "content-architecture.md"),
        "## Sitemap / page or section outline", "Scene ID",
    )
    expected = {
        row[0] for row in outline_rows
        if len(row) >= 5 and re.fullmatch(r"SCN-[0-9]{3,}", row[0])
    }
    rows = table_rows(production, heading, "Scene ID")
    beats = {"ANCHOR", "PROOF", "SUPPORT", "ATMOSPHERE", "TRANSITION", "REST", "CLIMAX", "CLOSURE"}
    formats = {"NONE", "BACKGROUND", "LATERAL", "INLINE", "FOREGROUND", "TEXTURE", "FULL_BLEED", "TRANSPARENT_OBJECT", "SEQUENCE", "VIDEO", "REAL_3D"}
    behaviors = {"STATIC", "HOVER", "STICKY", "PARALLAX", "PINNED_SCROLL", "VIDEO_PLAYBACK", "INTERACTIVE_3D"}
    seen: set[str] = set()
    selected_beats: set[str] = set()
    for row in rows:
        if len(row) < 10 or not all(row[:10]):
            errors.append("G4 page visual narrative contains a malformed row")
            continue
        scene_id, beat, _job, _intensity, selected_format, behavior, trigger, decomposition, fallback, _transition = row[:10]
        if scene_id not in expected:
            errors.append(f"G4 visual narrative has unknown scene {scene_id}")
            continue
        if scene_id in seen:
            errors.append(f"G4 duplicate visual narrative row for {scene_id}")
        seen.add(scene_id)
        selected_beats.add(beat)
        if beat not in beats:
            errors.append(f"G4 {scene_id} has invalid page beat {beat}")
        if selected_format not in formats:
            errors.append(f"G4 {scene_id} has invalid visual format {selected_format}")
        if behavior not in behaviors:
            errors.append(f"G4 {scene_id} has invalid visual behavior {behavior}")
            continue
        if selected_format == "NONE" and behavior != "STATIC":
            errors.append(f"G4 {scene_id} NONE format must use STATIC behavior")
        if behavior != "STATIC" and fallback.upper() in {"NONE", "N/A", "TBD"}:
            errors.append(f"G4 {scene_id} {behavior} needs a mobile/reduced-motion fallback")
        if behavior == "PARALLAX" and not re.search(r"(?i)\b(?:depth[- ]?)?layers?\b", decomposition):
            errors.append(f"G4 {scene_id} PARALLAX requires independent depth layers")
        if behavior in {"STICKY", "PINNED_SCROLL"} and selected_format in {"NONE", "TEXTURE"}:
            errors.append(f"G4 {scene_id} {behavior} needs a narrative visual, not {selected_format}")
        if behavior == "HOVER" and selected_format in {"NONE", "BACKGROUND", "TEXTURE", "FULL_BLEED"}:
            errors.append(f"G4 {scene_id} HOVER needs an interactive or explorable target")
        if behavior == "VIDEO_PLAYBACK" and selected_format not in {"VIDEO", "SEQUENCE"}:
            errors.append(f"G4 {scene_id} VIDEO_PLAYBACK requires VIDEO or SEQUENCE format")
        if behavior == "INTERACTIVE_3D" and selected_format != "REAL_3D":
            errors.append(f"G4 {scene_id} INTERACTIVE_3D requires REAL_3D format")
        if behavior != "STATIC" and len(trigger.strip()) < 12:
            errors.append(f"G4 {scene_id} {behavior} lacks a substantive narrative trigger")
    for scene_id in sorted(expected - seen):
        errors.append(f"G4 missing page visual narrative for scene {scene_id}")
    if expected and not selected_beats.intersection({"ANCHOR", "CLIMAX"}):
        errors.append("G4 visual narrative needs at least one ANCHOR or CLIMAX")
    if len(expected) >= 4 and "REST" not in selected_beats:
        errors.append("G4 visual narrative with four or more scenes needs a deliberate REST")
    return errors


def image_handoff_errors(project_dir: Path) -> list[str]:
    """Require per-scene image decisions and complete external-loop handoffs."""
    production = markdown(project_dir, "production-plan.md")
    heading = "## Asset inventory and readiness"
    diagnosis_heading = "## Render diagnosis and external handoff"
    errors = structural_build_errors(project_dir)
    errors.extend(visual_narrative_errors(project_dir))
    if not _named_value(production, diagnosis_heading, "VISUAL_DIAGNOSIS"):
        errors.append("G4 image decisions require a render-based VISUAL_DIAGNOSIS")

    outline_rows = table_rows(
        markdown(project_dir, "content-architecture.md"),
        "## Sitemap / page or section outline", "Scene ID",
    )
    expected = {
        row[0] for row in outline_rows
        if len(row) >= 5 and re.fullmatch(r"SCN-[0-9]{3,}", row[0])
    }
    decision_rows = table_rows(production, "## Scene image decisions", "Scene ID")
    decisions: dict[str, tuple[str, str]] = {}
    for row in decision_rows:
        if len(row) < 7 or not all(row[:7]):
            errors.append("G4 scene image decisions contain a malformed row")
            continue
        scene_id, decision, role, representation, truth, placement, route = row[:7]
        if scene_id not in expected:
            errors.append(f"G4 image decision has unknown scene {scene_id}")
            continue
        if scene_id in decisions:
            errors.append(f"G4 duplicate image decision for {scene_id}")
        decisions[scene_id] = (decision, route)
        if decision == "IMAGE":
            if role not in {"BACKGROUND", "LATERAL", "INLINE", "FOREGROUND", "ICON", "TEXTURE", "TRANSITION"}:
                errors.append(f"G4 {scene_id} IMAGE has invalid role")
            if route != "EXISTING" and not re.fullmatch(r"EXTERNAL:IH-[0-9]{3,}", route):
                errors.append(f"G4 {scene_id} IMAGE needs EXISTING or EXTERNAL:IH-### route")
        elif decision == "NO_IMAGE":
            if role != "NONE" or route != "NONE":
                errors.append(f"G4 {scene_id} NO_IMAGE must use role and route NONE")
        else:
            errors.append(f"G4 {scene_id} image decision must be IMAGE or NO_IMAGE")
    for scene_id in sorted(expected - set(decisions)):
        errors.append(f"G4 missing image decision for scene {scene_id}")

    rows = table_rows(
        production, heading, "ID"
    )
    handoffs: set[tuple[str, str]] = set()
    for row in rows:
        if len(row) < 8:
            errors.append("G4 image handoff map contains a malformed row")
            continue
        asset_id, scene, production_type, role_method, status, final_file, handoff, integration = row[:8]
        if not re.fullmatch(r"IMG-[0-9]{3,}", asset_id):
            continue
        if not scene:
            errors.append(f"G4 image {asset_id} is missing its scene and observed render need")
        selected_type = production_type.split()[0].strip("`:/") if production_type else ""
        if selected_type not in WEB_IMAGE_OUTPUT_TYPES:
            errors.append(f"G4 image {asset_id} has no valid web-ready production type")
        if status != "FINAL" or not final_file:
            errors.append(f"G4 image {asset_id} must be FINAL with a returned or existing real file")
        if not integration:
            errors.append(f"G4 image {asset_id} is missing exact landing integration")
        external = role_method in {"PRIMARY:EXTERNAL_IMAGE_LOOP", "SUPPORTING:EXTERNAL_IMAGE_LOOP"}
        if external:
            match = re.search(r"\b(IH-[0-9]{3,})\b", handoff)
            scene_match = re.search(r"\b(SCN-[0-9]{3,})\b", scene)
            if not match:
                errors.append(f"G4 external image {asset_id} is missing IH-* handoff and production brief")
            elif scene_match:
                handoffs.add((scene_match.group(0), match.group(1)))
        elif not handoff:
            errors.append(f"G4 existing image {asset_id} is missing source/readiness evidence")
    for scene_id, (decision, route) in decisions.items():
        if decision == "IMAGE" and route.startswith("EXTERNAL:"):
            handoff_id = route.split(":", 1)[1]
            if (scene_id, handoff_id) not in handoffs:
                errors.append(f"G4 {scene_id} external route {handoff_id} has no matching returned IMG row")
    return errors


def creative_master_errors(project_dir: Path) -> list[str]:
    """Validate that the confirmed G2 artistic master has binding design authority."""
    text = markdown(project_dir, "creative-direction.md")
    rows = table_rows(text, "## Artistic master", "Evidence ID")
    errors: list[str] = []
    heading = "## Creative master handoff"
    master = _named_value(text, heading, "CREATIVE_MASTER")
    if not re.fullmatch(r"AM-[0-9]{3,}", master):
        errors.append("G2 creative master handoff needs CREATIVE_MASTER: AM-###")
    for name in MASTER_FIELDS:
        value = _named_value(text, heading, name)
        if not value:
            errors.append(f"G2 creative master handoff missing {name}")
    invariants = _named_value(text, heading, "INVARIANTS")
    present = {name for name in MASTER_INVARIANTS if re.search(rf"(?:^|;)\s*{name}\s*=\s*[^;]+", invariants)}
    for name in sorted(MASTER_INVARIANTS - present):
        errors.append(f"G2 creative master invariants missing {name}")
    grammar = _named_value(text, heading, "SCENE_GRAMMAR")
    grammar_present = {name for name in GRAMMAR_RELATIONS if re.search(rf"(?:^|;)\s*{name}\s*=\s*[^;]+", grammar)}
    for name in sorted(GRAMMAR_RELATIONS - grammar_present):
        errors.append(f"G2 creative master scene grammar missing {name}")
    selected = _named_value(text, "## Direction selection handoff", "SELECTED_DIRECTION")
    if _named_value(text, heading, "SOURCE_DIRECTION") != selected:
        errors.append("G2 creative master SOURCE_DIRECTION must match the reviewed direction")

    matching = [row for row in rows if len(row) >= 4 and row[0] == master]
    if master and len(matching) != 1:
        errors.append(f"G2 creative master {master} must match exactly one artistic master")
    elif matching:
        row = matching[0]
        physical_error = _physical_composition_error(project_dir, row[3], f"G2 creative master {master}")
        if physical_error:
            errors.append(physical_error)
    return errors


def scene_grammar_errors(project_dir: Path) -> list[str]:
    outline_rows = table_rows(
        markdown(project_dir, "content-architecture.md"),
        "## Sitemap / page or section outline", "Scene ID",
    )
    expected = {row[0] for row in outline_rows if len(row) >= 5 and re.fullmatch(r"SCN-[0-9]{3,}", row[0])}
    rows = table_rows(markdown(project_dir, "visual-system.md"), "## Scene grammar", "Scene ID")
    errors: list[str] = []
    seen: set[str] = set()
    for row in rows:
        if len(row) < 8 or not all(row[:8]):
            errors.append("G3 Scene Grammar contains an incomplete row")
            continue
        if row[0] in seen:
            errors.append(f"G3 duplicate Scene Grammar row: {row[0]}")
        seen.add(row[0])
        if row[0] not in expected:
            errors.append(f"G3 Scene Grammar {row[0]} is absent from G1 outline")
    for scene_id in sorted(expected - seen):
        errors.append(f"G3 missing Scene Grammar for scene {scene_id}")
    return errors


def design_fingerprint_errors(project_dir: Path) -> list[str]:
    text = markdown(project_dir, "qa-release.md")
    fields = (
        "BACKGROUND_CHARACTER", "ACCENT_CHARACTER", "DISPLAY_TYPE_CHARACTER",
        "HERO_COMPOSITION", "HERO_MEDIA", "SIGNATURE_MECHANISM", "DEPTH_MEDIUM", "MOTION_INTENSITY",
    )
    return [
        f"G5 design fingerprint missing {name}"
        for name in fields
        if not _named_value(text, "## Design fingerprint", name)
    ]


def creative_master_fidelity_errors(project_dir: Path) -> list[str]:
    """Validate the compact G2-to-G3 creative-master handoff."""
    creative = markdown(project_dir, "creative-direction.md")
    visual = markdown(project_dir, "visual-system.md")
    errors = creative_master_errors(project_dir)
    master = _named_value(creative, "## Creative master handoff", "CREATIVE_MASTER")
    source = _named_value(visual, "## Creative master development", "CREATIVE_MASTER_SOURCE")
    if source != master:
        errors.append(f"G3 creative master source {source or '<empty>'} does not match selected {master or '<empty>'}")
    for name in ("INVARIANTS_PRESERVED", "DELIBERATE_DEVIATIONS", "HERO_BODY_TRANSLATION"):
        if not _named_value(visual, "## Creative master development", name):
            errors.append(f"G3 creative master development missing {name}")
    return errors


def scene_visual_errors(project_dir: Path, profile: str = "focused") -> list[str]:
    rows = table_rows(
        markdown(project_dir, "visual-system.md"),
        "### Scene visual opportunities", "Scene",
    )
    errors: list[str] = []
    complete_scenes: list[str] = []
    seen_cmp: set[str] = set()
    for row in rows:
        if len(row) < 8:
            errors.append("G3 scene visual opportunity contains a malformed row")
            continue
        scene_name, job, baseline, mode, desktop, mobile, decomposition, decision = row[:8]
        row_complete = all((scene_name, job, baseline, mode, desktop, mobile, decomposition, decision))
        if mode not in SCENE_PRODUCTION_MODES:
            errors.append(f"G3 {scene_name or 'scene'} has invalid production mode")
            row_complete = False
        for viewport, value in (("desktop", desktop), ("mobile", mobile)):
            match = re.fullmatch(r"(CMP-[0-9]{3,}):(.+)", value.strip().strip("`"))
            if not match:
                errors.append(f"G3 {scene_name or 'scene'} needs {viewport} CMP-ID:path evidence")
                row_complete = False
                continue
            cmp_id, reference = match.groups()
            if cmp_id in seen_cmp:
                errors.append(f"G3 duplicate composition ID: {cmp_id}")
            seen_cmp.add(cmp_id)
            physical_error = _physical_composition_error(project_dir, reference, f"G3 {cmp_id}")
            if physical_error:
                errors.append(physical_error)
                row_complete = False
        if not all(token in decomposition for token in ("HTML/CSS", "IMG-", "FX-")):
            errors.append(f"G3 {scene_name or 'scene'} lacks HTML/CSS + IMG-* + FX-* decomposition")
            row_complete = False
        if row_complete:
            complete_scenes.append(scene_name)
    if not any("HERO" in name.upper() for name in complete_scenes):
        errors.append("G3 requires a composed hero scene")
    if profile in {"standard", "extended"} and not any("HERO" not in name.upper() for name in complete_scenes):
        errors.append("G3 requires one distinct composed body scene")
    return errors


def color_direction_errors(project_dir: Path) -> list[str]:
    text = markdown(project_dir, "visual-system.md")
    rows = table_rows(text, "### Color direction territories", "Territory")
    required_territories = {"BASELINE", "BRAND_LED", "CHALLENGER"}
    composition_markers = {
        "LUMINANCE", "CHROMA", "TEMPERATURE", "DOMINANT_ACCENT",
        "NEUTRALS", "MEDIA", "LARGE_SURFACES", "PERCEPTION",
    }
    role_markers = {"dominant", "background", "foreground", "support", "accent"}
    errors: list[str] = []
    found: set[str] = set()
    selected = 0
    evidence_ids: set[str] = set()
    evidence_paths: set[str] = set()
    for row in rows:
        if len(row) < 7:
            errors.append("G3 color territory contains a malformed row")
            continue
        territory, evidence, hierarchy, provenance, composition, accessibility, verdict = row[:7]
        if territory not in required_territories:
            errors.append(f"G3 invalid color territory: {territory or '<empty>'}")
        else:
            found.add(territory)
        match = re.fullmatch(r"(CLR-[0-9]{3,}):(.+)", evidence.strip().strip("`"))
        if not match:
            errors.append(f"G3 {territory or 'color territory'} needs physical CLR-ID:path evidence")
        else:
            color_id, reference = match.groups()
            if color_id in evidence_ids:
                errors.append(f"G3 duplicate color evidence ID: {color_id}")
            if reference in evidence_paths:
                errors.append(f"G3 color territories must use distinct render files: {reference}")
            evidence_ids.add(color_id); evidence_paths.add(reference)
            physical_error = _physical_composition_error(project_dir, reference, f"G3 {color_id}")
            if physical_error:
                errors.append(physical_error)
        hierarchy_lower = hierarchy.lower()
        if not role_markers.issubset({marker for marker in role_markers if marker in hierarchy_lower}) \
                or len(re.findall(r"\d+(?:[.,]\d+)?\s*%", hierarchy)) < 5:
            errors.append(f"G3 {territory or 'color territory'} lacks five color roles with approximate percentages")
        missing_composition = sorted(marker for marker in composition_markers if marker not in composition.upper())
        if missing_composition:
            errors.append(f"G3 {territory or 'color territory'} COLOR_COMPOSITION missing {', '.join(missing_composition)}")
        if not all((provenance, accessibility)):
            errors.append(f"G3 {territory or 'color territory'} lacks provenance/accessibility evidence")
        if verdict == "SELECTED":
            selected += 1
        elif verdict != "REJECTED":
            errors.append(f"G3 {territory or 'color territory'} has invalid verdict")
    for territory in sorted(required_territories - found):
        errors.append(f"G3 missing color territory {territory}")
    if selected != 1:
        errors.append("G3 color direction requires exactly one SELECTED territory")

    challenge_rows = table_rows(text, "### Independent color challenge", "Physical evidence")
    if len(challenge_rows) != 1:
        errors.append("G3 independent color challenge requires exactly one evidence row")
        return errors
    row = challenge_rows[0]
    if len(row) < 8 or not all(row[:7]):
        errors.append("G3 independent color challenge row is incomplete")
        return errors
    evidence, accent_removed, neutral_swap, category_swap, _identity_test, _drift, advantage, verdict = row[:8]
    match = re.fullmatch(r"(CLR-[0-9]{3,}):(.+)", evidence.strip().strip("`"))
    if not match:
        errors.append("G3 independent color challenge needs physical CLR-ID:path evidence")
    else:
        color_id, reference = match.groups()
        physical_error = _physical_composition_error(project_dir, reference, f"G3 {color_id}")
        if physical_error:
            errors.append(physical_error)
    if verdict != "PASS":
        errors.append("G3 independent color challenge is not PASS")
    return errors
