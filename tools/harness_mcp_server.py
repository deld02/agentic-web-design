#!/usr/bin/env python3
"""Small MCP adapter for the canonical landing evaluation harness.

The adapter grants no design authority. It exposes the existing sequential
harness through bounded tools so a chat client cannot silently bypass it.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import stat
import sys
import urllib.request
from functools import wraps
from threading import RLock
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

import evaluation_harness as harness
from project_validation import ROOT, load_json
from validation_execution_receipt import execution_receipt_errors
from validation_image_generation import generated_asset_targets
from validation_user_authority import record_master_confirmation
from stage_orchestrator import activate_stage_status, build_stage_packet, capability_guidance, complete_stage_status
from harness_transition import transition_rollback, recover_transition, server_lock

PROTOCOL_VERSION = "2025-06-18"
RUNS_ROOT = (ROOT / ".harness" / "runs").resolve()
MAX_TEXT_BYTES = 1_000_000
MAX_REQUEST_BYTES = 18 * 1024 * 1024
# One server process owns a runs directory. Serialize reads as well as writes so
# clients cannot observe candidate state while its validation is in progress.
_STATE_LOCK = RLock()


def _serialized(function):
    @wraps(function)
    def guarded(*args, **kwargs):
        with _STATE_LOCK:
            with server_lock(RUNS_ROOT):
                return function(*args, **kwargs)
    return guarded

STAGE_FILES: dict[str, set[str]] = {
    "definition": {"PROJECT.md", "brief.md", "project.config.json"},
    "research-strategy": {"research-strategy.md"},
    "content-architecture": {"content-architecture.md"},
    "direction-divergence": {"creative-direction.md"},
    "direction-review": set(),
    "creative-master": {"creative-direction.md"},
    "visual-experience": {"visual-system.md"},
    "design-review": set(),
    "technology-selection": {"technology-decision.md", "project.config.json"},
    "production-plan": {"production-plan.md"},
    "implementation": {"qa-release.md"},
    "build-review": set(),
    "release": {"qa-release.md", "decision-log.md"},
}
IMPLEMENTATION_STAGES = {"technology-selection", "implementation"}
TEXT_SUFFIXES = {".md", ".json", ".html", ".css", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".astro", ".vue", ".svelte", ".txt"}
RASTER_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".avif"}


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _run_dir(run_id: str) -> Path:
    if not run_id or Path(run_id).name != run_id:
        raise ValueError("run_id must be one managed run name")
    candidate = (RUNS_ROOT / run_id).resolve()
    if not _inside(candidate, RUNS_ROOT) or not (candidate / "run.json").is_file():
        raise ValueError("managed run not found")
    recover_transition(candidate)
    return candidate


def _project_and_stage(run_id: str) -> tuple[Path, dict[str, Any], Path]:
    run_dir = _run_dir(run_id)
    from harness_session import session_mode
    backend = load_json(run_dir / "run.json").get("ai_backend")
    if backend and backend != ("session" if session_mode() else "api"):
        raise ValueError("run backend differs from server configuration; no implicit provider switch")
    status = harness.chat_status(run_dir)
    return run_dir, status, (run_dir / "project").resolve()


def _implementation_root(project: Path, config: dict | None = None) -> Path:
    config = config if config is not None else load_json(project / "project.config.json")
    value = config.get("implementation_root", "undetermined")
    # A managed implementation is always a dedicated, non-overlapping subtree.
    # Allowing arbitrary roots turns a code-write permission into state access.
    if not isinstance(value, str) or value.replace("\\", "/") != "implementation":
        raise ValueError("managed implementation_root must be 'implementation'")
    implementation = _bounded_project_file(project, value)
    if implementation != project / "implementation":
        raise ValueError("implementation_root must not redirect through a link")
    return implementation


def _bounded_project_file(project: Path, relative: str) -> Path:
    if not relative or Path(relative).is_absolute() or ":" in relative:
        raise ValueError("path must be relative to the managed project")
    lexical = project / relative
    for part in (lexical, *lexical.parents):
        if part == project:
            break
        attributes = getattr(part.lstat(), "st_file_attributes", 0) if part.exists() else 0
        if part.is_symlink() or attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            raise ValueError("managed paths must not traverse links or junctions")
    candidate = (project / relative).resolve()
    if not _inside(candidate, project):
        raise ValueError("path escapes the managed project")
    return candidate


def _write_allowed(project: Path, stage: str, relative: str) -> Path:
    from harness_review import revision_stage
    stage = revision_stage(project, stage) or stage
    candidate = _bounded_project_file(project, relative)
    normalized = candidate.relative_to(project).as_posix()
    if normalized in STAGE_FILES.get(stage, set()):
        return candidate
    study_root = {"direction-divergence":"evidence/directions/", "visual-experience":"evidence/compositions/"}.get(stage)
    if study_root and normalized.startswith(study_root) and candidate.suffix.lower() in TEXT_SUFFIXES:
        return candidate
    if stage in IMPLEMENTATION_STAGES:
        if normalized.startswith("frontend/") and candidate.suffix.lower() in TEXT_SUFFIXES:
            return candidate
        implementation = _implementation_root(project)
        if _inside(candidate, implementation):
            return candidate
    raise ValueError(f"{relative} is not writable during {stage}")


@_serialized
def start_landing(arguments: dict[str, Any]) -> dict[str, Any]:
    brief = str(arguments.get("brief", "")).strip()
    scenario = str(arguments.get("scenario", "")).strip() or None
    if not brief and not scenario:
        raise ValueError("brief or scenario is required")
    from harness_operations import runtime_status
    readiness = runtime_status(sys.modules[__name__], {})
    if not readiness["ready_for_live_probe"]:
        return {"status":"BLOCKED", "managed":False, "adapter_readiness":readiness,
                "instruction":"Configure missing server capabilities before starting a landing. No run was created."}
    result = harness.start_chat_run(scenario, RUNS_ROOT, None, brief or None)
    from harness_session import session_mode
    run_path = Path(result["run_dir"]) / "run.json"
    run_metadata = load_json(run_path)
    run_metadata["ai_backend"] = "session" if session_mode() else "api"
    run_path.write_text(json.dumps(run_metadata, indent=2), encoding="utf-8")
    result["managed"] = True
    result["adapter_readiness"] = readiness
    return _with_stage_packet(result)


@_serialized
def get_stage(arguments: dict[str, Any]) -> dict[str, Any]:
    run_dir = _run_dir(str(arguments.get("run_id", "")))
    run = load_json(run_dir / "run.json")
    if run.get("status") not in {"RUNNING", "NEEDS_USER"}:
        return {"status": run.get("status"), "run_id": run_dir.name,
                "findings": run.get("findings", []), "stage": run.get("active_stage")}
    return _with_stage_packet(harness.chat_status(run_dir))


def _with_stage_packet(status: dict[str, Any]) -> dict[str, Any]:
    from harness_session import session_mode
    if session_mode():
        status["execution_backend"] = "CODEX_SESSION_NO_API_KEY"
        status["native_media_instruction"] = "At image stages use the session image-generation tool and return a physical raster with its actual tool result reference via register_session_image. Tool origin is client-attested. If no native image tool is available, stop for production; never substitute SVG or call an API. run_review launches a fresh subscription-authenticated Codex CLI review; missing login blocks review, not a fake PASS."
    stage_id = status.get("stage")
    if not stage_id or "project_dir" not in status or status.get("status") == "FAILED":
        return status
    stages = load_json(ROOT / "config" / "pipeline.json")["stages"]
    stage = next(item for item in stages if item["id"] == stage_id)
    project = Path(status["project_dir"]).resolve()
    from harness_review import revision_stage
    correction_stage = revision_stage(project, stage_id)
    if correction_stage:
        stage = next(item for item in stages if item["id"] == correction_stage)
        writable = STAGE_FILES.get(correction_stage, set())
        status["stage_packet"] = build_stage_packet(ROOT, project, stage, writable)
        status["stage_packet"]["revision_for"] = stage_id
        status["stage_packet"]["findings"] = load_json(project / ".reviews" / f"{stage_id}.json")["result"]["findings"]
        status["stage_packet"]["correction_kind"] = load_json(project / ".reviews" / f"{stage_id}.json")["result"].get('correction_kind')
        approval = project / '.reviews/design-approval.json'
        if stage_id == 'design-review' and approval.is_file() and load_json(approval).get('status') == 'ADJUST':
            status["stage_packet"]["findings"] = [load_json(approval)['user_signal']]
        status["stage_packet"]["completion_protocol"] = [
            "Correct only the independent findings, then call run_review again. The review stage stays open; do not approve it yourself.",
            "CRAFT: preserve the viable thesis and repair execution. CONCEPT: replace the failed relationship within the owner stage, preserve constraints and valid upstream content; do not merely reposition assets. REFERENCE: stop for orchestrator escalation to research, never compensate with extra effects or silently edit upstream evidence. Missing diagnosis requires a fresh review, not an assumed correction. Keep the existing one-correction budget.",
        ]
        return status
    writable = STAGE_FILES.get(stage_id, set())
    status["stage_packet"] = build_stage_packet(ROOT, project, stage, writable)
    review_path = project / '.reviews' / f'{stage_id}.json'
    if review_path.is_file():
        review_result = load_json(review_path).get('result', {})
        if review_result.get('verdict') == 'REVISE' and review_result.get('correction_kind') == 'REFERENCE':
            status['stage_packet']['correction_kind'] = 'REFERENCE'
            status['stage_packet']['writable_files'] = []
            status['stage_packet']['completion_protocol'] = [
                'Escalate inadequate references to 00; preserve work and request upstream recovery. Do not edit research or downstream design from this review stage. No automatic retry or new budget.'
            ]
    return status


@_serialized
def list_files(arguments: dict[str, Any]) -> dict[str, Any]:
    _run, status, project = _project_and_stage(str(arguments.get("run_id", "")))
    files = [
        path.relative_to(project).as_posix()
        for path in sorted(project.rglob("*"))
        if path.is_file() and ".git" not in path.parts
    ]
    return {"stage": status["stage"], "files": files}


@_serialized
def read_file(arguments: dict[str, Any]) -> dict[str, Any]:
    _run, status, project = _project_and_stage(str(arguments.get("run_id", "")))
    relative = str(arguments.get("path", ""))
    candidate = _bounded_project_file(project, relative)
    if not candidate.is_file() or candidate.suffix.lower() not in TEXT_SUFFIXES:
        raise ValueError("requested text file is missing or unsupported")
    if candidate.stat().st_size > MAX_TEXT_BYTES:
        raise ValueError("file exceeds MCP read limit")
    return {"stage": status["stage"], "path": relative, "text": candidate.read_text(encoding="utf-8")}


@_serialized
def get_guidance(arguments: dict[str, Any]) -> dict[str, Any]:
    _run, status, _project = _project_and_stage(str(arguments.get("run_id", "")))
    from harness_review import revision_stage
    return {"stage": status["stage"]} | capability_guidance(
        ROOT,
        revision_stage(_project, status["stage"]) or status["stage"],
        str(arguments.get("capability_id", "")).strip(),
    )


@_serialized
def write_file(arguments: dict[str, Any]) -> dict[str, Any]:
    run_dir, status, project = _project_and_stage(str(arguments.get("run_id", "")))
    relative = str(arguments.get("path", ""))
    text = arguments.get("text")
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    if len(text.encode("utf-8")) > MAX_TEXT_BYTES:
        raise ValueError("file exceeds MCP write limit")
    candidate = _write_allowed(project, status["stage"], relative)
    if candidate == project / "project.config.json":
        config = json.loads(text)
        if not isinstance(config, dict):
            raise ValueError("project configuration must be an object")
        if config.get("implementation_root", "undetermined") != "undetermined":
            _implementation_root(project, config)
    if candidate.suffix.lower() not in TEXT_SUFFIXES:
        raise ValueError("only supported text/code files may be written")
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_text(text, encoding="utf-8")
    target = candidate.relative_to(project).as_posix()
    from harness_review import revision_stage
    owner_stage = revision_stage(project, status["stage"]) or status["stage"]
    owner = next(item["agent"] for item in load_json(ROOT / "config/pipeline.json")["stages"] if item["id"] == owner_stage)
    harness.append_event(run_dir, {"event": "artifact_write", "stage": owner_stage, "agent": owner, "target": target,
                                  "review_for":status["stage"] if owner_stage != status["stage"] else None})
    return {"status": "WRITTEN", "stage": status["stage"], "path": target, "bytes": len(text.encode("utf-8"))}


@_serialized
def register_image(arguments: dict[str, Any]) -> dict[str, Any]:
    return harness.confirm_chat_image(
        _run_dir(str(arguments.get("run_id", ""))),
        Path(str(arguments.get("path", ""))),
        str(arguments.get("asset_id", "")).strip() or None,
    )


def _image_output(run_dir: Path, stage: str, relative: str, asset_id: str | None) -> Path:
    project = (run_dir / "project").resolve()
    if stage == "creative-master":
        output = _bounded_project_file(project, relative or "assets/artistic-master.png")
    else:
        targets = generated_asset_targets(project)
        if not asset_id or asset_id not in targets:
            raise ValueError("production image needs a declared generated asset_id")
        output = (_implementation_root(project) / targets[asset_id]).resolve()
        if not _inside(output, _implementation_root(project)):
            raise ValueError("declared image target escapes implementation root")
    if output.suffix.lower() not in RASTER_SUFFIXES:
        raise ValueError("generated output must use a supported raster extension")
    return output


def _openai_image(prompt: str, api_key: str, output_format: str = "png", opener: Callable[..., Any] = urllib.request.urlopen) -> bytes:
    model = os.getenv("AGENTIC_IMAGE_MODEL")
    if not model:
        raise RuntimeError("AGENTIC_IMAGE_MODEL must be explicitly configured")
    payload = json.dumps({"model": model, "prompt": prompt, "output_format": output_format}).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with opener(request, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))
    encoded = result.get("data", [{}])[0].get("b64_json")
    if not encoded:
        raise RuntimeError("image API returned no raster data")
    return base64.b64decode(encoded, validate=True)


@_serialized
def generate_image(arguments: dict[str, Any]) -> dict[str, Any]:
    run_dir, status, _project = _project_and_stage(str(arguments.get("run_id", "")))
    if status["stage"] not in {"creative-master", "production-plan"}:
        raise ValueError("image generation is allowed only at its two canonical pipeline stages")
    prompt = str(arguments.get("prompt", "")).strip()
    if len(prompt) < 40:
        raise ValueError("image prompt must describe a project-specific visual intention")
    from harness_session import session_mode
    if session_mode():
        destination = _image_output(run_dir, status["stage"], str(arguments.get("path", "")), arguments.get("asset_id"))
        return {"status": "NEEDS_NATIVE_IMAGE", "prompt": prompt, "output_path": str(destination),
                "instruction": "Call the native session image-generation tool now. Save its actual raster in the project, then call register_session_image with its actual result reference. Do not draw a substitute SVG or invent a receipt. If unavailable, stop for image production; no API fallback."}
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for physical image generation")
    asset_id = str(arguments.get("asset_id", "")).strip() or None
    output = _image_output(run_dir, status["stage"], str(arguments.get("path", "")), asset_id)
    output_format = {".jpg": "jpeg", ".jpeg": "jpeg", ".webp": "webp", ".png": "png"}.get(output.suffix.lower())
    if not output_format:
        raise ValueError("direct image generation supports PNG, JPEG or WebP targets")
    raster = _openai_image(prompt, api_key, output_format)
    from harness_media import inspect_raster, image_content
    inspect_raster(raster, output.suffix)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(raster)
    return harness.confirm_chat_image(run_dir, output, asset_id, observed_generation=True) | {"_images":[image_content(output)]}


@_serialized
def confirm_master(arguments: dict[str, Any]) -> dict[str, Any]:
    run_dir, active, project = _project_and_stage(str(arguments.get("run_id", "")))
    from validation_landing_blueprint import complete_landing_flow
    if complete_landing_flow(project):
        raise ValueError("This run approves the complete landing once at design-review; use confirm_design, not confirm_master")
    if active["stage"] != "creative-master":
        raise ValueError("master confirmation is valid only during creative-master")
    result = record_master_confirmation(
        project / "creative-direction.md",
        str(arguments.get("status", "")),
        str(arguments.get("user_signal", "")),
    )
    harness.append_event(run_dir, {"event": "artifact_write", "stage": active["stage"], "agent": active["agent"], "target": "creative-direction.md"})
    run = load_json(run_dir / "run.json")
    run.update(status="RUNNING", active_stage=active["stage"], findings=[])
    harness.write_json(run_dir / "run.json", run)
    return result | {"stage": active["stage"]}


@_serialized
def confirm_design(arguments: dict[str, Any]) -> dict[str, Any]:
    run_dir, active, project = _project_and_stage(str(arguments.get("run_id", "")))
    from validation_landing_blueprint import complete_landing_flow, record_design_approval
    if active["stage"] != "design-review" or not complete_landing_flow(project):
        raise ValueError("Complete landing approval is available only at design-review in the new flow")
    result = record_design_approval(project, str(arguments.get("status", "")), str(arguments.get("user_signal", "")))
    harness.append_event(run_dir, {"event":"tool_call", "stage":"design-review", "agent":"07", "tool":"USER_DESIGN_CONFIRMATION", "target":result['review_id'], **result})
    return result


@_serialized
def advance_stage(arguments: dict[str, Any]) -> dict[str, Any]:
    run_dir, active, project = _project_and_stage(str(arguments.get("run_id", "")))
    stages = load_json(ROOT / "config" / "pipeline.json")["stages"]
    stage = next(item for item in stages if item["id"] == active["stage"])
    if stage["id"] == "visual-experience":
        from harness_review import design_preflight_errors
        errors = design_preflight_errors(project)
        if errors:
            # Keep ownership with 04; do not hand malformed work to 07.
            return _with_stage_packet({**active, "status":"REVISE", "findings":errors})
    if stage["agent"] == "07":
        from harness_review import review_record_errors, revision_stage
        errors = review_record_errors(project, stage["id"])
        if errors:
            if revision_stage(project, stage["id"]):
                return _with_stage_packet({**active, "status":"REVISE", "findings":errors})
            return {**active, "status":"BLOCKED", "findings":errors}
    if stage["id"] == "design-review":
        from validation_landing_blueprint import design_approval_errors
        errors = design_approval_errors(project)
        if errors:
            return {**active, "status":"NEEDS_USER", "findings":errors,
                    "instruction":"Show the complete desktop/mobile proposal. Record the actual user signal with confirm_design. Do not build yet."}
    evidence = [
        str(item.get("target")) for item in harness.read_events(run_dir)
        if item.get("event") == "artifact_write" and item.get("stage") == stage["id"] and item.get("target")
    ]
    state_path = project / "status.json"
    original = state_path.read_bytes()
    with transition_rollback(run_dir):
        complete_stage_status(project, stage, evidence)
        result = harness.advance_chat_run(run_dir)
        if result.get("status") in {"FAILED", "REVISE", "NEEDS_USER", "BLOCKED"}:
            state_path.write_bytes(original)
        elif result.get("stage"):
            next_stage = next(item for item in stages if item["id"] == result["stage"])
            activate_stage_status(project, next_stage)
            result = harness.chat_status(run_dir)
        return _with_stage_packet(result)


@_serialized
def verify_run(arguments: dict[str, Any]) -> dict[str, Any]:
    run_dir = _run_dir(str(arguments.get("run_id", "")))
    receipt = run_dir / "execution-receipt.json"
    if not receipt.is_file():
        report = harness.evaluate(run_dir)
        return {"verified": False, "status": report["status"], "findings": report["findings"]}
    errors = execution_receipt_errors(receipt, ROOT)
    return {"verified": not errors, "receipt": str(receipt), "findings": errors,
            "image_provenance": "CLIENT_ATTESTED_NATIVE_TOOL" if load_json(run_dir / "run.json").get("ai_backend") == "session" else "SERVER_OBSERVED_API"}


def _schema(properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {"type": "object", "properties": properties, "required": required, "additionalProperties": False}


TOOLS: dict[str, tuple[str, dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]], dict[str, bool]]] = {
    "confirm_design": ("Record the single user approval of the complete reviewed desktop/mobile landing proposal before construction.", _schema({"run_id":{"type":"string"}, "status":{"type":"string","enum":["APPROVED","DELEGATED","ADJUST"]}, "user_signal":{"type":"string"}}, ["run_id","status","user_signal"]), confirm_design, {"readOnlyHint":False,"destructiveHint":False,"idempotentHint":False,"openWorldHint":False}),
    "start_landing": ("Start the only valid managed landing run. Call this before designing or coding.", _schema({"brief": {"type": "string"}, "scenario": {"type": "string"}}, []), start_landing, {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}),
    "get_stage": ("Read the single active stage plus its complete specialist contract, linked guidance, capabilities and current artifacts.", _schema({"run_id": {"type": "string"}}, ["run_id"]), get_stage, {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}),
    "list_files": ("List physical files in one managed landing project.", _schema({"run_id": {"type": "string"}}, ["run_id"]), list_files, {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}),
    "read_file": ("Read one bounded text artifact from the managed project.", _schema({"run_id": {"type": "string"}, "path": {"type": "string"}}, ["run_id", "path"]), read_file, {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}),
    "get_guidance": ("Load one conditional design capability only when its trigger applies to the active stage.", _schema({"run_id": {"type": "string"}, "capability_id": {"type": "string"}}, ["run_id", "capability_id"]), get_guidance, {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}),
    "write_file": ("Write only the artifact owned by the active stage, or implementation code when allowed.", _schema({"run_id": {"type": "string"}, "path": {"type": "string"}, "text": {"type": "string"}}, ["run_id", "path", "text"]), write_file, {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}),
    "generate_image": ("Make a paid OpenAI image-generation request and register the physical raster at the active image stage. Require user approval.", _schema({"run_id": {"type": "string"}, "prompt": {"type": "string"}, "path": {"type": "string"}, "asset_id": {"type": "string"}}, ["run_id", "prompt"]), generate_image, {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True}),
    "register_image": ("Register a physical raster import; this is not observed generation. SVG and CSS are rejected.", _schema({"run_id": {"type": "string"}, "path": {"type": "string"}, "asset_id": {"type": "string"}}, ["run_id", "path"]), register_image, {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}),
    "confirm_master": ("Record the user's sole artistic-master checkpoint signal.", _schema({"run_id": {"type": "string"}, "status": {"type": "string", "enum": ["APPROVED", "DELEGATED", "ADJUST"]}, "user_signal": {"type": "string"}}, ["run_id", "status", "user_signal"]), confirm_master, {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}),
    "advance_stage": ("Validate physical evidence, close the active stage and open exactly one successor. Never skip stages.", _schema({"run_id": {"type": "string"}}, ["run_id"]), advance_stage, {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}),
    "verify_run": ("Verify the final execution receipt. A landing is not harness-certified unless verified is true.", _schema({"run_id": {"type": "string"}}, ["run_id"]), verify_run, {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}),
}


def _result(value: dict[str, Any], error: bool = False) -> dict[str, Any]:
    images = value.pop("_images", [])
    resources = value.pop("_resources", [])
    return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}, *images, *resources], "structuredContent": value, "isError": error}


def dispatch(message: dict[str, Any]) -> dict[str, Any] | None:
    request_id = message.get("id")
    method = message.get("method")
    if request_id is None:
        return None
    try:
        if method == "initialize":
            result = {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "agentic-web-design-harness", "version": "1.0.0"},
                "instructions": (
                    "Before any landing research, design or code, call start_landing. "
                    "Act as the specialist in the returned stage_packet; it contains the complete active contract. "
                    "Use bounded files and never work ahead; then call advance_stage. The harness alone owns status and never skips. "
                    "Creative master and declared final imagery require physical raster generation/registration. "
                    "Only verify_run verified=true permits a claim of complete Agentic Web Design execution."
                ),
            }
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {"tools": [{"name": name, "title": name.replace("_", " ").title(), "description": spec[0], "inputSchema": spec[1], "annotations": spec[3]} for name, spec in TOOLS.items()]}
        elif method == "tools/call":
            params = message.get("params", {})
            name = params.get("name")
            if name not in TOOLS:
                raise ValueError(f"unknown tool {name}")
            result = _result(TOOLS[name][2](params.get("arguments", {})))
        else:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    except Exception as exc:
        if method == "tools/call":
            return {"jsonrpc": "2.0", "id": request_id, "result": _result({"error": str(exc)}, True)}
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32603, "message": str(exc)}}


def serve_stdio() -> None:
    # MCP is UTF-8 regardless of the Windows console's legacy code page.
    # Stage packets contain non-ASCII prose; ASCII-only health checks miss this.
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")
    for line in sys.stdin:
        try:
            message = json.loads(line)
            response = dispatch(message)
            if response is not None:
                print(json.dumps(response, ensure_ascii=False), flush=True)
        except Exception as exc:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}), flush=True)


def _loopback(host: str) -> bool:
    return host in {"127.0.0.1", "localhost", "::1"}


def serve_http(host: str, port: int, origins: set[str], token: str | None) -> None:
    if not _loopback(host) and not token:
        raise ValueError("non-loopback HTTP requires a bearer token")

    class Handler(BaseHTTPRequestHandler):
        def _reject(self, status: int, message: str) -> None:
            body = json.dumps({"error": message}).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            self._reject(405, "Streamable HTTP requests use POST /mcp")

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/mcp":
                self._reject(404, "not found")
                return
            origin = self.headers.get("Origin")
            if origin and origin not in origins:
                self._reject(403, "origin not allowed")
                return
            if token and self.headers.get("Authorization") != f"Bearer {token}":
                self._reject(401, "invalid bearer token")
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > MAX_REQUEST_BYTES:
                    raise ValueError("invalid request size")
                response = dispatch(json.loads(self.rfile.read(length)))
                if response is None:
                    self.send_response(202)
                    self.end_headers()
                    return
                body = json.dumps(response, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as exc:
                self._reject(400, str(exc))

        def log_message(self, _format: str, *_args: Any) -> None:
            return

    ThreadingHTTPServer((host, port), Handler).serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="Expose the landing harness over MCP.")
    parser.add_argument("--transport", choices=("stdio", "http"), default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--allow-origin", action="append", default=[])
    parser.add_argument("--token-env", default="AGENTIC_MCP_TOKEN")
    args = parser.parse_args()
    if args.transport == "stdio":
        serve_stdio()
        return 0
    token = os.getenv(args.token_env, "").strip() or None
    origins = set(args.allow_origin) | {f"http://localhost:{args.port}", f"http://127.0.0.1:{args.port}"}
    serve_http(args.host, args.port, origins, token)
    return 0


from harness_operations import operation_specs
TOOLS.update(operation_specs(sys.modules[__name__]))

if __name__ == "__main__":
    raise SystemExit(main())
