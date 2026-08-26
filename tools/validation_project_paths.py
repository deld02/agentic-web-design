#!/usr/bin/env python3
"""Resolve implementation paths consistently in repository and isolated harness projects."""

from pathlib import Path


def implementation_root_for(project_dir: Path, repository_root: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate.resolve()
    project_dir = project_dir.resolve()
    try:
        project_dir.relative_to((repository_root / "projects").resolve())
        base = repository_root
    except ValueError:
        base = project_dir
    return (base / candidate).resolve()
