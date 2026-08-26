#!/usr/bin/env python3
from pathlib import Path
import argparse, re, sys

from validation_common import section, valid_signature

SUPPORTED = {'.png', '.jpg', '.jpeg', '.webp', '.avif', '.gif', '.svg', '.mp4', '.webm', '.glb', '.gltf'}
SOURCE_SUFFIXES = {'.html', '.css', '.scss', '.sass', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.astro', '.vue', '.svelte'}
IGNORED_DIRS = {'.git', 'node_modules', '.next', '.astro', '__pycache__'}
CAPTURE_MARKERS = ('screenshot', 'full-page', 'fullpage', 'desktop-full', 'mobile-full', 'page-capture')
MEDIA_METHODS = {'KEEP_OR_EDIT', 'EXTERNAL_IMAGE_LOOP', 'ORIGINAL_PHOTO', 'LICENSED_SOURCE', 'CUSTOM_ILLUSTRATION', '3D_RENDER', 'VIDEO_RENDER', 'SVG_OR_CSS'}
DELIVERED_MEDIA = {'FLAT_2D', 'LAYERED_2D', 'RENDERED_3D', 'INTERACTIVE_3D'}
REAL_3D_MEDIA = {'RENDERED_3D', 'INTERACTIVE_3D'}


def inventory(text):
    rows = []
    for line in section(text, '## Asset inventory and readiness').splitlines():
        if not line.startswith('|') or '---' in line or re.search(r'\|\s*ID\s*\|', line):
            continue
        cells = [cell.strip().strip('`') for cell in line.strip().strip('|').split('|')]
        if len(cells) >= 6 and re.fullmatch(r'IMG-[0-9]{3,}', cells[0]):
            rows.append(cells[:6])
    return rows


def effect_inventory(text):
    rows = []
    for line in section(text, '### Material effect decisions').splitlines():
        if not line.startswith('|') or '---' in line or re.search(r'\|\s*Effect ID / scene\s*\|', line):
            continue
        cells = [cell.strip().strip('`') for cell in line.strip().strip('|').split('|')]
        if len(cells) >= 10 and re.search(r'FX-[0-9]{3,}', cells[0]):
            rows.append(cells)
    return rows


def three_d_inventory(text):
    rows = []
    for line in section(text, '### 3D production provenance').splitlines():
        if not line.startswith('|') or '---' in line or re.search(r'\|\s*FX ID\s*\|', line):
            continue
        cells = [cell.strip().strip('`') for cell in line.strip().strip('|').split('|')]
        if len(cells) >= 7 and re.fullmatch(r'FX-[0-9]{3,}', cells[0]):
            rows.append(cells[:7])
    return rows


def implementation_sources(root):
    for path in root.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        yield path


def resolve_asset(reference, implementation_root):
    candidate = Path(reference)
    if candidate.is_absolute():
        return candidate.resolve()
    return (implementation_root / candidate).resolve()


def composition_asset_names(project_dir):
    names = set()
    creative = project_dir / 'creative-direction.md'
    if creative.is_file():
        for line in section(creative.read_text(encoding='utf-8'), '## Artistic master').splitlines():
            if not line.startswith('|') or '---' in line or re.search(r'\|\s*Evidence ID\s*\|', line):
                continue
            cells = [cell.strip().strip('`') for cell in line.strip().strip('|').split('|')]
            if len(cells) >= 4 and re.fullmatch(r'AM-[0-9]{3,}', cells[0]) and cells[3]:
                names.add(Path(cells[3]).name.lower())
    visual = project_dir / 'visual-system.md'
    if visual.is_file():
        for line in section(visual.read_text(encoding='utf-8'), '### Scene visual opportunities').splitlines():
            if not line.startswith('|') or '---' in line or re.search(r'\|\s*Scene\s*\|', line):
                continue
            cells = [cell.strip().strip('`') for cell in line.strip().strip('|').split('|')]
            for value in cells[4:6]:
                match = re.fullmatch(r'CMP-[0-9]{3,}:(.+)', value) if value else None
                if match:
                    names.add(Path(match.group(1).strip()).name.lower())
    return names


def validate_delivery(project_dir, implementation_root):
    project_dir = Path(project_dir).resolve()
    implementation_root = Path(implementation_root).resolve()
    errors = []
    plan = project_dir / 'production-plan.md'

    if not project_dir.is_dir(): errors.append(f'project directory does not exist: {project_dir}')
    if not implementation_root.is_dir(): errors.append(f'implementation root does not exist: {implementation_root}')
    if not plan.is_file(): errors.append(f'missing production plan: {plan}')
    if errors: return errors, 0

    text = plan.read_text(encoding='utf-8')
    if re.search(r'(?m)^\s*USER_EXPLICIT_TEXT_ONLY:\s*\S.+$', text):
        brief = project_dir / 'brief.md'
        if not brief.is_file() or not re.search(r'(?m)^\s*USER_EXPLICIT_TEXT_ONLY:\s*\S.+$', brief.read_text(encoding='utf-8')):
            errors.append('text-only exception must also be recorded in brief.md as explicit user authority')
        rows = []
    else:
        rows = [row for row in inventory(text) if row[4] == 'FINAL']
        if not rows:
            errors.append('production plan has no FINAL IMG asset')

    primary_rows = []
    for row in rows:
        role_method = row[3]
        match = re.fullmatch(r'(PRIMARY|SUPPORTING):([A-Z0-9_]+)', role_method)
        if not match or match.group(2) not in MEDIA_METHODS:
            errors.append(f'{row[0]}: invalid payload role/method {role_method or "<empty>"}')
            continue
        if match.group(1) == 'PRIMARY':
            primary_rows.append(row)
    if rows and not primary_rows:
        errors.append('production plan has no FINAL PRIMARY scene-bearing visual; supporting assets do not satisfy the requirement')
    if primary_rows and all(Path(row[5]).suffix.lower() == '.svg' for row in primary_rows):
        errors.append('SVG/vector cannot be the only PRIMARY visual; provide a scene-bearing raster, video or 3D asset')

    sources = list(implementation_sources(implementation_root))
    cmp_names = composition_asset_names(project_dir)
    source_text = []
    for source in sources:
        try: source_text.append((source, source.read_text(encoding='utf-8', errors='ignore')))
        except OSError: pass

    for image_id, _scene, _representation, _role_method, _status, reference in rows:
        if not reference or reference.upper() in {'TBD', 'NONE', 'N/A', 'PLACEHOLDER'}:
            errors.append(f'{image_id}: missing usable final file')
            continue
        asset = resolve_asset(reference, implementation_root)
        try: asset.relative_to(implementation_root)
        except ValueError:
            errors.append(f'{image_id}: final asset must be inside implementation root: {reference}')
            continue
        lowered = asset.name.lower()
        if re.search(r'(?i)(?:^|[-_])cmp[-_]?[0-9]{3,}', lowered) or lowered in cmp_names or re.search(r'CMP-[0-9]{3,}', reference, re.I):
            errors.append(f'{image_id}: CMP design evidence cannot be shipped as a FINAL landing asset: {reference}')
        if any(marker in lowered for marker in CAPTURE_MARKERS):
            errors.append(f'{image_id}: QA/full-page capture cannot be a landing asset: {asset.name}')
        if asset.suffix.lower() not in SUPPORTED:
            errors.append(f'{image_id}: unsupported final visual format: {asset.suffix or "<none>"}')
        if not asset.is_file():
            errors.append(f'{image_id}: final asset does not exist: {reference}')
            continue
        if not valid_signature(asset):
            errors.append(f'{image_id}: file is empty or does not match a valid visual format: {reference}')
        needles = {reference.replace('\\', '/'), asset.name}
        if not any(any(needle in body.replace('\\', '/') for needle in needles) for _source, body in source_text):
            errors.append(f'{image_id}: asset exists but is not referenced by implementation source: {reference}')

    effects = [row for row in effect_inventory(text) if row[9] in {'FINAL', 'STATIC_WINNER_REVIEWED'}]
    if not effects:
        errors.append('production plan has no delivered FX mechanism')
    for row in effects:
        effect_id, status = row[0], row[9]
        proof = row[10] if len(row) >= 11 else ''
        medium = row[11] if len(row) >= 12 else ''
        if medium not in DELIVERED_MEDIA:
            errors.append(f'{effect_id}: delivered medium must be one of {sorted(DELIVERED_MEDIA)}')
        if status == 'STATIC_WINNER_REVIEWED':
            if not proof.startswith('STATIC:') or not proof.removeprefix('STATIC:').strip():
                errors.append(f'{effect_id}: static winner lacks STATIC:<evidence> implementation proof')
            continue
        if not proof or '#' not in proof:
            errors.append(f'{effect_id}: FINAL mechanism needs source/file#marker implementation proof')
            continue
        reference, marker = (part.strip() for part in proof.split('#', 1))
        source = resolve_asset(reference, implementation_root)
        try: source.relative_to(implementation_root)
        except ValueError:
            errors.append(f'{effect_id}: effect source must be inside implementation root: {reference}')
            continue
        if source.suffix.lower() not in SOURCE_SUFFIXES or not source.is_file():
            errors.append(f'{effect_id}: effect implementation source does not exist: {reference}')
            continue
        body = source.read_text(encoding='utf-8', errors='ignore')
        if not marker or marker not in body:
            errors.append(f'{effect_id}: implementation marker not found in {reference}: {marker or "<empty>"}')

    provenance = {row[0]: row for row in three_d_inventory(text)}
    for row in effects:
        effect_id = re.search(r'FX-[0-9]{3,}', row[0]).group(0)
        medium = row[11] if len(row) >= 12 else ''
        if medium not in REAL_3D_MEDIA:
            continue
        detail = provenance.get(effect_id)
        if not detail:
            errors.append(f'{effect_id}: {medium} requires 3D production provenance')
            continue
        _fx_id, declared, source_tool, asset_runtime, rights, integration, fallback = detail
        if declared != medium:
            errors.append(f'{effect_id}: 3D provenance medium does not match delivered medium')
        if not source_tool or re.fullmatch(r'(?i)(css|svg|html|native|self[- ]?drawn)', source_tool):
            errors.append(f'{effect_id}: 3D needs an identified external source or authoring tool; CSS/SVG is not 3D')
        real_3d_signal = re.search(r'(?i)(three(?:\.js)?|spline|babylon|model-viewer|webgl|webgpu|blender|cinema ?4d|houdini|unreal|\.glb\b|\.gltf\b|\.blend\b)', asset_runtime)
        if not asset_runtime or not real_3d_signal:
            errors.append(f'{effect_id}: 3D needs a real model, scene, render tool or web runtime')
        if not rights or rights.upper() in {'TBD', 'UNKNOWN', 'NONE'}:
            errors.append(f'{effect_id}: 3D source needs explicit license or production rights')
        if not integration or '#' not in integration:
            errors.append(f'{effect_id}: 3D provenance needs source/file#marker integration proof')
        if not fallback or fallback.upper() in {'TBD', 'NONE'}:
            errors.append(f'{effect_id}: 3D needs a static or reduced-motion fallback')

    return errors, len(rows)


def main():
    parser = argparse.ArgumentParser(description='Verify physical visual assets and their implementation references.')
    parser.add_argument('--project-dir', required=True)
    parser.add_argument('--implementation-root', required=True)
    args = parser.parse_args()
    errors, count = validate_delivery(args.project_dir, args.implementation_root)
    if errors:
        print('DELIVERY VALIDATION FAILED')
        for error in errors: print('-', error)
        return 1
    print(f'DELIVERY PROOF OK — {count} FINAL visual asset(s) and the delivered mechanism proof are valid and integrated.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
