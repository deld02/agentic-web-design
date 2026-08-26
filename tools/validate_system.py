#!/usr/bin/env python3
from pathlib import Path
from collections import defaultdict, deque
import json, re, sys
from design_capabilities import validate_design_capabilities
from validate_delivery import validate_delivery
from evaluation_harness import validate_harness_config
from project_validation import artistic_master_errors, claim_errors as project_claim_errors, color_direction_errors, creative_master_confirmation_errors, creative_master_errors, creative_master_fidelity_errors, experience_spine_errors, final_render_errors, image_handoff_errors, hero_stress_errors, page_rhythm_errors, project_quality_bar_errors, reference_benchmark_errors, review_checkpoint_errors, scene_color_map_errors, scene_outline, scene_strategy_errors, scene_visual_errors, structural_build_errors, technology_freshness_errors
from validation_common import section

ROOT = Path(__file__).resolve().parents[1]
errors = []
VALID = {'PENDING','ACTIVE','REVIEW','APPROVED','BLOCKED','SUPERSEDED'}
HEADINGS = ['## MISIÓN','## OWNERSHIP','## NO PUEDE','## MODOS','## INPUTS OBLIGATORIOS','## PROCESO','## OUTPUTS OBLIGATORIOS','## ESCALADO','## REGLAS ESPECÍFICAS']
MANDATORY = {'G1':{'research-strategy'},'G2':{'direction-review'},'G3':{'design-review'},'G4':{'production-plan','technology-selection','build-review'}}
CONFIG_KEYS = {'system_version','project_type','delivery_profile','visual_identity_mode','content_model','technology','accessibility_target','implementation_root'}
STATUS_KEYS = {'project','system_version','active_stage','active_gate','active_agent','active_mode','status','gates','checkpoints','release'}
GLOBAL_DECISION_HEADER = ['ID','Scope','Decision','Evidence','Owner','Status']
GLOBAL_DECISION_STATUSES = {'DECIDED','VERIFIED','SUPERSEDED'}

def load(rel):
    path=ROOT/rel
    if not path.exists(): errors.append(f'MISSING: {rel}'); return {}
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc: errors.append(f'INVALID JSON {rel}: {exc}'); return {}

runtime_files=load('config/runtime-files.json')
CORE=list(runtime_files.get('top_level',[]))
CORE.extend(runtime_files.get('required_runtime_files',[]))
CORE.extend(f"tools/{name}" for name in runtime_files.get('tool_files',[]))
for rel in CORE:
    if not (ROOT/rel).exists(): errors.append(f'MISSING: {rel}')
for rel in runtime_files.get('trees',[]):
    if not (ROOT/rel).is_dir(): errors.append(f'MISSING RUNTIME TREE: {rel}')
runtime_skill=ROOT/'skills/agentic-web-design/SKILL.md'
runtime_text=runtime_skill.read_text(encoding='utf-8') if runtime_skill.is_file() else ''
if not re.search(r'(?m)^name:\s*agentic-web-design\s*$',runtime_text) or not re.search(r'(?m)^description:\s*\S.+$',runtime_text):
    errors.append('operational agentic-web-design skill has invalid frontmatter')
manifest=load('repo-manifest.json'); agents_cfg=load('config/agents.json'); gates_cfg=load('config/gates.json')
pipeline_cfg=load('config/pipeline.json'); profiles_cfg=load('config/profiles.json'); tech_cfg=load('config/technology-options.json')
design_cfg=load('config/design-capabilities.json'); governance_cfg=load('config/system-governance.json')
harness_cfg=load('harness/scenarios.json')
load('schemas/project-status.schema.json'); load('schemas/project-config.schema.json')
versions={x.get('version') for x in (manifest,agents_cfg,gates_cfg,pipeline_cfg,profiles_cfg,tech_cfg)}
versions.add(design_cfg.get('system_version'))
versions.add(governance_cfg.get('version'))
if len(versions)!=1: errors.append(f'Version mismatch across manifest/configs: {versions}')
version=manifest.get('version')
for harness_error in validate_harness_config(harness_cfg, version): errors.append(harness_error)

