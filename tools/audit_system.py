#!/usr/bin/env python3
from datetime import date, datetime, timedelta
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today()
errors = []


def load(rel):
    path = ROOT / rel
    if not path.is_file():
        errors.append(f'MISSING: {rel}')
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        errors.append(f'INVALID JSON {rel}: {exc}')
        return {}


def day(value, label):
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except Exception:
        errors.append(f'{label} must be YYYY-MM-DD')
        return None


manifest = load('repo-manifest.json')
governance = load('config/system-governance.json')
capabilities = load('config/design-capabilities.json')
resources = load('config/resource-sources.json')
version = manifest.get('version')

if governance.get('version') != version:
    errors.append('system governance version mismatch')
if governance.get('operational_agent') is not False:
    errors.append('System Steward must remain outside the operational agent registry')
cadence = governance.get('cadence_days')
if not isinstance(cadence, int) or isinstance(cadence, bool) or not 30 <= cadence <= 180:
    errors.append('governance cadence_days must be 30..180')
last_audit = day(governance.get('last_audit'), 'last_audit')
next_review = day(governance.get('next_review'), 'next_review')
if last_audit and next_review and cadence:
    if next_review > last_audit + timedelta(days=cadence):
        errors.append('next_review exceeds governance cadence')
    if TODAY > next_review:
        errors.append(f'system audit overdue since {next_review}')
if governance.get('verdict') not in {'PASS', 'PASS_WITH_CONDITIONS', 'FAIL'}:
    errors.append('invalid system audit verdict')

for rel in ('governance/system-steward.md', governance.get('latest_report', ''), 'docs/standards/landing-quality.md'):
    if not rel or not (ROOT / rel).is_file():
        errors.append(f'MISSING: {rel}')
report = ROOT / governance.get('latest_report', '')
if report.is_file():
    text = report.read_text(encoding='utf-8')
    for heading in ('## KEEP', '## IMPROVE', '## ADD', '## REMOVE', '## Scenario verdicts', '## Next review'):
        if heading not in text:
            errors.append(f'latest system audit missing {heading}')

if governance.get('scope') != 'landing-creation-only':
    errors.append('system governance scope must remain landing-creation-only')
required_out={'seo-strategy','analytics','privacy-legal','application-security','commerce','cms','localization','post-launch-operations'}
if not required_out.issubset(set(governance.get('out_of_scope',[]))):
    errors.append('system governance must keep non-landing disciplines out of scope')
for scenario in governance.get('scenarios', []):
    if not str(scenario.get('id','')).startswith('landing-'):
        errors.append(f'{scenario.get("id")}: non-landing scenario is not allowed')
    if scenario.get('support') not in {'CORE', 'CORE_WITH_RISK_TRIAGE'}:
        errors.append(f'{scenario.get("id")}: invalid scenario support')

for item in capabilities.get('capabilities', []):
    checked = day(item.get('last_checked'), f'{item.get("id")}.last_checked')
    days = item.get('review_by_days')
    if checked and isinstance(days, int) and TODAY > checked + timedelta(days=days):
        errors.append(f'{item.get("id")}: capability review overdue')
resource_checked = day(resources.get('checked'), 'resource registry checked')
if resource_checked:
    for item in resources.get('sources', []):
        days = item.get('review_by_days')
        if isinstance(days, int) and TODAY > resource_checked + timedelta(days=days):
            errors.append(f'{item.get("id")}: resource review overdue')

if errors:
    print('SYSTEM AUDIT FAILED')
    for error in errors:
        print('-', error)
    sys.exit(1)
print(f'OK — landing-only system governance current; {len(governance.get("scenarios", []))} scenarios; next review {governance.get("next_review")}.')
