#!/usr/bin/env python3
"""Architecture ratchets for the dependency-free Python tooling."""

from __future__ import annotations

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _config(name: str) -> dict:
    return json.loads((ROOT / "config" / name).read_text(encoding="utf-8"))


def _tree(relative: str) -> ast.Module:
    path = ROOT / relative
    return ast.parse(path.read_text(encoding="utf-8"), filename=relative)


def quality_errors() -> list[str]:
    """Return deterministic source-organization violations."""
    config = _config("code-quality.json")
    errors: list[str] = []
    definitions: dict[str, list[str]] = defaultdict(list)
    python_files = sorted((ROOT / "tools").glob("*.py"))

    for path in python_files:
        relative = path.relative_to(ROOT).as_posix()
        tree = _tree(relative)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                definitions[node.name].append(relative)

    for name in config["unique_function_definitions"]:
        owners = definitions.get(name, [])
        if owners != ["tools/validation_common.py"]:
            errors.append(f"{name} must be defined only in tools/validation_common.py; found {owners}")

    for relative, limit in config["module_line_budgets"].items():
        count = len((ROOT / relative).read_text(encoding="utf-8").splitlines())
        if count > limit:
            errors.append(f"{relative} has {count} lines; ratchet is {limit}")

    for relative, limit in config["function_line_budgets"].items():
        for node in ast.walk(_tree(relative)):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            size = (node.end_lineno or node.lineno) - node.lineno + 1
            if size > limit:
                errors.append(f"{relative}:{node.lineno} {node.name} has {size} lines; ratchet is {limit}")

    for relative, forbidden_module in config["forbidden_import_edges"]:
        for node in ast.walk(_tree(relative)):
            imported: list[str] = []
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported = [node.module]
            if forbidden_module in imported:
                errors.append(f"{relative} must not import {forbidden_module}")

    runtime = _config("runtime-files.json")
    keys = ("top_level", "trees", "tool_files", "required_runtime_files", "pack_exclude")
    for key in keys:
        values = runtime.get(key, [])
        if not isinstance(values, list) or not values:
            errors.append(f"runtime-files.json {key} must be a non-empty list")
        elif len(values) != len(set(values)):
            errors.append(f"runtime-files.json {key} contains duplicates")
    for relative in runtime.get("top_level", []) + runtime.get("required_runtime_files", []):
        if not (ROOT / relative).is_file():
            errors.append(f"runtime file is missing: {relative}")
    for relative in runtime.get("trees", []):
        if not (ROOT / relative).is_dir():
            errors.append(f"runtime tree is missing: {relative}")
    for name in runtime.get("tool_files", []):
        if not (ROOT / "tools" / name).is_file():
            errors.append(f"runtime tool is missing: tools/{name}")
    for relative in runtime.get("pack_exclude", []):
        if not (ROOT / relative).is_file():
            errors.append(f"pack exclusion is missing: {relative}")
    maintenance_files = (
        "CHANGELOG.md",
        "DECISIONS.md",
        "config/code-quality.json",
        "config/pack-safety.json",
        "docs/maintenance/README.md",
        "tools/build_chatgpt_pack.py",
        "tools/code_quality.py",
    )
    for relative in maintenance_files:
        if not (ROOT / relative).is_file():
            errors.append(f"maintenance file is missing: {relative}")
    return errors


def main() -> int:
    errors = quality_errors()
    if errors:
        print("CODE QUALITY FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CODE QUALITY OK — ownership, dependency and size ratchets pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
