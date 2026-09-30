"""MCP media, visual review and static-delivery operations.

This module receives the adapter explicitly; it never imports a second server
instance when the executable entry point is __main__.
"""

import base64
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import re
from hashlib import sha256
from uuid import uuid4
import zipfile

from harness_media import inspect_raster, image_content
from harness_render import render_static
from harness_review import run_visual_review, revision_stage
from validation_common import table_rows
from validation_release_integrity import implementation_digest, write_manifest
from harness_frontend_build import build_capability, build_export
from harness_session import session_mode, codex_status, register_session_image


def check_technology(api, arguments):
    profile = arguments["profile"]
    services = arguments.get("required_services", [])
    capability = build_capability()
    supported = profile in {"static-html", "npm-static-export"} and not services
    ready = supported and (profile == "static-html" or capability["available"])
    return {"status":"AVAILABLE_FOR_PROBE" if ready else "BLOCKED", "profile":profile,
            "build_runtime":capability, "required_services":services,
            "reason":"No automatic stack substitution. SSR and external services need a separate verified adapter; hosting is not deployment authorization."}


def build_frontend(api, arguments):
    run, active, project = api._project_and_stage(arguments["run_id"])
    stage = revision_stage(project, active["stage"]) or active["stage"]
    if stage not in {"technology-selection", "implementation"}:
        raise ValueError("frontend build is only available to the frontend owner")
    api._implementation_root(project)
    api._bounded_project_file(project, "frontend")
    result = build_export(project, arguments["output"])
    api.harness.append_event(run, {"event":"artifact_write", "stage":stage, "agent":"06",
                                  "target":"evidence/frontend-build.json"})
    return result


def runtime_status(api, arguments):
    checks = {"image_decoder":bool(importlib.util.find_spec("PIL")),
              "api_key_configured":bool(os.getenv("OPENAI_API_KEY")),
              "review_model_configured":bool(os.getenv("AGENTIC_REVIEW_MODEL")),
              "image_model_configured":bool(os.getenv("AGENTIC_IMAGE_MODEL")),
              "node_available":bool(shutil.which("node"))}
    checks["browser_runtime_available"] = False
    if checks["node_available"]:
        try:
            probe = subprocess.run([shutil.which("node"), "-e", "const p=require('playwright');const fs=require('fs');process.exit(fs.existsSync(p.chromium.executablePath()) || process.env.AGENTIC_BROWSER_CHANNEL==='msedge' && fs.existsSync('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe') ? 0 : 1)"],
                capture_output=True, timeout=10, check=False)
            checks["browser_runtime_available"] = probe.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            pass
    native = session_mode()
    if native:
        for name in ("api_key_configured", "review_model_configured", "image_model_configured"):
            checks.pop(name)
    review = codex_status() if native else {"provider": "OPENAI_RESPONSES"}
    if native:
        checks["subscription_reviewer_ready"] = bool(review.get("available") and review.get("chatgpt_login"))
    from harness_blender import blender_capability
    return {"checks":checks, "ready_for_live_probe":all(checks.values()),
            "ai_backend": "session" if native else "api",
            "review_readiness": review,
            "blender": blender_capability(),
            "image_workflow": "Use native session image tool, then register_session_image; no automatic API fallback" if native else "API generation",
            "supported_build":"static HTML or npm static export through opt-in Docker or explicitly approved trusted local builds",
            "frontend_build":build_capability(),
            "limitations":["Configuration presence does not verify credentials, model access or browser launch.",
                            "Run render_landing and run_review to test those capabilities. API operations may incur costs."]}


def read_image(api, arguments):
    run = api._run_dir(arguments["run_id"])
    project = (run / "project").resolve()
    path = api._bounded_project_file(project, arguments["path"])
    return {"path":arguments["path"], "_images":[image_content(path)]}


def upload_image(api, arguments):
    run, active, project = api._project_and_stage(arguments["run_id"])
    stage = revision_stage(project, active["stage"]) or active["stage"]
    if stage not in {"research-strategy", "direction-divergence", "creative-master", "visual-experience", "production-plan"}:
        raise ValueError("image import is unavailable at this stage")
    from harness_design_plan import require_plan
    require_plan(project,stage)
    data = base64.b64decode(arguments["data_base64"], validate=True)
    suffix = arguments["extension"].lower()
    metadata = inspect_raster(data, suffix)
    asset_id = arguments.get("asset_id")
    if stage == "research-strategy" and asset_id:
        raise ValueError("research captures are reference evidence, not production assets")
    if stage == "production-plan":
        targets = api.generated_asset_targets(project)
        if not asset_id or asset_id not in targets:
            raise ValueError("production import requires a declared generated asset_id")
        path = api._bounded_project_file(project, "implementation/" + targets[asset_id])
        if not path.is_relative_to(api._implementation_root(project)) or path.suffix.lower() != suffix:
            raise ValueError("import must match declared asset target")
    else:
        path = project / "evidence" / f"import-{uuid4().hex}{suffix}"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError("import target already exists; preserve the original and choose a new target")
    path.write_bytes(data)
    relative = path.relative_to(project).as_posix()
    api.harness.append_event(run, {"event":"artifact_write", "stage":active["stage"], "agent":active["agent"],
        "target":relative, "provenance":"EXTERNAL_IMPORT", "sha256":metadata["sha256"]})
    # An import is evidence of a physical file, not proof that this server
    # generated it. Never fabricate a tool_call IMAGE_GEN from uploaded bytes.
    return {"status":"IMPORTED", "path":relative, **metadata,
            "generation_observed":False, "_images":[image_content(path)]}