# Registry and contracts
agents=agents_cfg.get('agents',[]); ids=[x.get('id') for x in agents]; amap={x['id']:x for x in agents if x.get('id')}
if None in ids or len(ids)!=len(set(ids)): errors.append('Agent IDs must be present and unique')
if manifest.get('agents')!=len(amap): errors.append(f"Manifest agent count {manifest.get('agents')} != {len(amap)}")
for aid,agent in amap.items():
    path=ROOT/agent.get('file',''); modes=agent.get('modes',[])
    if not path.is_file(): errors.append(f'{aid}: missing contract {path}'); continue
    if not modes or len(modes)!=len(set(modes)): errors.append(f'{aid}: missing/duplicate modes')
    text=path.read_text(encoding='utf-8')
    for heading in HEADINGS:
        if heading not in text: errors.append(f'{aid}: missing heading {heading}')
    if '## GATE / CRITERIO' not in text and '## GATE' not in text: errors.append(f'{aid}: missing gate/criterion section')

# Gates and artifacts
gates=gates_cfg.get('gates',[]); gids=[x.get('id') for x in gates]; gmap={x['id']:x for x in gates if x.get('id')}
if len(gids)!=len(set(gids)): errors.append('Duplicate gate IDs')
release_gate=gates_cfg.get('release_gate')
if release_gate not in gmap or manifest.get('release_gate')!=release_gate: errors.append('Release gate mismatch')
for gid,gate in gmap.items():
    if gate.get('owner') not in amap: errors.append(f'{gid}: unknown owner')
    for reviewer in gate.get('reviewers',[]):
        if reviewer not in amap: errors.append(f'{gid}: unknown reviewer {reviewer}')
    for artifact in gate.get('required_artifacts',[]):
        if not (ROOT/'templates/project'/artifact).is_file(): errors.append(f'{gid}: template missing required artifact {artifact}')
    for cid in sorted(MANDATORY.get(gid,set())-set(gate.get('approval_requires_stages',[]))): errors.append(f'{gid}: missing mandatory core checkpoint {cid}')

# Pipeline semantics and cycle detection
stages=pipeline_cfg.get('stages',[]); sids=[x.get('id') for x in stages]; smap={x['id']:x for x in stages if x.get('id')}
if len(sids)!=len(set(sids)): errors.append('Duplicate pipeline stage IDs')
if pipeline_cfg.get('owner_of_state')!='00': errors.append('Only 00 may own official state')
critical_sequence={
    'technology-selection': {'design-review'},
    'production-plan': {'technology-selection'},
    'implementation': {'technology-selection','production-plan'},
    'build-review': {'implementation'},
}
for sid,expected_dependencies in critical_sequence.items():
    actual=set(smap.get(sid,{}).get('depends_on',[]))
    if actual!=expected_dependencies:
        errors.append(f'{sid}: critical pipeline order mismatch; expected dependencies {sorted(expected_dependencies)}')
for gid,gate in gmap.items():
    for cid in gate.get('approval_requires_stages',[]):
        if cid not in smap: errors.append(f'{gid}: unknown approval-required stage {cid}')
        elif smap[cid].get('gate') is not None: errors.append(f'{gid}: approval-required stage {cid} must be checkpoint')
