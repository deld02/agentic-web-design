#!/usr/bin/env python3
"""Dependency-free parsing and media helpers shared by validators."""

from __future__ import annotations

import json
import re
from pathlib import Path


def load_json(path: Path) -> dict:
    """Read a UTF-8 JSON object from *path*."""
    return json.loads(path.read_text(encoding="utf-8"))


def section(text: str, heading: str) -> str:
    """Return the Markdown body immediately below an exact heading."""
    match = re.search(
        rf"(?ms)^{re.escape(heading)}\s*$\n(.*?)(?=^#{{1,6}}\s|\Z)", text
    )
    return match.group(1).strip() if match else ""


def table_rows(text: str, heading: str, _header_token: str = "") -> list[list[str]]:
    """Return data cells from the first Markdown table under *heading*."""
    rows: list[list[str]] = []
    header_skipped = False
    for line in section(text, heading).splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not header_skipped:
            header_skipped = True
            continue
        rows.append(cells)
    return rows


def valid_signature(path: Path) -> bool:
    """Perform a cheap signature check for media accepted by delivery validators."""
    data = path.read_bytes()
    if not data:
        return False
    suffix = path.suffix.lower()
    if suffix == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix in {".jpg", ".jpeg"}:
        return data.startswith(b"\xff\xd8\xff")
    if suffix == ".gif":
        return data.startswith((b"GIF87a", b"GIF89a"))
    if suffix == ".webp":
        return len(data) > 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    if suffix == ".avif":
        return len(data) > 12 and b"ftypavif" in data[:32]
    if suffix == ".svg":
        return b"<svg" in data[:4096].lower()
    if suffix == ".glb":
        return data.startswith(b"glTF")
    if suffix == ".gltf":
        return data.lstrip().startswith(b"{")
    return len(data) >= 32
