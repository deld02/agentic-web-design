#!/usr/bin/env python3
"""Deterministic checks for the user-facing final landing handoff."""

from __future__ import annotations

from pathlib import Path, PurePosixPath
import re
import zipfile


FIELDS = (
    "DELIVERY_STATUS", "LANDING_ENTRY", "RUN_COMMAND", "BUILD_COMMAND",
    "PREVIEW_TARGET", "DELIVERY_PACKAGE", "ASSET_COMPLETENESS",
    "LIMITATIONS", "HANDOFF_SUMMARY",
)
FORBIDDEN_PARTS = {
    ".git", ".harness", "__pycache__", "node_modules", "tests", "audit", "audits",
}
PLACEHOLDER = re.compile(r"(?:<[^>]+>|\b(?:pending|todo|tbd|undetermined)\b)", re.I)


def _field(text: str, name: str) -> str:
    match = re.search(rf"(?m)^{re.escape(name)}:\s*(.*?)\s*$", text)
    return match.group(1).strip() if match else ""


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _unsafe_parts(parts: tuple[str, ...] | list[str]) -> set[str]:
    lowered = {part.lower() for part in parts}
    bad = lowered & FORBIDDEN_PARTS
    if any(part.endswith(".pyc") for part in lowered):
        bad.add("*.pyc")
    return bad


def final_delivery_contract_errors(
    qa_text: str, repository_root: Path, implementation_root: Path
) -> list[str]:
    """Validate the final contract and its physical package."""
    errors: list[str] = []
    values = {name: _field(qa_text, name) for name in FIELDS}
    for name, value in values.items():
        if not value or PLACEHOLDER.search(value):
            errors.append(f"final delivery contract missing substantive {name}")
    if errors:
        return errors

    status = values["DELIVERY_STATUS"]
    if status not in {"READY", "READY_WITH_LIMITATIONS", "NOT_READY"}:
        errors.append("final delivery DELIVERY_STATUS is invalid")
    elif status == "NOT_READY":
        errors.append("final delivery is NOT_READY")
    if values["ASSET_COMPLETENESS"] != "COMPLETE":
        errors.append("final delivery ASSET_COMPLETENESS must be COMPLETE")
    limitations = values["LIMITATIONS"]
    if status == "READY" and limitations.upper() != "NONE":
        errors.append("READY delivery must declare LIMITATIONS: NONE")
    if status == "READY_WITH_LIMITATIONS" and limitations.upper() == "NONE":
        errors.append("READY_WITH_LIMITATIONS requires an explicit limitation")
    if len(values["HANDOFF_SUMMARY"].split()) < 6:
        errors.append("final delivery HANDOFF_SUMMARY is too vague")
    if values["BUILD_COMMAND"].upper() == "NOT_REQUIRED":
        pass
    elif len(values["BUILD_COMMAND"].split()) < 2:
        errors.append("final delivery BUILD_COMMAND is not executable guidance")
    if len(values["RUN_COMMAND"].split()) < 2:
        errors.append("final delivery RUN_COMMAND is not executable guidance")

    implementation_root = implementation_root.resolve()
    entry_rel = Path(values["LANDING_ENTRY"])
    entry = (implementation_root / entry_rel).resolve()
    if entry_rel.is_absolute() or not _inside(entry, implementation_root) or not entry.is_file():
        errors.append("final delivery LANDING_ENTRY is not a real file inside implementation_root")

    preview_value = values["PREVIEW_TARGET"]
    if not re.match(r"https?://", preview_value, re.I):
        preview = Path(preview_value)
        if not preview.is_absolute():
            preview = repository_root / preview
        if not preview.resolve().exists():
            errors.append("final delivery PREVIEW_TARGET does not exist")

    package = Path(values["DELIVERY_PACKAGE"])
    if not package.is_absolute():
        package = repository_root / package
    package = package.resolve()
    if not package.exists():
        errors.append("final delivery DELIVERY_PACKAGE does not exist")
    elif package.is_dir():
        if not (package / entry_rel).is_file():
            errors.append("delivery folder does not contain LANDING_ENTRY")
        bad: set[str] = set()
        for item in package.rglob("*"):
            bad.update(_unsafe_parts(item.relative_to(package).parts))
        if bad:
            errors.append("delivery folder contains internal/generated material: " + ", ".join(sorted(bad)))
    elif package.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(package) as archive:
                names = [PurePosixPath(name) for name in archive.namelist()]
                wanted = PurePosixPath(entry_rel.as_posix())
                if not any(name == wanted or name.parts[-len(wanted.parts):] == wanted.parts for name in names):
                    errors.append("delivery ZIP does not contain LANDING_ENTRY")
                bad = set().union(*(_unsafe_parts(list(name.parts)) for name in names)) if names else set()
                if bad:
                    errors.append("delivery ZIP contains internal/generated material: " + ", ".join(sorted(bad)))
        except zipfile.BadZipFile:
            errors.append("final delivery DELIVERY_PACKAGE is not a valid ZIP")
    else:
        errors.append("final delivery DELIVERY_PACKAGE must be a folder or ZIP")
    return errors
