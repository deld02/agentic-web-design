"""Color evidence checks; artistic quality belongs to independent review."""
from pathlib import Path
import re
from validation_common import table_rows

def markdown(project,filename):
    return (Path(project)/filename).read_text(encoding="utf-8")

def _named_value(text,heading,name):
    from project_validation import _named_value as value
    return value(text,heading,name)

def _physical_composition_error(project,reference,label):
    from project_validation import _physical_composition_error as check
    return check(project,reference,label)

def color_direction_errors(project_dir: Path) -> list[str]:
    from validation_creative_decisions import evidence_led
    if evidence_led(project_dir):
        return evidence_led_color_errors(project_dir)
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


def evidence_led_color_errors(project_dir: Path) -> list[str]:
    """Require real surface proof; expand alternatives only for material uncertainty."""
    text=markdown(project_dir,'visual-system.md')
    uncertainty=_named_value(text,'### Color direction territories','COLOR_UNCERTAINTY')
    reason=_named_value(text,'### Color direction territories','COLOR_REASON')
    rows=table_rows(text,'### Color direction territories','Territory')
    errors=[]
    if uncertainty not in {'LOW','MATERIAL'} or not reason: errors.append('G3 requires COLOR_UNCERTAINTY and COLOR_REASON')
    if len(rows)<(2 if uncertainty=='MATERIAL' else 1): errors.append('G3 insufficient physical color evidence for declared uncertainty')
    selected=0;paths=set()
    for row in rows:
        if len(row)<7 or not all(row[:7]): errors.append('G3 incomplete color evidence row');continue
        _,evidence,hierarchy,provenance,composition,accessibility,verdict=row[:7]
        match=re.fullmatch(r'CLR-\d{3,}:(.+)',evidence)
        if not match: errors.append('G3 color evidence requires CLR-ID:path');continue
        if match[1] in paths: errors.append('G3 color alternatives reuse physical evidence')
        paths.add(match[1])
        physical=_physical_composition_error(project_dir,match[1],'G3 color')
        if physical: errors.append(physical)
        if verdict=='SELECTED': selected+=1
        elif verdict!='REJECTED': errors.append('G3 invalid color verdict')
    if selected!=1: errors.append('G3 color requires one selected system')
    # Independent color assessment lives in the protected review axis, not an owner PASS row.
    return errors
