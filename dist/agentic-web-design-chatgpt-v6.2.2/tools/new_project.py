#!/usr/bin/env python3
from pathlib import Path
import json, re, shutil, sys

ROOT = Path(__file__).resolve().parents[1]

if len(sys.argv) != 2:
    raise SystemExit('Usage: python tools/new_project.py <project-slug>')

slug = sys.argv[1].strip().lower().replace(' ', '-')
if not re.fullmatch(r'[a-z0-9][a-z0-9.-]*', slug):
    raise SystemExit('Invalid slug. Use lowercase letters, numbers, dots and hyphens.')

src = ROOT / 'templates' / 'project'
dst = ROOT / 'projects' / slug
if dst.exists():
    raise SystemExit(f'Project already exists: {dst}')

PROJECT_FILES = [
    'PROJECT.md', 'project.config.json', 'status.json', 'brief.md',
    'research-strategy.md', 'content-architecture.md', 'creative-direction.md',
    'visual-system.md', 'production-plan.md', 'technology-decision.md',
    'qa-release.md', 'decision-log.md'
]

dst.mkdir(parents=True)
for rel in PROJECT_FILES:
    source = src / rel
    if not source.is_file():
        raise SystemExit(f'Missing project template: {rel}')
    shutil.copy2(source, dst / rel)

# Replace template marker in textual project files.
for path in dst.rglob('*'):
    if path.is_file() and path.suffix in {'.md', '.json', '.txt'}:
        text = path.read_text(encoding='utf-8')
        path.write_text(text.replace('replace-me', slug), encoding='utf-8')

status_path = dst / 'status.json'
data = json.loads(status_path.read_text(encoding='utf-8'))
data['project'] = slug
status_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

print(f'Created {dst.relative_to(ROOT)}')
