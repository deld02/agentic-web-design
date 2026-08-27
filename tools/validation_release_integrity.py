#!/usr/bin/env python3
"""Release integrity, content-lock and runtime-traversal validation."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json
import re

from validation_common import table_rows, valid_signature


ARTIFACTS = (
    "content-architecture.md", "creative-direction.md", "visual-system.md",
    "production-plan.md", "technology-decision.md",
)
SOURCE_SUFFIXES = {
    ".html", ".css", ".scss", ".sass", ".js", ".mjs", ".cjs", ".ts",
    ".tsx", ".jsx", ".astro", ".vue", ".svelte", ".json", ".md",
}
IGNORED_DIRS = {".git", "node_modules", ".next", ".astro", "__pycache__"}
CONTENT_ROLES = {"HERO_THESIS", "PRIMARY_CTA", "NAVIGATION", "CLAIM", "PROOF", "BODY", "LEGAL"}
PLACEHOLDERS = {"", "tbd", "todo", "pending", "undetermined", "placeholder"}


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _field(text: str, name: str) -> str:
    match = re.search(rf"(?m)^{re.escape(name)}:\s*(.*?)\s*$", text)
    return match.group(1).strip() if match else ""


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _implementation_files(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*")
        if path.is_file() and not any(part in IGNORED_DIRS for part in path.relative_to(root).parts)
    )


def implementation_digest(root: Path) -> str:
    digest = sha256()
    for path in _implementation_files(root):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8") + b"\0" + _sha(path).encode("ascii") + b"\n")
    return digest.hexdigest()


def _source_corpus(root: Path) -> str:
    chunks: list[str] = []
    for path in _implementation_files(root):
        if path.suffix.lower() in SOURCE_SUFFIXES:
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    return re.sub(r"\s+", " ", "\n".join(chunks)).casefold()


def content_lock_definition_errors(project_dir: Path) -> list[str]:
    text = (project_dir / "content-architecture.md").read_text(encoding="utf-8")
    rows = table_rows(text, "## Content lock", "Content ID")
    errors: list[str] = []
    seen: set[str] = set()
    roles: set[str] = set()
    if not rows:
        return ["G1 requires a content lock with final hero thesis and primary CTA"]
    for row in rows:
        if len(row) < 5 or any(cell.strip().casefold() in PLACEHOLDERS for cell in row[:5]):
            errors.append("G1 content lock contains an incomplete row")
            continue
        content_id, role, exact_text, requirement, _use = row[:5]
        if not re.fullmatch(r"CNT-[0-9]{3,}", content_id):
            errors.append(f"G1 invalid content-lock ID: {content_id or '<empty>'}")
        if content_id in seen:
            errors.append(f"G1 duplicate content-lock ID: {content_id}")
        seen.add(content_id)
        if role not in CONTENT_ROLES:
            errors.append(f"G1 {content_id} has invalid content-lock role")
        else:
            roles.add(role)
        if requirement not in {"REQUIRED", "OPTIONAL", "OMIT"}:
            errors.append(f"G1 {content_id} has invalid build requirement")
        if len(exact_text.split()) < 2:
            errors.append(f"G1 {content_id} exact approved text is too vague")
    for role in ("HERO_THESIS", "PRIMARY_CTA"):
        if role not in roles:
            errors.append(f"G1 content lock missing {role}")
    return errors


def content_lock_build_errors(project_dir: Path, implementation_root: Path) -> list[str]:
    errors = content_lock_definition_errors(project_dir)
    if not implementation_root.is_dir():
        return errors + ["content lock cannot inspect missing implementation root"]
    text = (project_dir / "content-architecture.md").read_text(encoding="utf-8")
    rows = table_rows(text, "## Content lock", "Content ID")
    corpus = _source_corpus(implementation_root)
    for row in rows:
        if len(row) < 5:
            continue
        content_id, _role, exact_text, requirement, _use = row[:5]
        present = re.sub(r"\s+", " ", exact_text).casefold() in corpus
        if requirement == "REQUIRED" and not present:
            errors.append(f"G4 content lock {content_id} is absent from implementation source")
        if requirement == "OMIT" and present:
            errors.append(f"G4 content lock {content_id} was marked OMIT but appears in implementation source")
    return errors


def runtime_traversal_errors(project_dir: Path, implementation_root: Path | None = None) -> list[str]:
    qa_path = project_dir / "qa-release.md"
    qa = qa_path.read_text(encoding="utf-8") if qa_path.is_file() else ""
    content = (project_dir / "content-architecture.md").read_text(encoding="utf-8")
    expected = {
        row[0] for row in table_rows(content, "## Sitemap / page or section outline", "Scene ID")
        if len(row) >= 5 and re.fullmatch(r"SCN-[0-9]{3,}", row[0])
    }
    rows = table_rows(qa, "### Runtime traversal", "Scene ID")
    errors: list[str] = []
    covered: set[tuple[str, str]] = set()
    evidence_paths: set[str] = set()
    current_digest = implementation_digest(implementation_root) if implementation_root and implementation_root.is_dir() else None
    for row in rows:
        if len(row) < 8 or not all(row[:8]):
            errors.append("G4 runtime traversal contains an incomplete row")
            continue
        scene_id, viewport, trigger, expected_state, observed, evidence, verdict, source_digest = row[:8]
        if scene_id not in expected:
            errors.append(f"G4 runtime traversal has unknown scene {scene_id}")
        if viewport not in {"DESKTOP", "MOBILE"}:
            errors.append(f"G4 runtime traversal {scene_id} has invalid viewport")
        if verdict != "PASS":
            errors.append(f"G4 runtime traversal {scene_id}/{viewport} is not PASS")
        if min(len(trigger), len(expected_state), len(observed)) < 8:
            errors.append(f"G4 runtime traversal {scene_id}/{viewport} lacks behavioral detail")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", source_digest):
            errors.append(f"G4 runtime traversal {scene_id}/{viewport} lacks source SHA-256")
        elif current_digest and source_digest != f"sha256:{current_digest}":
            errors.append(f"G4 runtime traversal {scene_id}/{viewport} was captured from a stale implementation")
        candidate = (project_dir / evidence).resolve()
        if not _inside(candidate, project_dir.resolve()) or not candidate.is_file() or not valid_signature(candidate):
            errors.append(f"G4 runtime traversal evidence is missing or invalid: {evidence}")
        if evidence in evidence_paths:
            errors.append(f"G4 runtime traversal reuses evidence file: {evidence}")
        evidence_paths.add(evidence)
        covered.add((scene_id, viewport))
    for scene_id in sorted(expected):
        for viewport in ("DESKTOP", "MOBILE"):
            if (scene_id, viewport) not in covered:
                errors.append(f"G4 runtime traversal missing {scene_id}/{viewport}")
    return errors


def manifest_path(project_dir: Path) -> Path:
    qa_path = project_dir / "qa-release.md"
    qa = qa_path.read_text(encoding="utf-8") if qa_path.is_file() else ""
    value = _field(qa, "RELEASE_INTEGRITY_MANIFEST")
    return (project_dir / value).resolve() if value else project_dir / "evidence/release-integrity.json"


def write_manifest(project_dir: Path, implementation_root: Path) -> Path:
    project_dir = project_dir.resolve()
    implementation_root = implementation_root.resolve()
    path = manifest_path(project_dir)
    if not _inside(path, project_dir):
        raise ValueError("release integrity manifest must be inside project evidence")
    runtime_rows = table_rows(
        (project_dir / "qa-release.md").read_text(encoding="utf-8"),
        "### Runtime traversal", "Scene ID",
    )
    evidence: dict[str, str] = {}
    for row in runtime_rows:
        if len(row) >= 6:
            candidate = (project_dir / row[5]).resolve()
            if _inside(candidate, project_dir) and candidate.is_file():
                evidence[row[5]] = _sha(candidate)
    payload = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "implementation_sha256": implementation_digest(implementation_root),
        "artifacts": {name: _sha(project_dir / name) for name in ARTIFACTS},
        "runtime_evidence": evidence,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def integrity_manifest_errors(project_dir: Path, implementation_root: Path) -> list[str]:
    project_dir = project_dir.resolve()
    path = manifest_path(project_dir)
    if not _inside(path, project_dir) or not path.is_file():
        return ["G4 release integrity manifest is missing inside project evidence"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ["G4 release integrity manifest is invalid JSON"]
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("G4 release integrity manifest has unknown schema")
    if not implementation_root.is_dir() or data.get("implementation_sha256") != implementation_digest(implementation_root):
        errors.append("G4 implementation changed after runtime evidence/review snapshot")
    recorded = data.get("artifacts", {})
    for name in ARTIFACTS:
        target = project_dir / name
        if not target.is_file() or recorded.get(name) != _sha(target):
            errors.append(f"G4 {name} changed after release integrity snapshot")
    evidence = data.get("runtime_evidence", {})
    for reference, digest in evidence.items():
        target = (project_dir / reference).resolve()
        if not _inside(target, project_dir) or not target.is_file() or digest != _sha(target):
            errors.append(f"G4 runtime evidence changed after snapshot: {reference}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a release-integrity snapshot after final runtime evidence.")
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--implementation-root", required=True, type=Path)
    args = parser.parse_args()
    path = write_manifest(args.project_dir, args.implementation_root)
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
