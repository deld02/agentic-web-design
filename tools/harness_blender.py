"""Bounded external Blender handoff. The server never executes an uploaded builder."""
import base64
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from uuid import uuid4

from harness_media import inspect_raster
from validation_blender import blender_rows, blender_handoff_errors

MANIFEST = "evidence/blender/handoff.json"
SUFFIXES = {"scene": ".blend", "builder": ".py", "preview": ".png", "export": ".glb"}
MAX_BYTES = 12 * 1024 * 1024


def blender_capability():
    executable = os.getenv("BLENDER_EXECUTABLE") or shutil.which("blender")
    return {"available": bool(executable and Path(executable).is_file()), "executable": executable,
            "scope": "Optional fixed-script inspection; no uploaded Python execution, no artistic approval"}


def preserve_blender_assets(project, destination):
    """Rebuilds must retain server-inspected media, never overwrite conflicting output."""
    manifest = project / MANIFEST
    if not manifest.is_file():
        return
    errors = blender_handoff_errors(project)
    if errors:
        raise ValueError("Cannot rebuild with stale Blender handoff: " + "; ".join(errors))
    for item in json.loads(manifest.read_text(encoding="utf-8"))["assets"]:
        delivery = item.get("delivery", {})
        relative = delivery.get("path", "")
        if not relative or Path(relative).is_absolute():
            raise ValueError("Blender delivery path missing")
        target = (destination / relative).resolve()
        if not target.is_relative_to(destination.resolve()):
            raise ValueError("Blender delivery path escapes export")
        record = next((r for r in item["files"].values() if r.get("sha256") == delivery.get("sha256")), None)
        if not record:
            raise ValueError("Blender delivery has no inspected source")
        source = (project / record["path"]).resolve()
        if not source.is_relative_to(project.resolve()) or sha256(source.read_bytes()).hexdigest() != delivery["sha256"]:
            raise ValueError("Blender delivery source changed")
        if target.exists() and sha256(target.read_bytes()).hexdigest() != delivery["sha256"]:
            raise ValueError("Build conflicts with inspected Blender media")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())


def _context(api, arguments):
    run, active, project = api._project_and_stage(arguments["run_id"])
    if active["stage"] != "production-plan":
        raise ValueError("Blender return is only available during production-plan")
    fx = arguments["fx_id"]
    if not re.fullmatch(r"FX-[0-9]{3,}", fx):
        raise ValueError("invalid FX ID")
    plan = api._bounded_project_file(project, "production-plan.md")
    text = plan.read_text(encoding="utf-8")
    rows = [row for row in blender_rows(text) if row[0] == fx]
    if len(rows) != 1 or rows[0][1] not in {"INTERACTIVE_3D", "RENDERED_3D"}:
        raise ValueError("declare one custom Blender provenance row with a supported medium first")
    return run, project, fx, rows[0][1], plan, text


