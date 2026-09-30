"""Harness-owned planning receipts. No new stage or user approval."""
import json
from pathlib import Path
from datetime import datetime, timezone
from validation_common import section, table_rows
from validation_creative_decisions import evidence_led, PLAN_SECTIONS, plan_digest, plan_errors

def seal_plan(run, stage):
    project=Path(run)/'project'
    if not evidence_led(project) or stage not in PLAN_SECTIONS:
        raise ValueError('planning receipts apply only to evidence-led-v2 direction/visual stages')
    filename,_=PLAN_SECTIONS[stage]
    text=(project/filename).read_text(encoding='utf-8')
    from project_validation import creative_idea_errors, project_quality_bar_errors, page_rhythm_errors
    errors=creative_idea_errors(project)+project_quality_bar_errors(project) if stage=='direction-divergence' else page_rhythm_errors(project)
    if errors: raise ValueError('; '.join(errors))
    path=Path(run)/'control/design-plans.json'
    records=json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}
    digest=plan_digest(project,stage)
    if records.get(stage,{}).get('digest')==digest: return records[stage]
    heading,header=('## Direction divergence','Direction ID') if stage=='direction-divergence' else ('### Section design loop','Scene')
    if table_rows(text,heading,header):
        raise ValueError('seal the plan before recording derived boards/section evidence; changed plan requires a clean new derived record, preserve old files')
    if stage=='visual-experience' and table_rows(text,'## Foundation alternatives and decision evidence','Candidate system'):
        raise ValueError('macro plan must precede foundation decision evidence')
    record={'digest':digest,'sealed_at':datetime.now(timezone.utc).isoformat(),
            'revision':records.get(stage,{}).get('revision',0)+1}
    if record['revision']>2: raise ValueError('planning correction budget exhausted; request user direction')
    records[stage]=record;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(records,indent=2),encoding='utf-8')
    return record

def require_plan(project,stage):
    errors=plan_errors(project,stage)
    if errors: raise ValueError('; '.join(errors))
