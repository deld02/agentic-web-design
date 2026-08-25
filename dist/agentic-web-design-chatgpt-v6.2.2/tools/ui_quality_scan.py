#!/usr/bin/env python3
"""Deterministic code checks for observable UI defects and AI-template signals.

The scanner never scores beauty. Critical defects may block; aesthetic signals
remain advisory evidence for agent 07.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SOURCE_SUFFIXES = {".html", ".css", ".js", ".jsx", ".ts", ".tsx", ".astro", ".vue", ".svelte"}


def _finding(rule: str, severity: str, path: Path, line: int, message: str) -> dict[str, Any]:
    return {"rule": rule, "severity": severity, "file": str(path), "line": line, "message": message}


def scan_implementation(root: Path) -> dict[str, Any]:
    root = root.resolve()
    findings: list[dict[str, Any]] = []
    files = sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES)
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = path.relative_to(root)
        lowered = text.casefold()
        focus_replacement = ":focus-visible" in lowered
        for number, line in enumerate(text.splitlines(), 1):
            low = line.casefold()
            if re.search(r"\btransition\s*:\s*all\b", low):
                findings.append(_finding("TRANSITION_ALL", "ADVISORY", relative, number, "transition: all obscures intent and can animate costly properties"))
            if re.search(r"outline\s*:\s*(?:none|0)\b", low) and not focus_replacement:
                findings.append(_finding("FOCUS_REMOVED", "CRITICAL", relative, number, "focus outline is removed without a visible :focus-visible replacement"))
            if re.search(r"(?:bounce|elastic)\b", low) and any(token in low for token in ("ease", "easing", "animation", "transition")):
                findings.append(_finding("BOUNCE_EASING", "ADVISORY", relative, number, "bounce/elastic easing is a common generic delight substitute; verify project meaning"))
            if "todo" in low or "lorem ipsum" in low or "john doe" in low:
                findings.append(_finding("PLACEHOLDER_CONTENT", "CRITICAL", relative, number, "placeholder content remains in implementation"))
        if path.suffix.lower() in {".html", ".astro", ".vue", ".svelte", ".jsx", ".tsx"}:
            for match in re.finditer(r"<img\b([^>]*)>", text, re.I | re.S):
                attrs = match.group(1)
                line = text.count("\n", 0, match.start()) + 1
                if not re.search(r"\balt\s*=", attrs, re.I):
                    findings.append(_finding("IMG_ALT", "CRITICAL", relative, line, "image has no alt attribute"))
                if not (re.search(r"\bwidth\s*=", attrs, re.I) and re.search(r"\bheight\s*=", attrs, re.I)):
                    findings.append(_finding("IMG_DIMENSIONS", "ADVISORY", relative, line, "image lacks intrinsic width/height and may cause layout shift"))
        color_literals = re.findall(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(", text)
        if len(color_literals) >= 8 and "var(--" not in text:
            findings.append(_finding("TOKEN_DISCIPLINE", "ADVISORY", relative, 1, "many literal colors are used without visible custom-property token discipline"))
    return {
        "root": str(root),
        "files_scanned": len(files),
        "status": "FAIL" if any(item["severity"] == "CRITICAL" for item in findings) else "PASS",
        "findings": findings,
        "boundary": "deterministic code evidence only; visual quality remains agent-07 judgment",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = scan_implementation(args.root)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
