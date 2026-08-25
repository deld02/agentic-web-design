from pathlib import Path
from datetime import date, datetime, timedelta
import json
import re

REQUIRED_FIELDS = {
    'id','slot','tier','activation','allowed_agents','allowed_stages','reference',
    'source_url','source_license','revision_policy','vendored','decision_authority',
    'fallback','review_by_days','last_checked'
}


def validate_design_capabilities(root, system_version, agent_ids, stage_ids):
    errors=[]
    path=Path(root)/'config/design-capabilities.json'
    try:
        data=json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        return [f'config/design-capabilities.json invalid: {exc}']

    if data.get('system_version')!=system_version:
        errors.append('design capabilities system_version mismatch')
    policy=data.get('policy',{})
    entry=policy.get('skill_entrypoint','')
    entry_path=Path(root)/entry
    if not entry or not entry_path.is_file():
        errors.append('design capability skill_entrypoint missing')
    else:
        skill_text=entry_path.read_text(encoding='utf-8')
        parts=skill_text.split('---',2)
        if len(parts)<3:
            errors.append('design capability skill frontmatter missing')
        else:
            name=re.search(r'(?m)^name:\s*([a-z0-9-]+)\s*$',parts[1])
            description=re.search(r'(?m)^description:\s*(.+)\s*$',parts[1])
            if not name or name.group(1)!=entry_path.parent.name:
                errors.append('design capability skill name must match folder')
            if not description or len(description.group(1).strip())<30:
                errors.append('design capability skill description is missing or too vague')
        if 'TODO' in skill_text or 'placeholder' in skill_text.lower():
            errors.append('design capability skill contains unfinished scaffold text')
    required_slots=set(policy.get('required_core_slots',[]))
    if required_slots!={'direction-primary','direction-challenger','craft-polish','interface-audit'}:
        errors.append('design capability required_core_slots mismatch')
    if policy.get('max_direction_primary')!=1:
        errors.append('max_direction_primary must be 1')
    if policy.get('max_direction_challenger_per_round')!=1:
        errors.append('max_direction_challenger_per_round must be 1')
    if policy.get('capability_log_heading')!='## Design capability log':
        errors.append('design capability log heading mismatch')

    capabilities=data.get('capabilities',[])
    ids=[item.get('id') for item in capabilities]
    if None in ids or len(ids)!=len(set(ids)):
        errors.append('design capability IDs must be present and unique')
    slot_counts={}
    for item in capabilities:
        cid=item.get('id','<unknown>')
        missing=REQUIRED_FIELDS-set(item)
        if missing:
            errors.append(f'{cid}: missing fields {sorted(missing)}')
            continue
        slot=item['slot']; slot_counts[slot]=slot_counts.get(slot,0)+1
        if not item['source_url'].startswith('https://'):
            errors.append(f'{cid}: source_url must be https')
        if item['source_license'] in {'','unknown'}:
            errors.append(f'{cid}: source license must be classified')
        if item['revision_policy'] not in {'revalidate-at-use','pinned-commit'}:
            errors.append(f'{cid}: invalid revision_policy')
        if not isinstance(item['vendored'],bool) or not isinstance(item['decision_authority'],bool):
            errors.append(f'{cid}: vendored and decision_authority must be boolean')
        if not isinstance(item['review_by_days'],int) or isinstance(item['review_by_days'],bool) or item['review_by_days']<=0:
            errors.append(f'{cid}: review_by_days must be positive integer')
        try:
            checked=datetime.strptime(item['last_checked'],'%Y-%m-%d').date()
            if date.today()>checked+timedelta(days=item['review_by_days']):
                errors.append(f'{cid}: source review overdue since {checked+timedelta(days=item["review_by_days"])}')
        except (TypeError,ValueError):
            errors.append(f'{cid}: last_checked must be YYYY-MM-DD')
        if not item['allowed_agents'] or any(a not in agent_ids for a in item['allowed_agents']):
            errors.append(f'{cid}: allowed_agents contain unknown role')
        if not item['allowed_stages'] or any(s not in stage_ids for s in item['allowed_stages']):
            errors.append(f'{cid}: allowed_stages contain unknown stage')
        if not (Path(root)/item['reference']).is_file():
            errors.append(f'{cid}: local reference missing {item["reference"]}')
        if item['tier']=='core' and (item['activation']!='automatic' or item['fallback']=='none'):
            errors.append(f'{cid}: core capability needs automatic activation and local fallback')
        if item['tier']=='experimental' and item['activation']=='automatic':
            errors.append(f'{cid}: experimental capability cannot activate automatically')
        if slot in {'knowledge-lookup','craft-polish','motion-craft','interface-audit','immersive-booster','direction-challenger','structure-challenger','interaction-reference-extraction','craft-correction','motion-runtime'} and item['decision_authority']:
            errors.append(f'{cid}: slot {slot} cannot have decision authority')
        if slot=='immersive-booster' and item['activation']!='explicit-direction-only':
            errors.append(f'{cid}: immersive booster must be explicit-direction-only')

    for slot in required_slots:
        matching=[item for item in capabilities if item.get('slot')==slot and item.get('tier')=='core']
        if len(matching)!=1:
            errors.append(f'{slot}: expected exactly one core capability')
    if slot_counts.get('direction-primary',0)!=1:
        errors.append('direction-primary: expected exactly one capability')
    return errors