def import_blender_file(api, arguments):
    run, project, fx, medium, plan, text = _context(api, arguments)
    role = arguments["role"]
    if role not in SUFFIXES:
        raise ValueError("unsupported Blender file role")
    encoded = arguments["data_base64"]
    if len(encoded) > 4 * ((MAX_BYTES + 2) // 3):
        raise ValueError("Blender file exceeds 12 MiB import limit")
    data = base64.b64decode(encoded, validate=True)
    if not data or len(data) > MAX_BYTES:
        raise ValueError("empty or oversized Blender file")
    if role == "preview":
        inspect_raster(data, ".png")
    elif role == "scene" and not data.startswith(b"BLENDER"):
        raise ValueError("expected uncompressed .blend")
    elif role == "export" and not data.startswith(b"glTF"):
        raise ValueError("expected GLB")
    elif role == "builder":
        data.decode("utf-8")  # archived for reproducibility, NEVER executed
    digest = sha256(data).hexdigest()
    relative = f"evidence/blender/{fx}/{role}-{digest}{SUFFIXES[role]}"
    target = api._bounded_project_file(project, relative)
    manifest = api._bounded_project_file(project, MANIFEST)
    payload = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {"assets": []}
    item = next((a for a in payload["assets"] if a["fx_id"] == fx), None)
    if item is None:
        item = {"fx_id": fx, "files": {}}
        payload["assets"].append(item)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    item["files"][role] = {"path": relative, "sha256": digest}
    item["files"].pop("inspection", None)
    item.pop("delivery", None)
    manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    field = re.compile(r"(?m)^BLENDER_HANDOFF:[^\r\n]*")
    text = field.sub("BLENDER_HANDOFF: " + MANIFEST, text) if field.search(text) else text.replace(
        "### 3D production provenance", "### 3D production provenance\n\nBLENDER_HANDOFF: " + MANIFEST, 1)
    plan.write_text(text, encoding="utf-8")
    api.harness.append_event(run, {"event": "artifact_write", "stage": "production-plan", "agent": "05",
                                  "target": relative, "sha256": digest, "provenance": "EXTERNAL_3D_IMPORT"})
    return {"status": "IMPORTED_NOT_INSPECTED", "path": relative, "sha256": digest}


def inspect_blender_asset(api, arguments):
    run, project, fx, medium, _plan, _text = _context(api, arguments)
    capability = blender_capability()
    if not capability["available"]:
        raise RuntimeError("Blender unavailable; configure BLENDER_EXECUTABLE. No approval recorded")
    manifest = api._bounded_project_file(project, MANIFEST)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    item = next(a for a in payload["assets"] if a["fx_id"] == fx)
    roles = {"scene", "builder", "preview"} | ({"export"} if medium == "INTERACTIVE_3D" else set())
    paths = {}
    for role in roles:
        record = item["files"].get(role, {})
        path = api._bounded_project_file(project, record.get("path", ""))
        if not path.is_file() or sha256(path.read_bytes()).hexdigest() != record.get("sha256"):
            raise ValueError(f"missing or stale Blender {role}")
        paths[role] = path
    inspect_raster(paths["preview"].read_bytes(), ".png")
    directory = api._bounded_project_file(project, f"evidence/blender/{fx}/inspection-{uuid4().hex}")
    directory.mkdir(parents=True)
    env = {k: v for k, v in os.environ.items() if k.upper() in {"SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP"}}
    worker = Path(__file__).with_name("blender_inspect.py")
    reports, commands = {}, []
    for role in ("scene", "export") if medium == "INTERACTIVE_3D" else ("scene",):
        output = directory / f"{role}.json"
        command = [capability["executable"], "--background", "--factory-startup", "--disable-autoexec",
                   "--python-exit-code", "1", "--python", str(worker), "--", str(paths[role]), str(output)]
        commands.append(command)
        with (directory / f"{role}.log").open("wb") as log:
            result = subprocess.run(command, env=env, cwd=directory, stdout=log, stderr=subprocess.STDOUT, timeout=60, check=False)
        if result.returncode or not output.is_file():
            raise RuntimeError(f"Blender {role} inspection failed; logs preserved at {directory}")
        reports[role] = json.loads(output.read_text(encoding="utf-8"))
    for role, path in paths.items():
        if sha256(path.read_bytes()).hexdigest() != item["files"][role]["sha256"]:
            raise ValueError("Blender inputs changed during inspection")
    report = {"provenance": "SERVER_BLENDER_INSPECTION", "exit_code": 0,
              "blender_version": reports["scene"]["blender_version"], "command": subprocess.list2cmdline(commands[0]),
              "fresh_import": "export" in reports, "inspected": reports,
              "input_sha256": {role: item["files"][role]["sha256"] for role in roles}}
    inspection = directory / "receipt.json"
    inspection.write_text(json.dumps(report, indent=2), encoding="utf-8")
    item["files"]["inspection"] = {"path": inspection.relative_to(project).as_posix(), "sha256": sha256(inspection.read_bytes()).hexdigest()}
    role = "export" if medium == "INTERACTIVE_3D" else "preview"
    relative = f"media/blender/{fx}-{item['files'][role]['sha256'][:16]}{paths[role].suffix}"
    api._implementation_root(project)
    destination = api._bounded_project_file(project, "implementation/" + relative)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(paths[role].read_bytes())
    item["delivery"] = {"path": relative, "sha256": item["files"][role]["sha256"]}
    manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    api.harness.append_event(run, {"event": "tool_call", "tool": "BLENDER_INSPECT", "stage": "production-plan",
                                  "agent": "05", "target": fx, "receipt": item["files"]["inspection"]})
    return {"status": "INSPECTED_NOT_INTEGRATED", "asset": item, "instruction": "06 must load this exact delivery.path; render_landing and independent review remain required."}
