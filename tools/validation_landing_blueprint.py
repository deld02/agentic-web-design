"""Whole-page proposal and its single user checkpoint; no extra pipeline stage."""
from pathlib import Path
import json
import re

from validation_common import table_rows, valid_signature


def complete_landing_flow(project: Path) -> bool:
    run = Path(project).parent / 'run.json'
    return run.is_file() and json.loads(run.read_text(encoding='utf-8')).get('user_checkpoint') == 'complete-landing'


def blueprint_errors(project: Path) -> list[str]:
    if not complete_landing_flow(project):
        return []
    project = Path(project).resolve()
    visual = (project / 'visual-system.md').read_text(encoding='utf-8')
    content = (project / 'content-architecture.md').read_text(encoding='utf-8')
    scenes = [r[0] for r in table_rows(content, '## Sitemap / page or section outline', 'Scene ID') if re.fullmatch(r'SCN-\d{3,}', r[0])]
    rows = table_rows(visual, '### Scene visual opportunities', 'Scene')
    declared = [r[0] for r in rows]
    errors = []
    if not scenes or sorted(declared) != sorted(scenes):
        errors.append('G3 complete proposal must compose every architecture scene exactly once')
    for key in ('PAGE_DESKTOP', 'PAGE_MOBILE'):
        match = re.search(rf'(?m)^{key}:\s*([^\r\n]+)', visual)
        path = (project / match[1].strip()).resolve() if match else project
        if not path.is_relative_to(project) or not path.is_file() or not valid_signature(path):
            errors.append(f'G3 complete proposal requires physical {key} full-page evidence')
    return errors


def design_approval_errors(project: Path) -> list[str]:
    if not complete_landing_flow(project):
        return []
    path = Path(project) / '.reviews/design-approval.json'
    if not path.is_file():
        return ['LANDING_APPROVAL_REQUIRED: show the complete desktop/mobile proposal and ask once']
    try:
        approval = json.loads(path.read_text(encoding='utf-8'))
        review = json.loads((Path(project) / '.reviews/design-review.json').read_text(encoding='utf-8'))
        from harness_review import review_record_errors
        if approval.get('status') not in {'APPROVED', 'DELEGATED'} or not approval.get('user_signal'):
            return ['LANDING_APPROVAL_REQUIRED: proposal needs user adjustment or approval']
        if approval.get('review_id') != review.get('response_id') or approval.get('inputs') != review.get('inputs') or review_record_errors(Path(project), 'design-review'):
            return ['LANDING_APPROVAL_STALE: the approved proposal changed']
    except (OSError, ValueError, TypeError):
        return ['LANDING_APPROVAL_REQUIRED: invalid approval receipt']
    return []


def record_design_approval(project: Path, status: str, signal: str) -> dict:
    if status not in {'APPROVED', 'DELEGATED', 'ADJUST'} or not signal.strip():
        raise ValueError('Provide an approval status and the actual user signal')
    from harness_review import review_record_errors
    errors = blueprint_errors(project) + review_record_errors(project, 'design-review')
    if errors:
        raise ValueError('; '.join(errors))
    review = json.loads((project / '.reviews/design-review.json').read_text(encoding='utf-8'))
    result = {'status':status, 'user_signal':signal.strip(), 'review_id':review['response_id'], 'inputs':review['inputs']}
    target = project / '.reviews/design-approval.json'
    if target.is_file():
        # Keep checkpoint history; no overwriting previous user signals.
        with (project / '.reviews/design-approval-history.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(target.read_text(encoding='utf-8').replace('\n', '') + '\n')
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'status':status, 'review_id':review['response_id']}
