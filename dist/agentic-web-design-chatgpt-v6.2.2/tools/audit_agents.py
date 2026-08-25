#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[1]
agents=json.loads((ROOT/'config/agents.json').read_text(encoding='utf-8'))['agents']
pipeline=json.loads((ROOT/'config/pipeline.json').read_text(encoding='utf-8'))['stages']
gates=json.loads((ROOT/'config/gates.json').read_text(encoding='utf-8'))['gates']
used={a['id']:[] for a in agents}
for s in pipeline: used.setdefault(s['agent'],[]).append(f"{s['id']}:{s['mode']}")
owned={a['id']:[] for a in agents}
for g in gates: owned.setdefault(g['owner'],[]).append(g['id'])

lines=['# Generated Agent Contract Audit','', '| ID | Modes | Pipeline use | Gates owned | Contract |','|---|---|---|---|---|']
required=['## MISIÓN','## OWNERSHIP','## NO PUEDE','## MODOS','## INPUTS OBLIGATORIOS','## PROCESO','## OUTPUTS OBLIGATORIOS','## ESCALADO','## REGLAS ESPECÍFICAS']
problems=[]
for a in agents:
    text=(ROOT/a['file']).read_text(encoding='utf-8')
    missing=[h for h in required if h not in text]
    state='OK' if not missing else 'MISSING: '+', '.join(missing)
    if missing: problems.append(f"{a['id']}: {state}")
    lines.append(f"| {a['id']} | {', '.join(a['modes'])} | {', '.join(used.get(a['id'],[])) or 'transversal/none'} | {', '.join(owned.get(a['id'],[])) or '—'} | {state} |")
lines += ['', '## Result', '', 'OK' if not problems else '\n'.join('- '+p for p in problems)]
out=ROOT/'docs/audit/generated-agent-contract-audit.md'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(out.relative_to(ROOT))
print('OK' if not problems else f'{len(problems)} problems')
if problems:
    sys.exit(1)
