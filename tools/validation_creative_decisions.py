"""Evidence-led v2 checks: provenance and recorded order, never artistic scores."""
from pathlib import Path
from hashlib import sha256
import json
import re
from validation_common import load_json, section, table_rows

CONTRACT = 'evidence-led-v2'
PROOF_MODES = {'GENERATED_IMAGE','TYPOGRAPHIC_STUDY','PHOTO_TREATMENT','COMPOSITION_STUDY','MATERIAL_STUDY','MOTION_STUDY','INTERACTION_PROTOTYPE','3D_STUDY'}
PLAN_SECTIONS = {'direction-divergence': ('creative-direction.md', ('## Project-specific quality bar','## Creative idea')),
                 'visual-experience': ('visual-system.md', ('## Global page rhythm',))}

def evidence_led(project):
    project = Path(project)
    run = project.parent/'run.json'
    config = project/'project.config.json'
    # Managed run metadata is authoritative: a specialist cannot downgrade it.
    if run.is_file() and 'design_contract' in load_json(run):
        return load_json(run).get('design_contract') == CONTRACT
    return config.is_file() and load_json(config).get('design_contract') == CONTRACT

def bounded_evidence(project, reference):
    root = Path(project).resolve()
    path = root/reference
    if Path(reference).is_absolute() or ':' in reference or not reference:
        return None
    for part in (path, *path.parents):
        if part == root: break
        if part.is_symlink() or (part.exists() and getattr(part.lstat(),'st_file_attributes',0) & 1024):
            return None
    resolved = path.resolve()
    return resolved if resolved.is_relative_to(root) and resolved.is_file() else None

def source_rows(project):
    text = (Path(project)/'research-strategy.md').read_text(encoding='utf-8')
    return table_rows(text,'## Discovered evidence authority','Source ID')

def source_errors(project):
    errors=[]; seen=set()
    for row in source_rows(project):
        if len(row)<8 or not all(row[:8]):
            errors.append('research source requires eight populated provenance fields'); continue
        source,kind,actual,finding,truth,evidence,date,relevance=row[:8]
        if not re.fullmatch(r'SRC-\d{3,}',source) or source in seen: errors.append('invalid or duplicate research source ID')
        seen.add(source)
        if kind not in {'WEB','FILE','USER','OBSERVATION'}: errors.append(f'{source}: invalid source type')
        if truth not in {'VERIFIED','USER_SUPPLIED','HYPOTHESIS'}: errors.append(f'{source}: invalid truth status')
        try:
            from datetime import date as observed_date
            observed_date.fromisoformat(date)
        except ValueError:
            errors.append(f'{source}: valid observed date required')
        if not re.match(r'^https?://\S+$',evidence) and bounded_evidence(project,evidence) is None:
            errors.append(f'{source}: actual URL or physical bounded evidence required')
        if kind=='WEB' and not re.match(r'^https?://\S+$',actual): errors.append(f'{source}: actual web source URL required')
    if not seen: errors.append('research has no verifiable source rows')
    return errors

def proof_mode(project):
    text=(Path(project)/'creative-direction.md').read_text(encoding='utf-8')
    body=section(text,'## Artistic master')
    match=re.search(r'(?m)^PROOF_MODE:\s*(\S+)\s*$',body)
    return match.group(1) if match else None

def generation_required(project):
    return not evidence_led(project) or proof_mode(project)=='GENERATED_IMAGE'

def plan_digest(project,stage):
    filename,headings=PLAN_SECTIONS[stage]
    text=(Path(project)/filename).read_text(encoding='utf-8')
    values=[section(text,h).strip() for h in headings]
    if any(not value for value in values): raise ValueError('plan sections are missing')
    return sha256(json.dumps(values,ensure_ascii=False).encode()).hexdigest()

def plan_errors(project,stage):
    if not evidence_led(project) or stage not in PLAN_SECTIONS: return []
    path=Path(project).parent/'control/design-plans.json'
    record=load_json(path).get(stage,{}) if path.is_file() else {}
    try: digest=plan_digest(project,stage)
    except (OSError,ValueError): return ['design plan missing']
    if not record or record.get('digest')!=digest:
        return [f'{stage}: plan must be sealed before derived evidence; reseal invalidates prior evidence']
    return []

def critical_media_errors(project):
    if not evidence_led(project): return []
    text=(Path(project)/'visual-system.md').read_text(encoding='utf-8')
    rows=table_rows(text,'### Composition-critical media','Scene ID')
    outline=table_rows((Path(project)/'content-architecture.md').read_text(encoding='utf-8'),'## Sitemap / page or section outline','Scene ID')
    expected={r[0] for r in outline if r and re.fullmatch(r'SCN-\d{3,}',r[0])}
    seen=set();errors=[]
    for row in rows:
        if len(row)<5 or not all(row[:5]): errors.append('critical media decision is incomplete');continue
        scene,decision,reason,evidence,boundary=row[:5]
        if scene not in expected or scene in seen: errors.append('critical media scene unknown or duplicate')
        seen.add(scene)
        if decision not in {'CRITICAL','NON_CRITICAL','NO_MEDIA'}: errors.append(f'{scene}: invalid critical media decision')
        if decision=='CRITICAL' and bounded_evidence(project,evidence) is None:
            errors.append(f'{scene}: critical media requires physical production-feasible proof before G3')
        elif decision=='CRITICAL':
            from project_validation import _physical_composition_error
            physical=_physical_composition_error(Path(project),evidence,f'{scene} critical media')
            if physical: errors.append(physical)
    if seen!=expected: errors.append('critical media decisions must cover every scene')
    return errors