for sid,stage in smap.items():
    aid=stage.get('agent'); mode=stage.get('mode')
    if aid not in amap: errors.append(f'{sid}: unknown agent {aid}')
    elif mode not in amap[aid].get('modes',[]): errors.append(f'{sid}: invalid mode {mode} for {aid}')
    if stage.get('gate') is not None and stage['gate'] not in gmap: errors.append(f'{sid}: unknown gate')
    entry=stage.get('entry_requires')
    if not isinstance(entry,dict): errors.append(f'{sid}: missing entry_requires'); continue
    for dep in stage.get('depends_on',[]):
        if dep not in smap: errors.append(f'{sid}: unknown dependency {dep}'); continue
        parent=smap[dep]
        if parent.get('gate'):
            allowed=entry.get('gates',{}).get(parent['gate'],[])
            is_review=sid in gmap[parent['gate']].get('approval_requires_stages',[])
            if is_review and not ({'REVIEW','APPROVED'} & set(allowed)): errors.append(f'{sid}: dependency {dep}/{parent["gate"]} lacks REVIEW|APPROVED semantic entry condition')
            elif not is_review and 'APPROVED' not in allowed: errors.append(f'{sid}: dependency {dep}/{parent["gate"]} lacks APPROVED semantic entry condition')
        elif 'APPROVED' not in entry.get('checkpoints',{}).get(dep,[]): errors.append(f'{sid}: checkpoint dependency {dep} lacks APPROVED semantic entry condition')
indeg={sid:0 for sid in smap}; adj=defaultdict(list)
for sid,stage in smap.items():
    for dep in stage.get('depends_on',[]):
        if dep in smap: indeg[sid]+=1; adj[dep].append(sid)
queue=deque([sid for sid,n in indeg.items() if n==0]); visited=0
while queue:
    node=queue.popleft(); visited+=1
    for child in adj[node]:
        indeg[child]-=1
        if indeg[child]==0: queue.append(child)
if visited!=len(smap): errors.append('Pipeline dependency cycle detected')
errors.extend(validate_design_capabilities(ROOT,version,set(amap),set(smap)))
counts=defaultdict(int)
for stage in stages:
    if stage.get('gate'): counts[stage['gate']]+=1
for gid in gmap:
    if counts[gid]!=1: errors.append(f'{gid}: expected exactly one formal stage, found {counts[gid]}')

# Profiles and technology selection contract
profiles=profiles_cfg.get('profiles',{})
if set(profiles)!={'focused','standard','extended'}: errors.append('Profiles must be focused, standard and extended')
for name,profile in profiles.items():
    for field in ('description','design_evidence','qa_scope'):
        if not isinstance(profile.get(field),str) or not profile[field].strip(): errors.append(f'profile {name}: {field} must be non-empty')
option_ids={x.get('id') for x in tech_cfg.get('option_families',[])}
if not {'html','astro','custom'}<=option_ids: errors.append('Technology options must include html, astro and custom')
if len(tech_cfg.get('decision_criteria',[]))<8: errors.append('Technology selection criteria are incomplete')
errors.extend(technology_freshness_errors())

def validate_config(path):
    rel=path.relative_to(ROOT)
    try: data=json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc: errors.append(f'{rel} invalid JSON: {exc}'); return {}
    if set(data)-CONFIG_KEYS: errors.append(f'{rel}: schema validation failed: unknown fields {sorted(set(data)-CONFIG_KEYS)}')
    if CONFIG_KEYS-set(data): errors.append(f'{rel}: schema validation failed: missing fields {sorted(CONFIG_KEYS-set(data))}')
    if data.get('system_version')!=version: errors.append(f'{rel}: system_version mismatch')
    if data.get('project_type') not in {'undetermined','landing'}: errors.append(f'{rel}: invalid project_type')
    if data.get('delivery_profile') not in profiles: errors.append(f'{rel}: invalid delivery_profile')
    if data.get('visual_identity_mode') not in {'undetermined','inherit','evolve','establish'}: errors.append(f'{rel}: invalid visual_identity_mode')
    if data.get('content_model') not in {'undetermined','static','editorial','managed','application','mixed'}: errors.append(f'{rel}: invalid content_model')
    if not isinstance(data.get('implementation_root'),str) or not data.get('implementation_root').strip(): errors.append(f'{rel}: implementation_root must be non-empty string')
    tech=data.get('technology',{})
    if set(tech)!={'status','choice','decision_artifact'} or tech.get('status') not in {'undetermined','selected'} or tech.get('decision_artifact')!='technology-decision.md': errors.append(f'{rel}: invalid technology object')
    return data