def render_landing(api, arguments):
    run, active, project = api._project_and_stage(arguments["run_id"])
    stage = revision_stage(project, active["stage"]) or active["stage"]
    study = {"direction-divergence":"evidence/directions", "visual-experience":"evidence/compositions"}.get(stage)
    from validation_creative_decisions import evidence_led
    if stage == "creative-master" and evidence_led(project):
        study = "evidence/proof"
    from harness_design_plan import require_plan
    require_plan(project,stage)
    if not study and stage not in {"technology-selection", "production-plan", "implementation", "build-review"}:
        raise ValueError("rendering is unavailable at this stage")
    implementation = api._bounded_project_file(project, study) if study else api._implementation_root(project)
    content = (project / "content-architecture.md").read_text(encoding="utf-8")
    scenes = [] if study else [row[0] for row in table_rows(content,"## Sitemap / page or section outline","Scene ID") if row and re.fullmatch(r"SCN-[0-9]{3,}",row[0])]
    result = render_static(project, implementation, arguments.get("entry", "index.html"), scenes, arguments.get("actions"))
    owner = next(item["agent"] for item in api.load_json(api.ROOT / "config/pipeline.json")["stages"] if item["id"] == stage)
    for capture in result["captures"]:
        api.harness.append_event(run, {"event":"render", "stage":stage, "agent":owner,
            "target":capture["file"], "source_sha256":result["source_sha256"]})
    result["_images"] = [image_content(project / item["file"]) for item in result["captures"] if item["kind"] == "whole-page"]
    return result


def run_review(api, arguments):
    run, active, project = api._project_and_stage(arguments["run_id"])
    stage = next(s for s in api.load_json(api.ROOT / "config/pipeline.json")["stages"] if s["id"] == active["stage"])
    paths = arguments["images"]
    for name in paths:
        api._bounded_project_file(project, name)
    if stage["id"] == "build-review":
        source = implementation_digest(api._implementation_root(project))
        for name in paths:
            manifest = (project / name).parent / "capture.json"
            if not manifest.is_file():
                raise ValueError("build review requires managed render evidence")
            report = api.load_json(manifest)
            if any(c.get("errors") or c.get("observations", {}).get("overflow") or c.get("observations", {}).get("missingImages") for c in report.get("captures", [])):
                raise ValueError("managed render contains runtime errors, overflow or missing images")
            if report.get("source_sha256") != source or report.get("image_sha256", {}).get(name) != sha256((project / name).read_bytes()).hexdigest():
                raise ValueError("build-review render is stale or unverified")
    record = run_visual_review(api.ROOT, project, stage, paths)
    api.harness.append_event(run, {"event":"tool_call", "stage":stage["id"], "agent":"07", "tool":"ISOLATED_VISUAL_REVIEW", "target":record["response_id"]})
    return record


def prepare_delivery(api, arguments):
    run, active, project = api._project_and_stage(arguments["run_id"])
    if active["stage"] not in {"implementation", "build-review", "release"}:
        raise ValueError("delivery preparation is unavailable at this stage")
    implementation = api._implementation_root(project)
    if not (implementation / "index.html").is_file():
        raise ValueError("delivery needs a static index.html")
    files = []
    for path in implementation.rglob("*"):
        api._bounded_project_file(project, path.relative_to(project).as_posix())
        if path.is_file():
            if path.name.startswith(".env") or any(part in {".git", "node_modules"} for part in path.parts):
                raise ValueError("delivery contains private/dependency directories; remove them from export")
            files.append(path)
    if sum(path.stat().st_size for path in files) > 150 * 1024 * 1024:
        raise ValueError("delivery exceeds 150 MiB")
    from validation_release_integrity import manifest_path
    if manifest_path(project) != project / "evidence/release-integrity.json":
        raise ValueError("managed integrity manifest must use evidence/release-integrity.json")
    destination = project / "delivery.zip"
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as package:
        for path in files:
            package.write(path, path.relative_to(implementation))
    manifest = write_manifest(project, implementation)
    return {"status":"PACKAGED_NOT_APPROVED", "package":str(destination), "files":len(files),
            "integrity_manifest":manifest.relative_to(project).as_posix(),
            "sha256":sha256(destination.read_bytes()).hexdigest(),
            "instruction":"Complete the final contract and run advance_stage/verify_run. Packaging is not release approval."}


