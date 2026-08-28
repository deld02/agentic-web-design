"""Cross-gate traceability for project-specific identity authority."""

from pathlib import Path
import re

from validation_common import load_json, section, table_rows


AUTHORITIES = {"BINDING", "EVOLVE_WITHIN_LIMITS", "OPEN_TO_REPLACE"}
STATUSES = {"EVALUATED", "NO_EXISTING_IDENTITY"}


def _markdown(project_dir: Path, name: str) -> str:
    path = project_dir / name
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _named_value(text: str, heading: str, name: str) -> str:
    match = re.search(rf"(?m)^[ \t]*{re.escape(name)}:[ \t]*(.+?)[ \t]*$", section(text, heading))
    return match.group(1).strip() if match else ""


def _references(value: str) -> set[str]:
    return set(re.findall(r"IDN-[0-9]{3,}", value))


def _contract(project_dir: Path) -> tuple[str, set[str], list[str]]:
    text = _markdown(project_dir, "research-strategy.md")
    status = _named_value(text, "## Identity authority contract", "IDENTITY_STATUS").strip("` ")
    rows = table_rows(text, "## Identity authority contract", "Identity ID")
    errors: list[str] = []
    identity_ids: set[str] = set()
    if status not in STATUSES:
        return status, identity_ids, ["G1 identity authority has invalid or missing IDENTITY_STATUS"]
    config = load_json(project_dir / "project.config.json")
    if status == "NO_EXISTING_IDENTITY":
        if rows:
            errors.append("G1 NO_EXISTING_IDENTITY cannot contain identity authority rows")
        if config.get("visual_identity_mode") in {"inherit", "evolve"}:
            errors.append("G1 inherit/evolve identity mode requires evaluated identity evidence")
        return status, identity_ids, errors
    if not rows:
        errors.append("G1 EVALUATED identity authority requires at least one IDN row")
    for row in rows:
        if len(row) < 8 or not all(row[:8]):
            errors.append("G1 identity authority contains an incomplete row")
            continue
        identity_id, authority = row[0], row[3]
        if not re.fullmatch(r"IDN-[0-9]{3,}", identity_id):
            errors.append(f"G1 invalid identity ID: {identity_id or '<empty>'}")
        elif identity_id in identity_ids:
            errors.append(f"G1 duplicate identity ID: {identity_id}")
        identity_ids.add(identity_id)
        if authority not in AUTHORITIES:
            errors.append(f"G1 {identity_id or 'identity row'} has invalid authority {authority or '<empty>'}")
    return status, identity_ids, errors


def identity_authority_errors(project_dir: Path) -> list[str]:
    return _contract(project_dir)[2]


def identity_direction_trace_errors(project_dir: Path) -> list[str]:
    status, expected, errors = _contract(project_dir)
    text = _markdown(project_dir, "creative-direction.md")
    directions = {row[0] for row in table_rows(text, "## Direction divergence", "Direction ID") if row}
    rows = table_rows(text, "### Identity constraint fit", "Direction ID")
    seen: set[str] = set()
    if len(rows) != 3:
        errors.append("G2 identity constraint fit requires exactly one row per direction")
    for row in rows:
        if len(row) < 5 or not all(row[:5]):
            errors.append("G2 identity constraint fit contains an incomplete row")
            continue
        direction_id, references, verdict = row[0], row[1], row[4]
        if direction_id not in directions:
            errors.append(f"G2 identity fit references unknown direction {direction_id or '<empty>'}")
        if direction_id in seen:
            errors.append(f"G2 duplicate identity fit for {direction_id}")
        seen.add(direction_id)
        if status == "NO_EXISTING_IDENTITY":
            if references.strip("` ") != "NO_EXISTING_IDENTITY":
                errors.append(f"G2 {direction_id} must record NO_EXISTING_IDENTITY")
        elif _references(references) != expected:
            errors.append(f"G2 {direction_id} must address every G1 identity ID")
        if verdict != "PASS":
            errors.append(f"G2 {direction_id} identity constraint fit is not PASS")
    for direction_id in sorted(directions - seen):
        errors.append(f"G2 missing identity constraint fit for {direction_id}")
    inheritance = _named_value(text, "## Creative master handoff", "IDENTITY_INHERITANCE").strip("` ")
    if status == "NO_EXISTING_IDENTITY" and inheritance != "NO_EXISTING_IDENTITY":
        errors.append("G2 master must inherit NO_EXISTING_IDENTITY")
    elif status == "EVALUATED" and _references(inheritance) != expected:
        errors.append("G2 master must inherit every G1 identity ID")
    return errors


def identity_visual_trace_errors(project_dir: Path) -> list[str]:
    status, expected, errors = _contract(project_dir)
    text = _markdown(project_dir, "visual-system.md")
    inheritance = _named_value(text, "## Creative master development", "IDENTITY_INHERITANCE").strip("` ")
    if status == "NO_EXISTING_IDENTITY" and inheritance != "NO_EXISTING_IDENTITY":
        errors.append("G3 visual system must inherit NO_EXISTING_IDENTITY")
    elif status == "EVALUATED" and _references(inheritance) != expected:
        errors.append("G3 visual system must inherit every G1 identity ID")
    rows = table_rows(text, "### Independent color challenge", "Physical evidence")
    if len(rows) != 1 or len(rows[0]) < 8:
        return errors + ["G3 identity equity requires the complete independent color challenge row"]
    identity_test, drift_finding, verdict = rows[0][4], rows[0][5], rows[0][7]
    if status == "NO_EXISTING_IDENTITY" and identity_test.strip("` ") != "NO_EXISTING_IDENTITY":
        errors.append("G3 color challenge must record NO_EXISTING_IDENTITY")
    elif status == "EVALUATED" and _references(identity_test) != expected:
        errors.append("G3 color challenge must test every G1 identity ID")
    if not drift_finding:
        errors.append("G3 color challenge lacks recognition / brand-drift finding")
    if verdict == "BRAND_DRIFT":
        errors.append("G3 independent color challenge detected BRAND_DRIFT")
    return errors
