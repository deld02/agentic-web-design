#!/usr/bin/env python3
"""Build a clean, current-only runtime pack for ChatGPT Projects."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOP_LEVEL = (
    "AGENTS.md", "SYSTEM.md", "WORKFLOW.md", "QUALITY-GATES.md",
    "CHATGPT-PROJECT-INSTRUCTIONS.md", "README.md", "repo-manifest.json",
)
TREES = (
    "agents", "config", "governance", "harness", "schemas", "templates/project",
    "docs/architecture", "docs/methods", "docs/standards",
    "skills/agentic-web-design", "skills/web-design-capabilities",
)
TOOL_FILES = (
    "audit_agents.py", "audit_state.py", "audit_system.py", "design_capabilities.py",
    "evaluation_harness.py", "new_project.py", "project_validation.py",
    "ui_quality_scan.py", "validate_delivery.py", "validate_design_capabilities.py",
    "validate_gate.py", "validate_resource_registry.py", "validate_system.py",
)
FORBIDDEN = (
    "Design Resource Scout", "00 Orchestrator", "11 Design Critic",
    "12 Accessibility", "G14", "G13", "G12",
)


def _copy(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def build_pack(output_root: Path) -> tuple[Path, Path]:
    manifest = json.loads((ROOT / "repo-manifest.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    output_root.mkdir(parents=True, exist_ok=True)
    output_root = output_root.resolve()
    pack = (output_root / f"agentic-web-design-chatgpt-v{version}").resolve()
    try:
        pack.relative_to(output_root)
    except ValueError as exc:
        raise ValueError("pack target escaped output root") from exc
    if pack.exists():
        raise FileExistsError(f"pack already exists: {pack}")
    pack.mkdir()

    for relative in TOP_LEVEL:
        _copy(ROOT / relative, pack / relative)
    for relative in TREES:
        _copy(ROOT / relative, pack / relative)
    for name in TOOL_FILES:
        _copy(ROOT / "tools" / name, pack / "tools" / name)

    runtime = (
        f"# ChatGPT runtime — v{version}\n\n"
        "This is the current execution package, not the historical repository. "
        "The only roles are `00` through `07`; the only pipeline authority is `config/pipeline.json`.\n\n"
        "For a real project, first save the user brief and run:\n\n"
        "```text\npython tools/evaluation_harness.py chat-start --brief-file <brief>\n```\n\n"
        "Then complete only the returned stage and use `chat-next`. During `creative-master`, "
        "generate a real raster and register it with `chat-image` before advancing.\n\n"
        "Do not search for or reconstruct earlier architectures. This pack intentionally contains no historical audits, changelog or superseded decision log.\n"
    )
    (pack / "START-HERE.md").write_text(runtime, encoding="utf-8")

    forbidden_hits: list[str] = []
    files: list[dict[str, str]] = []
    for path in sorted(item for item in pack.rglob("*") if item.is_file()):
        relative = str(path.relative_to(pack)).replace("\\", "/")
        data = path.read_bytes()
        files.append({"path": relative, "sha256": hashlib.sha256(data).hexdigest()})
        if path.suffix.lower() in {".md", ".json", ".txt"}:
            text = data.decode("utf-8", errors="ignore")
            for token in FORBIDDEN:
                if token.lower() in text.lower():
                    forbidden_hits.append(f"{relative}: {token}")
    if forbidden_hits:
        raise ValueError("legacy architecture leaked into ChatGPT pack: " + "; ".join(forbidden_hits))
    (pack / "runtime-manifest.json").write_text(
        json.dumps({"system_version": version, "files": files}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    archive = output_root / f"agentic-web-design-chatgpt-v{version}.zip"
    if archive.exists():
        raise FileExistsError(f"archive already exists: {archive}")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(item for item in pack.rglob("*") if item.is_file()):
            bundle.write(path, Path(pack.name) / path.relative_to(pack))
    return pack, archive


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    try:
        pack, archive = build_pack(args.output)
    except (OSError, ValueError) as exc:
        print(f"CHATGPT PACK FAILED — {exc}")
        return 1
    print(pack)
    print(archive)
    return 0


if __name__ == "__main__":
    sys.exit(main())