def download_delivery(api, arguments):
    from validation_execution_receipt import execution_receipt_errors
    run = api._run_dir(arguments["run_id"])
    errors = execution_receipt_errors(run / "execution-receipt.json", api.ROOT)
    if errors:
        raise ValueError("delivery is not verified: " + "; ".join(errors))
    package = run / "project/delivery.zip"
    if not package.is_file() or package.stat().st_size > 12 * 1024 * 1024:
        raise ValueError("inline download supports ZIPs up to 12 MiB; retrieve larger packages on the server")
    implementation = run / "project/implementation"
    expected = {path.relative_to(implementation).as_posix():path for path in implementation.rglob("*") if path.is_file()}
    with zipfile.ZipFile(package) as archive:
        if set(archive.namelist()) != set(expected) or len(archive.namelist()) != len(expected):
            raise ValueError("delivery ZIP does not match verified implementation")
        for name, path in expected.items():
            if archive.getinfo(name).file_size != path.stat().st_size or sha256(archive.read(name)).digest() != sha256(path.read_bytes()).digest():
                raise ValueError("delivery ZIP content is stale")
    return {"filename":"delivery.zip", "_resources":[{"type":"resource", "resource":{
        "uri":f"landing://{run.name}/delivery.zip", "mimeType":"application/zip", "blob":base64.b64encode(package.read_bytes()).decode("ascii")}}]}


def operation_specs(api):
    from functools import partial
    from harness_blender import import_blender_file, inspect_blender_asset
    string = {"type":"string"}
    run = {"run_id":string}
    specs = [
        ("import_blender_file", "Import one declared custom Blender file, at most 12 MiB. Builder is archived, never executed. No client inspection receipts accepted.", {**run,"fx_id":string,"role":{"type":"string","enum":["scene","builder","preview","export"]},"data_base64":string}, ["run_id","fx_id","role","data_base64"], import_blender_file, False, False),
        ("inspect_blender_asset", "Open the returned scene and GLB in fresh Blender processes with autoexec disabled. Server-owned inspector, 60 seconds per process; copy verified asset into implementation. Not artistic approval.", {**run,"fx_id":string}, ["run_id","fx_id"], inspect_blender_asset, False, False),
        ("check_technology", "Check execution compatibility before selecting a stack; does not approve design or deploy.", {"profile":{"type":"string","enum":["static-html","npm-static-export","server-runtime"]},"required_services":{"type":"array","items":string}}, ["profile"], check_technology, True, False),
        ("runtime_status", "Check local runtime configuration before starting design.", {}, [], runtime_status, True, False),
        ("build_frontend", "Build a static export using the operator-selected backend. Docker is isolated; local executes trusted code with host permissions and requires source-digest approval. Preserves old export; no deployment.", {**run,"output":{"type":"string","enum":["dist","out"]}}, ["run_id","output"], build_frontend, False, True),
        ("read_image", "View a real project raster, including after run completion.", {**run,"path":string}, ["run_id","path"], read_image, True, False),
        ("register_session_image", "Register a native session image tool result. Requires physical raster and actual tool result reference; provenance is client-attested, not server-observed generation.", {**run,"path":string,"asset_id":string,"tool_call_reference":string}, ["run_id","path","tool_call_reference"], register_session_image, False, False),
        ("upload_image", "Import a decoded raster, including reference captures during research-strategy. Research captures must omit asset_id. This is not observed image generation.", {**run,"data_base64":string,"extension":{"type":"string","enum":[".png",".jpg",".jpeg",".webp"]},"asset_id":string}, ["run_id","data_base64","extension"], upload_image, False, False),
        ("render_landing", "Capture static/exported HTML and optional click/hover/tab/reduced-motion states. No shell build; external network blocked.", {**run,"entry":string,"actions":{"type":"array","items":{"type":"object","properties":{"type":{"type":"string","enum":["click","hover","tab","reduced-motion"]},"selector":string},"required":["type"],"additionalProperties":False}}}, ["run_id"], render_landing, False, False),
        ("run_review", "Fresh-context visual review using configured API or Codex subscription backend. Consumes the selected provider's allowance. Never accepts a client-authored verdict.", {**run,"images":{"type":"array","items":string}}, ["run_id","images"], run_review, False, True),
        ("prepare_delivery", "Package static landing and integrity manifest. Does not approve delivery.", run, ["run_id"], prepare_delivery, False, False),
        ("download_delivery", "Return a verified ZIP as an MCP binary resource; client display support varies.", run, ["run_id"], download_delivery, True, False),
    ]
    return {name:(description, api._schema(properties,required), api._serialized(partial(function,api)),
        {"readOnlyHint":readonly,"destructiveHint":False,"idempotentHint":readonly,"openWorldHint":remote})
        for name,description,properties,required,function,readonly,remote in specs}
