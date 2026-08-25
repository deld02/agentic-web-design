#!/usr/bin/env python3
from pathlib import Path
from datetime import date, datetime, timedelta
import json, sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'config/resource-sources.json'
AGENTS = ROOT / 'config/agents.json'
METHOD = ROOT / 'docs/methods/resource-selection.md'
DOC = ROOT / 'docs/resources/creative-resource-registry.md'

errors = []


def load(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        errors.append(f'INVALID JSON {path.relative_to(ROOT)}: {e}')
        return {}


for path in (REGISTRY, AGENTS, METHOD, DOC):
    if not path.exists():
        errors.append(f'MISSING: {path.relative_to(ROOT)}')

registry = load(REGISTRY) if REGISTRY.exists() else {}
agents_cfg = load(AGENTS) if AGENTS.exists() else {}
agent_ids = {a.get('id') for a in agents_cfg.get('agents', []) if a.get('id')}

allowed = registry.get('allowed', {})
allowed_roles = set(allowed.get('roles', []))
allowed_kinds = set(allowed.get('kinds', []))
allowed_priorities = set(allowed.get('priorities', []))
allowed_license_scopes = set(allowed.get('license_scopes', []))
allowed_reuse_classes = set(allowed.get('reuse_classes', []))

EXPECTED_SELECTION_ORDER = [
    'problem_match',
    'reuse_safety',
    'stack_fit',
    'performance_accessibility',
    'cost_availability',
    'freshness',
    'novelty',
]

policy = registry.get('policy', {})
try:
    registry_checked = datetime.strptime(registry.get('checked'), '%Y-%m-%d').date()
except (TypeError, ValueError):
    registry_checked = None
    errors.append('resource registry checked must be YYYY-MM-DD')
if policy.get('default_decision') != 'NO_EXTERNAL_RESOURCE_REQUIRED':
    errors.append('resource policy default_decision must be NO_EXTERNAL_RESOURCE_REQUIRED')
if policy.get('selection_order') != EXPECTED_SELECTION_ORDER:
    errors.append('resource policy selection_order must keep safety/fit before novelty')
max_families = policy.get('max_source_families_per_decision')
if not isinstance(max_families, int) or isinstance(max_families, bool) or not 1 <= max_families <= 3:
    errors.append('resource policy max_source_families_per_decision must be integer 1..3')
max_options = policy.get('max_options_returned')
if not isinstance(max_options, int) or isinstance(max_options, bool) or not 1 <= max_options <= 3:
    errors.append('resource policy max_options_returned must be integer 1..3')
if not isinstance(policy.get('consult_when'), list) or not policy.get('consult_when'):
    errors.append('resource policy consult_when must be non-empty list')
if not isinstance(policy.get('do_not_consult_when'), list) or not policy.get('do_not_consult_when'):
    errors.append('resource policy do_not_consult_when must be non-empty list')
if not isinstance(policy.get('reuse_rule'), str) or not policy.get('reuse_rule', '').strip():
    errors.append('resource policy reuse_rule must be non-empty string')

if not allowed_roles or not allowed_roles.issubset(agent_ids):
    errors.append('resource registry allowed.roles must reference registered agents only')
for name, values in [
    ('kinds', allowed_kinds),
    ('priorities', allowed_priorities),
    ('license_scopes', allowed_license_scopes),
    ('reuse_classes', allowed_reuse_classes),
]:
    if not values:
        errors.append(f'resource registry allowed.{name} must be non-empty')

sources = registry.get('sources', [])
if not isinstance(sources, list) or len(sources) < 8:
    errors.append('resource registry must contain at least 8 curated sources')
    sources = sources if isinstance(sources, list) else []

ids = [s.get('id') for s in sources]
if None in ids or any(not isinstance(x, str) or not x.strip() for x in ids):
    errors.append('resource registry source id must be non-empty string')
if len(ids) != len(set(ids)):
    errors.append('resource registry source ids must be unique')

required_fields = {
    'id', 'name', 'url', 'roles', 'kinds', 'categories', 'priority', 'best_for', 'avoid_for',
    'stack', 'cost', 'license_scope', 'reuse_class', 'reusable_by_default', 'license_policy', 'review_by_days'
}

coverage = {'REFERENCE_ONLY': 0, 'CODE_SOURCE': 0, 'ASSET_SOURCE': 0, 'TOOL': 0}
priority_s = 0

for source in sources:
    sid = source.get('id', '<unknown>')
    missing = sorted(required_fields - set(source))
    if missing:
        errors.append(f'{sid}: missing fields {missing}')
        continue

    roles = source.get('roles')
    if not isinstance(roles, list) or not roles or any(r not in allowed_roles for r in roles):
        errors.append(f'{sid}: roles must be non-empty and allowed')

    kinds = source.get('kinds')
    if not isinstance(kinds, list) or not kinds or any(k not in allowed_kinds for k in kinds):
        errors.append(f'{sid}: kinds must be non-empty and allowed')
    else:
        for kind in set(kinds):
            coverage[kind] = coverage.get(kind, 0) + 1

    if source.get('priority') not in allowed_priorities:
        errors.append(f'{sid}: invalid priority {source.get("priority")}')
    elif source.get('priority') == 'S':
        priority_s += 1

    for field in ('categories', 'best_for', 'avoid_for', 'stack'):
        value = source.get(field)
        if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x.strip() for x in value):
            errors.append(f'{sid}: {field} must be non-empty string list')

    if not isinstance(source.get('url'), str) or not source.get('url', '').startswith('https://'):
        errors.append(f'{sid}: url must be https')
    if not isinstance(source.get('cost'), str) or not source.get('cost', '').strip():
        errors.append(f'{sid}: cost must be non-empty string')
    if source.get('license_scope') not in allowed_license_scopes:
        errors.append(f'{sid}: invalid license_scope')
    if source.get('reuse_class') not in allowed_reuse_classes:
        errors.append(f'{sid}: invalid reuse_class')
    if not isinstance(source.get('reusable_by_default'), bool):
        errors.append(f'{sid}: reusable_by_default must be boolean')
    if not isinstance(source.get('license_policy'), str) or not source.get('license_policy', '').strip():
        errors.append(f'{sid}: license_policy must be non-empty string')
    days = source.get('review_by_days')
    if not isinstance(days, int) or isinstance(days, bool) or days <= 0:
        errors.append(f'{sid}: review_by_days must be positive integer')
    elif registry_checked and date.today() > registry_checked + timedelta(days=days):
        errors.append(f'{sid}: source review overdue since {registry_checked + timedelta(days=days)}')

    # Safety invariants: ambiguous/per-item/tool rights never become default reuse.
    if source.get('license_scope') in {'per-item', 'tool-terms'} and source.get('reusable_by_default') is True:
        errors.append(f'{sid}: per-item/tool-terms source cannot be reusable_by_default')
    if source.get('reuse_class') in {'REFERENCE_ONLY', 'VERIFY_AT_USE'} and source.get('reusable_by_default') is True:
        errors.append(f'{sid}: {source.get("reuse_class")} cannot be reusable_by_default')
    if source.get('reuse_class') == 'CC0_ASSET':
        if 'ASSET_SOURCE' not in source.get('kinds', []):
            errors.append(f'{sid}: CC0_ASSET must be an ASSET_SOURCE')
        if source.get('reusable_by_default') is not True:
            errors.append(f'{sid}: CC0_ASSET should be reusable_by_default with provenance still required')
    if source.get('kinds') == ['REFERENCE_ONLY'] and source.get('reuse_class') != 'REFERENCE_ONLY':
        errors.append(f'{sid}: reference-only source must use REFERENCE_ONLY reuse_class')

if priority_s < 3:
    errors.append('resource registry must retain at least 3 priority-S sources')
for kind in ('REFERENCE_ONLY', 'CODE_SOURCE', 'ASSET_SOURCE', 'TOOL'):
    if coverage.get(kind, 0) == 0:
        errors.append(f'resource registry lacks coverage for {kind}')

if errors:
    print('RESOURCE REGISTRY VALIDATION FAILED')
    for error in errors:
        print('-', error)
    sys.exit(1)

print(f'OK — creative resource registry; {len(sources)} sources; conservative selection + reuse safety valid.')