configs={path.parent:validate_config(path) for path in [ROOT/'templates/project/project.config.json',*ROOT.glob('projects/*/project.config.json')]}

def requirements(stage,gstate,cstate):
    missing=[]; entry=stage.get('entry_requires',{})
    for gid,allowed in entry.get('gates',{}).items():
        actual=gstate.get(gid,{}).get('status')
        if actual not in allowed: missing.append(f'{gid}={actual}, need {allowed}')
    for cid,allowed in entry.get('checkpoints',{}).items():
        actual=cstate.get(cid,{}).get('status')
        if actual not in allowed: missing.append(f'{cid}={actual}, need {allowed}')
    return missing

def validate_item(rel,label,item):
    status=item.get('status'); evidence=item.get('evidence'); blockers=item.get('blockers'); decision=item.get('last_decision')
    if status not in VALID: errors.append(f'{rel}:{label} invalid status')
    if not isinstance(evidence,list): errors.append(f'{rel}:{label} evidence must be list'); evidence=[]
    if not isinstance(blockers,list): errors.append(f'{rel}:{label} blockers must be list'); blockers=[]
    if status=='APPROVED':
        if not evidence: errors.append(f'{rel}:{label} APPROVED without evidence')
        if blockers: errors.append(f'{rel}:{label} APPROVED with blockers')
        if not isinstance(decision,str) or not decision.strip(): errors.append(f'{rel}:{label} APPROVED without last_decision')
    if status=='BLOCKED' and not blockers: errors.append(f'{rel}:{label} BLOCKED without blocker reason')
    if status=='REVIEW' and not evidence: errors.append(f'{rel}:{label} REVIEW without evidence')

def data_rows(text,heading,header_label):
    body=section(text,heading)
    return [line for line in body.splitlines() if line.startswith('|') and '---' not in line and header_label not in line]

def explicit_text_only(text):
    return bool(re.search(r'(?m)^\s*USER_EXPLICIT_TEXT_ONLY:\s*\S.+$',text))

def final_visual_assets(text):
    rows=[]
    for line in data_rows(text,'## Asset inventory and readiness','ID'):
        cells=[cell.strip() for cell in line.strip().strip('|').split('|')]
        if len(cells)>=6 and re.fullmatch(r'IMG-[0-9]{3,}',cells[0]) and cells[3].startswith('PRIMARY:') and cells[4]=='FINAL' and cells[5]:
            rows.append(cells)
    return rows

def mechanism_rows(text,heading,minimum_cells):
    rows=[]
    for line in section(text,heading).splitlines():
        if not line.startswith('|') or '---' in line or not re.search(r'FX-[0-9]{3,}',line):
            continue
        cells=[cell.strip() for cell in line.strip().strip('|').split('|')]
        if len(cells)>=minimum_cells:
            rows.append(cells)
    return rows

def source_lane_count(value):
    return sum(marker in value for marker in ('LIVE_EXECUTION','MECHANISM_LAB','ELEMENT_BANK','3D_MATERIAL'))

