#!/usr/bin/env python3
from pathlib import Path
import json, sys
from design_capabilities import validate_design_capabilities

ROOT=Path(__file__).resolve().parents[1]

def load(rel):
    return json.loads((ROOT/rel).read_text(encoding='utf-8'))

manifest=load('repo-manifest.json')
agents={item['id'] for item in load('config/agents.json')['agents']}
stages={item['id'] for item in load('config/pipeline.json')['stages']}
errors=validate_design_capabilities(ROOT,manifest['version'],agents,stages)

if errors:
    print('DESIGN CAPABILITY VALIDATION FAILED')
    for error in errors: print('-',error)
    sys.exit(1)
print('OK — design capabilities; slots, activation, ownership, sources and fallbacks valid.')
