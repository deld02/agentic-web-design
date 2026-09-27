"""Physical handoff checks for custom Blender work, not aesthetic approval."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import struct

from validation_common import section, table_rows
from harness_media import inspect_raster


HEADING = "### 3D production provenance"


def blender_rows(text: str) -> list[list[str]]:
    return [row for row in table_rows(text, HEADING, "FX ID")
            if len(row) >= 3 and re.search(r"\bblender\b", row[2], re.I)
            and "EXISTING_ASSET" not in row[2]]


def _local_file(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError("expected project-relative path")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("file missing or outside project")
    return path


def blender_handoff_errors(project: Path) -> list[str]:
    project = Path(project)
    plan = project / "production-plan.md"
    text = plan.read_text(encoding="utf-8") if plan.is_file() else ""
    rows = blender_rows(text)
    if not rows:
        return []
    errors: list[str] = []
    match = re.search(r"(?m)^BLENDER_HANDOFF:[ \t]*([^\r\n]*)", section(text, HEADING))
    try:
        manifest = _local_file(project, match.group(1).strip().strip("`") if match else "")
        if manifest != (project / "evidence/blender/handoff.json").resolve():
            raise ValueError("use the server-owned Blender handoff, not a client-authored manifest")
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        assets = payload.get("assets") if isinstance(payload, dict) else None
        if not isinstance(assets, list) or not all(isinstance(a, dict) for a in assets):
            raise ValueError("assets must be a list of objects")
    except (ValueError, OSError) as exc:
        return [f"Blender requires physical BLENDER_HANDOFF: {exc}"]
    expected = {row[0]: row[1] for row in rows}
    seen: set[str] = set()
    for asset in assets:
        fx = asset.get("fx_id")
        if not isinstance(fx, str) or fx not in expected or fx in seen:
            errors.append("Blender handoff has unknown or duplicate FX ID")
            continue
        seen.add(fx)
        files = asset.get("files")
        if not isinstance(files, dict):
            errors.append(f"{fx}: Blender files must be an object")
            continue
        interactive = expected[fx] == "INTERACTIVE_3D"
        roles = {"scene", "builder", "preview", "inspection"}
        if interactive:
            roles.add("export")
        for role in sorted(roles):
            try:
                record = files.get(role)
                if not isinstance(record, dict):
                    raise ValueError("missing file record")
                path = _local_file(project, record.get("path"))
                data = path.read_bytes()
                if not data or hashlib.sha256(data).hexdigest() != record.get("sha256"):
                    raise ValueError("empty file or SHA-256 mismatch")
                if role == "scene" and (path.suffix != ".blend" or not data.startswith(b"BLENDER") or len(data) < 12):
                    raise ValueError("expected uncompressed Blender file")
                if role == "builder" and path.suffix != ".py":
                    raise ValueError("expected reproducible Python builder")
                if role == "preview":
                    if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".avif"}:
                        raise ValueError("expected raster preview")
                    inspect_raster(data, path.suffix.lower())
                if role == "export":
                    if len(data) < 20 or path.suffix != ".glb" or data[:4] != b"glTF":
                        raise ValueError("expected GLB export")
                    version, length = struct.unpack_from("<II", data, 4)
                    if version != 2 or length != len(data):
                        raise ValueError("invalid GLB header")
                if role == "inspection":
                    receipt_root = (project / "evidence/blender" / fx).resolve()
                    if path.name != "receipt.json" or path.parent.parent != receipt_root or not path.parent.name.startswith("inspection-"):
                        raise ValueError("inspection must be a server-owned receipt")
                    report = json.loads(data)
                    if not isinstance(report, dict) or type(report.get("exit_code")) is not int or report["exit_code"] != 0:
                        raise ValueError("inspection did not complete successfully")
                    if not all(isinstance(report.get(k), str) and report[k].strip() for k in ("blender_version", "command")):
                        raise ValueError("inspection needs actual Blender version and command")
                    if interactive and report.get("fresh_import") is not True:
                        raise ValueError("interactive export needs fresh-import inspection")
                    if report.get("provenance") != "SERVER_BLENDER_INSPECTION":
                        raise ValueError("run inspect_blender_asset; client-authored success is not inspection")
                    inputs = {key: files[key].get("sha256") for key in roles - {"inspection"} if isinstance(files.get(key), dict)}
                    if report.get("input_sha256") != inputs:
                        raise ValueError("server inspection is stale for current files")
            except (ValueError, OSError, UnicodeError) as exc:
                errors.append(f"{fx}: Blender {role}: {exc}")
    for fx in sorted(expected.keys() - seen):
        errors.append(f"{fx}: missing Blender handoff asset")
    return errors


def blender_delivery_errors(project: Path, implementation: Path) -> list[str]:
    """Bind inspected export to delivered bytes and a current browser fetch."""
    errors = blender_handoff_errors(project)
    text = (project / "production-plan.md").read_text(encoding="utf-8")
    rows = blender_rows(text)
    if errors or not rows:
        return errors
    from validation_release_integrity import implementation_digest
    match = re.search(r"(?m)^BLENDER_HANDOFF:[ \t]*([^\r\n]*)", section(text, HEADING))
    payload = json.loads(_local_file(project, match.group(1).strip().strip('`')).read_text(encoding="utf-8"))
    current = implementation_digest(implementation)
    fetched = {}
    for capture in (project / "evidence").glob("render-*/capture.json"):
        try:
            report = json.loads(capture.read_text(encoding="utf-8"))
            if report.get("source_sha256") == current:
                for item in report.get("captures", []):
                    if item.get("viewport") == "desktop" and not item.get("errors"):
                        fetched.update(item.get("fetched_assets", {}))
        except (ValueError, OSError):
            continue
    for item in payload["assets"]:
        fx = item["fx_id"]
        role = "export" if dict((r[0], r[1]) for r in rows)[fx] == "INTERACTIVE_3D" else "preview"
        try:
            delivery = item.get("delivery", {})
            target = _local_file(implementation, delivery.get("path"))
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            if digest != item["files"][role]["sha256"] or digest != delivery.get("sha256"):
                raise ValueError("delivered bytes differ from inspected asset")
            if fetched.get(target.relative_to(implementation).as_posix()) != digest:
                raise ValueError("current desktop render did not fetch the inspected asset; integrate and render again")
        except (ValueError, OSError) as exc:
            errors.append(f"{fx}: Blender delivery: {exc}")
    return errors