def validate_owner_artifact(project_dir,rel,gid):
    if gid=='G1':
        path=project_dir/'content-architecture.md'
        if path.is_file() and len(data_rows(path.read_text(encoding='utf-8'),'## Narrative alternatives and decision evidence','Candidate'))<2:
            errors.append(f'{rel}:G1 content-architecture must compare at least two narrative alternatives')
        if project_dir.name!='project':
            for claim_error in project_claim_errors(project_dir): errors.append(f'{rel}:{claim_error}')
            for reference_error in reference_benchmark_errors(project_dir): errors.append(f'{rel}:{reference_error}')
            _primary_scenes, outline_errors=scene_outline(project_dir)
            for outline_error in outline_errors: errors.append(f'{rel}:{outline_error}')
            for spine_error in experience_spine_errors(project_dir): errors.append(f'{rel}:{spine_error}')
    if gid=='G3':
        path=project_dir/'visual-system.md'
        if path.is_file():
            text=path.read_text(encoding='utf-8'); foundations=section(text,'## Foundation alternatives and decision evidence')
            if len(data_rows(text,'## Foundation alternatives and decision evidence','Candidate system'))<2 and 'ONLY_VIABLE:' not in foundations:
                errors.append(f'{rel}:G3 visual-system must compare at least two foundations or justify ONLY_VIABLE')
            if len(data_rows(text,'### Content-driven breakpoint evidence','Range tested'))<1:
                errors.append(f'{rel}:G3 visual-system needs observed responsive failure/recomposition evidence')
            if not explicit_text_only(text) and len(data_rows(text,'### Scene visual opportunities','Scene'))<1:
                errors.append(f'{rel}:G3 visual-system must integrate a substantial visual payload across desktop and mobile')
            mechanisms=mechanism_rows(text,'### Effect opportunity map',6)
            if not mechanisms or not any(row[3] and row[4] and row[5] for row in mechanisms):
                errors.append(f'{rel}:G3 visual-system must prototype a selected creative mechanism across responsive/reduced-motion states')
            if project_dir.name!='project':
                for hero_error in hero_stress_errors(project_dir): errors.append(f'{rel}:{hero_error}')
                for master_error in creative_master_fidelity_errors(project_dir): errors.append(f'{rel}:{master_error}')
                for color_error in color_direction_errors(project_dir): errors.append(f'{rel}:{color_error}')
                for scene_color_error in scene_color_map_errors(project_dir): errors.append(f'{rel}:{scene_color_error}')
                for strategy_error in scene_strategy_errors(project_dir): errors.append(f'{rel}:{strategy_error}')
                profile=configs.get(project_dir,{}).get('delivery_profile','focused')
                for scene_error in scene_visual_errors(project_dir,profile): errors.append(f'{rel}:{scene_error}')
                for rhythm_error in page_rhythm_errors(project_dir): errors.append(f'{rel}:{rhythm_error}')
    if gid=='G2':
        path=project_dir/'creative-direction.md'
        if path.is_file():
            if project_dir.name!='project':
                for quality_error in project_quality_bar_errors(project_dir): errors.append(f'{rel}:{quality_error}')
                for artistic_error in artistic_master_errors(project_dir): errors.append(f'{rel}:{artistic_error}')
                for confirmation_error in creative_master_confirmation_errors(project_dir): errors.append(f'{rel}:{confirmation_error}')
                for master_error in creative_master_errors(project_dir): errors.append(f'{rel}:{master_error}')
    if gid=='G4':
        path=project_dir/'production-plan.md'
        if path.is_file():
            text=path.read_text(encoding='utf-8')
            if not explicit_text_only(text) and not final_visual_assets(text):
                errors.append(f'{rel}:G4 production-plan requires at least one scene-bearing PRIMARY FINAL IMG asset')
            for image_error in image_handoff_errors(project_dir): errors.append(f'{rel}:{image_error}')
            for render_error in final_render_errors(project_dir): errors.append(f'{rel}:{render_error}')
            mechanisms=mechanism_rows(text,'### Material effect decisions',10)
            final=[row for row in mechanisms if row[5] and row[7] and row[9] in {'FINAL','STATIC_WINNER_REVIEWED'}]
            if not final:
                errors.append(f'{rel}:G4 production-plan requires a FINAL mechanism or evidenced STATIC_WINNER_REVIEWED')

