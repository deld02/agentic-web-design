#!/usr/bin/env python3
"""Validate narrow user-authored waivers against immutable harness input."""

from __future__ import annotations

import json
from pathlib import Path
import re


def record_master_confirmation(artifact: Path, status: str, user_signal: str) -> dict[str, str]:
    """Update only the bounded artistic-master checkpoint fields."""
    normalized = status.strip().upper()
    if normalized not in {"APPROVED", "DELEGATED", "ADJUST"}:
        raise ValueError("master status must be APPROVED, DELEGATED or ADJUST")
    signal = " ".join(user_signal.split())
    if not signal:
        raise ValueError("master confirmation needs the user's actual signal")
    if not artifact.is_file():
        raise ValueError("creative-direction.md is missing")
    text = artifact.read_text(encoding="utf-8")
    heading = "## Artistic master confirmation"
    if heading not in text:
        raise ValueError("artistic master confirmation section is missing")
    before, section = text.split(heading, 1)
    section = re.sub(r"(?m)^STATUS:\s*.*$", f"STATUS: {normalized}", section, count=1)
    section = re.sub(r"(?m)^USER_SIGNAL:\s*.*$", f"USER_SIGNAL: {signal}", section, count=1)
    artifact.write_text(before + heading + section, encoding="utf-8")
    return {"status": normalized, "user_signal": signal}


def _marker(path: Path, name: str) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"(?m)^\s*{re.escape(name)}:\s*(.+?)\s*$", text)
    return match.group(1).strip().strip("`\"'") if match else ""


def _normal(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def _immutable_brief(project_dir: Path) -> str:
    scenario = project_dir.resolve().parent / "scenario.json"
    if not scenario.is_file():
        return ""
    try:
        data = json.loads(scenario.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    return data.get("brief", "") if isinstance(data.get("brief"), str) else ""


def _authorized_quote(project_dir: Path, marker: str) -> str:
    brief_quote = _marker(project_dir / "brief.md", marker)
    plan_quote = _marker(project_dir / "production-plan.md", marker)
    immutable = _immutable_brief(project_dir)
    if not brief_quote or _normal(brief_quote) != _normal(plan_quote) or not immutable:
        return ""
    return brief_quote if _normal(brief_quote) in _normal(immutable) else ""


def explicit_text_only_authorized(project_dir: Path) -> bool:
    """True only for an exact user quote that rejects imagery as a whole."""
    quote = _authorized_quote(Path(project_dir), "USER_EXPLICIT_TEXT_ONLY")
    if not quote:
        return False
    if re.search(
        r"(?i)\b(ai|ia|generated?|generad[ao]s?|stock|magnific|midjourney|dall[- ]?e|provider|tool|herramienta)\b",
        quote,
    ):
        return False
    return bool(re.search(
        r"(?i)\b(text[ -]?only|solo texto|sin (?:ninguna )?(?:imagen(?:es)?|fotograf[ií]a(?:s)?|media)|without (?:any )?(?:images?|imagery|photos?|media)|no (?:images?|imagery|photos?))\b",
        quote,
    ))


def explicit_static_only_authorized(project_dir: Path) -> bool:
    """True only for an exact user quote that rejects all animation/motion."""
    quote = _authorized_quote(Path(project_dir), "USER_EXPLICIT_STATIC_ONLY")
    return bool(quote and re.search(
        r"(?i)\b(static[ -]?only|solo est[aá]tic[ao]|sin animaci(?:o|ó)n(?:es)?|sin movimiento|without (?:any )?(?:animation|motion)|no (?:animation|motion))\b",
        quote,
    ))