def parse_global_decisions(project_dir,rel):
    path=project_dir/'decision-log.md'
    if not path.is_file(): errors.append(f'{rel}: missing decision-log.md'); return []
    lines=path.read_text(encoding='utf-8').splitlines(); start=None
    for index,line in enumerate(lines):
        cells=[cell.strip() for cell in line.strip().strip('|').split('|')] if line.startswith('|') else []
        if cells==GLOBAL_DECISION_HEADER: start=index+2; break
    if start is None: errors.append(f'{rel}: decision-log missing global decision header'); return []
    rows=[]; seen=set()
    for line in lines[start:]:
        if not line.startswith('|'): continue
        cells=[cell.strip() for cell in line.strip().strip('|').split('|')]
        if len(cells)!=len(GLOBAL_DECISION_HEADER): errors.append(f'{rel}: malformed global decision row'); continue
        row=dict(zip(GLOBAL_DECISION_HEADER,cells)); did=row['ID']
        if not re.fullmatch(r'PD-[0-9]{3,}',did): errors.append(f'{rel}: invalid global decision ID {did}')
        elif did in seen: errors.append(f'{rel}: duplicate global decision ID {did}')
        seen.add(did)
        if not row['Scope'] or not row['Decision']: errors.append(f'{rel}:{did} incomplete global decision')
        match=re.search(r'([A-Za-z0-9_./-]+\.md)#[A-Za-z0-9_.-]+',row['Evidence'])
        if not match: errors.append(f'{rel}:{did} evidence must link artifact.md#section')
        elif not (project_dir/match.group(1)).is_file(): errors.append(f'{rel}:{did} evidence artifact does not exist: {match.group(1)}')
        if row['Owner'] not in amap: errors.append(f'{rel}:{did} unknown global decision owner {row["Owner"]}')
        if row['Status'] not in GLOBAL_DECISION_STATUSES: errors.append(f'{rel}:{did} invalid global decision status {row["Status"]}')
        rows.append(row)
    return rows

def validate_status(path):
    rel=path.relative_to(ROOT)
    try: data=json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc: errors.append(f'{rel} invalid JSON: {exc}'); return
    if set(data)-STATUS_KEYS: errors.append(f'{rel}: schema validation failed: unknown fields {sorted(set(data)-STATUS_KEYS)}')
    if data.get('system_version')!=version: errors.append(f'{rel}: system_version mismatch')
    if path.parent.name!='project' and path.parent.parent.name=='projects' and data.get('project')!=path.parent.name: errors.append(f'{rel}: project value does not match directory')
    gs=data.get('gates',{}); cs=data.get('checkpoints',{}); expected={sid:s for sid,s in smap.items() if s.get('gate') is None}
    for review_error in review_checkpoint_errors(data): errors.append(f'{rel}:{review_error}')
    if set(gs)!=set(gmap): errors.append(f'{rel}: gate keys mismatch')
    if set(cs)!=set(expected): errors.append(f'{rel}: checkpoint keys mismatch')
    for gid,gate in gmap.items():
        item=gs.get(gid,{}); validate_item(rel,gid,item)
        if item.get('owner')!=gate.get('owner') or item.get('reviewers')!=gate.get('reviewers',[]): errors.append(f'{rel}:{gid} gate contract mismatch')
        if item.get('status')=='APPROVED':
            for cid in gate.get('approval_requires_stages',[]):
                if cs.get(cid,{}).get('status')!='APPROVED': errors.append(f'{rel}:{gid} APPROVED while required checkpoint {cid} is not APPROVED')
            if path.parent.name!='project':
                ev=set(item.get('evidence',[]))
                for artifact in gate.get('required_artifacts',[]):
                    if artifact not in ev: errors.append(f'{rel}:{gid} APPROVED evidence does not reference required artifact {artifact}')
                    artifact_path=path.parent/artifact
                    if artifact_path.is_file():
                        text=artifact_path.read_text(encoding='utf-8')
                        if len(text.strip())<80: errors.append(f'{rel}:{gid} artifact {artifact} is too small')
                        if re.search(r'(?im)^status:\s*(pending|undetermined)\b',text): errors.append(f'{rel}:{gid} artifact {artifact} still has pending marker')
                        if gid in {'G2','G3','G4'} and '## Design capability log' not in text: errors.append(f'{rel}:{gid} artifact {artifact} missing design capability log')
            validate_owner_artifact(path.parent,rel,gid)
    for cid,stage in expected.items():
        item=cs.get(cid,{}); validate_item(rel,cid,item)
        if item.get('agent')!=stage.get('agent') or item.get('mode')!=stage.get('mode'): errors.append(f'{rel}:{cid} checkpoint contract mismatch')
    for sid,stage in smap.items():
        item=gs.get(stage['gate'],{}) if stage.get('gate') else cs.get(sid,{})
        if item.get('status') in {'ACTIVE','APPROVED'}:
            missing=requirements(stage,gs,cs)
            if missing: errors.append(f'{rel}:{sid} entry conditions not met: '+'; '.join(missing))
    active=data.get('active_stage')
    if active not in smap: errors.append(f'{rel}: unknown active_stage {active}')
    else:
        stage=smap[active]
        if data.get('active_agent')!=stage.get('agent') or data.get('active_mode')!=stage.get('mode') or data.get('active_gate')!=stage.get('gate'): errors.append(f'{rel}: active stage contract mismatch')
        item=gs.get(stage['gate'],{}) if stage.get('gate') else cs.get(active,{})
        if data.get('status')=='ACTIVE' and item.get('status')!='ACTIVE': errors.append(f'{rel}: active_stage item is not ACTIVE')
    config=configs.get(path.parent,{})
    if gs.get('G0',{}).get('status')=='APPROVED':
        if config.get('project_type')=='undetermined': errors.append(f'{rel}: G0 cannot be APPROVED with project_type undetermined')
    visual_started=gs.get('G3',{}).get('status') in {'ACTIVE','REVIEW','APPROVED'} or cs.get('design-review',{}).get('status') in {'ACTIVE','REVIEW','APPROVED'}
    if visual_started and config.get('visual_identity_mode')=='undetermined': errors.append(f'{rel}: visual experience cannot start with visual_identity_mode undetermined')
    technology_started=cs.get('technology-selection',{}).get('status') in {'ACTIVE','REVIEW','APPROVED'} or gs.get('G4',{}).get('status') in {'ACTIVE','REVIEW','APPROVED'}
    if technology_started and config.get('content_model')=='undetermined': errors.append(f'{rel}: technology selection cannot start with content_model undetermined')
    tech_approved=cs.get('technology-selection',{}).get('status')=='APPROVED' or gs.get('G4',{}).get('status')=='APPROVED' or gs.get('G5',{}).get('status')=='APPROVED'
    if tech_approved:
        tech=config.get('technology',{})
        if tech.get('status')!='selected' or tech.get('choice') in {None,'','undetermined'}: errors.append(f'{rel}: technology selection approved without selected technology')
        decision=path.parent/'technology-decision.md'
        if decision.is_file():
            rows=[line for line in decision.read_text(encoding='utf-8').splitlines() if line.startswith('|') and '---' not in line and 'Option' not in line]
            if len(rows)<2: errors.append(f'{rel}: technology decision must compare at least two options')
        if cs.get('technology-selection',{}).get('status')=='APPROVED':
            for build_error in structural_build_errors(path.parent): errors.append(f'{rel}:{build_error}')
    if gs.get('G4',{}).get('status')=='APPROVED' or gs.get('G5',{}).get('status')=='APPROVED':
        implementation_ref=config.get('implementation_root')
        if implementation_ref in {None,'','undetermined'}:
            errors.append(f'{rel}: approved production requires implementation_root for physical delivery proof')
        else:
            implementation_path=Path(implementation_ref)
            if not implementation_path.is_absolute(): implementation_path=ROOT/implementation_path
            delivery_errors,_count=validate_delivery(path.parent,implementation_path)
            for delivery_error in delivery_errors:
                errors.append(f'{rel}: delivery proof: {delivery_error}')
        qa=path.parent/'qa-release.md'
        if qa.is_file():
            qa_text=qa.read_text(encoding='utf-8')
            areas=('Objective and action','Content and assets','Visual direction','Responsive composition','Interaction and motion','Build fidelity','Functional delivery','Accessibility and performance')
            for area in areas:
                match=re.search(rf'(?im)^\|\s*{re.escape(area)}\s*\|\s*([A-Z_]+)\s*\|\s*(.*?)\s*\|$',qa_text)
                if not match: errors.append(f'{rel}: release baseline missing area {area}')
                elif match.group(1) not in {'COMPLETE','NOT_APPLICABLE','ACCEPTED_RISK'}: errors.append(f'{rel}: release baseline {area} unresolved ({match.group(1)})')
                elif match.group(1) in {'NOT_APPLICABLE','ACCEPTED_RISK'} and not match.group(2).strip(): errors.append(f'{rel}: release baseline {area} needs rationale/owner')
            evidence_rows=[line for line in qa_text.splitlines() if re.match(r'^\|\s*E-[A-Za-z0-9.-]+\s*\|',line)]
            if len(evidence_rows)<3: errors.append(f'{rel}: qa-release requires at least 3 structured evidence records')
    computed=all(gs.get(gid,{}).get('status')=='APPROVED' for gid in gmap if gid!=release_gate)
    if data.get('release',{}).get('eligible')!=computed: errors.append(f'{rel}: release eligibility mismatch')
    if gs.get(release_gate,{}).get('status')=='APPROVED' and not computed: errors.append(f'{rel}:{release_gate} APPROVED without release prerequisites')
    if gs.get(release_gate,{}).get('status')=='APPROVED':
        decision_rows=parse_global_decisions(path.parent,rel)
        if not decision_rows: errors.append(f'{rel}:{release_gate} requires at least one global decision')
        for row in decision_rows:
            if row['Status'] not in {'VERIFIED','SUPERSEDED'}: errors.append(f'{rel}:{release_gate} global decision {row["ID"]} not VERIFIED')

validate_status(ROOT/'templates/project/status.json')
for status in ROOT.glob('projects/*/status.json'):
    validate_status(status)
    for gate in gates:
        for artifact in gate.get('required_artifacts',[]):
            if not (status.parent/artifact).is_file(): errors.append(f'{status.parent.relative_to(ROOT)} missing {artifact}')

for workflow in (ROOT/'.github/workflows').glob('*.yml'):
    for match in re.finditer(r'(?m)^\s*-?\s*uses:\s*([^\s#]+)',workflow.read_text(encoding='utf-8')):
        use=match.group(1); ref=use.rsplit('@',1)[-1] if '@' in use else ''
        if not use.startswith('./') and not re.fullmatch(r'[0-9a-fA-F]{40}',ref): errors.append(f'{workflow.relative_to(ROOT)} action {use} not pinned to a full commit SHA')
for path in ROOT.glob('projects/**/*'):
    if path.is_file() and path.suffix in {'.md','.json'} and 'replace-me' in path.read_text(encoding='utf-8'): errors.append(f'{path.relative_to(ROOT)} still contains replace-me')
audit=manifest.get('audit',{})
if audit and (audit.get('agents')!=len(amap) or audit.get('gates')!=len(gmap) or audit.get('stages')!=len(smap) or audit.get('dependency_cycles')!=0): errors.append('Manifest audit counts do not match current architecture')

if errors:
    print('VALIDATION FAILED')
    for error in errors: print('-',error)
    sys.exit(1)
print(f'OK — v{version}; {len(amap)} agents; {len(gmap)} gates; {len(smap)} stages; adaptive technology selection valid.')
