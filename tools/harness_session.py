"""Subscription-backed execution. No API-key fallback and no fabricated tool calls."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def session_mode():
    mode = os.getenv("AGENTIC_AI_BACKEND", "api")
    if mode not in {"api", "session"}:
        raise ValueError("unknown AGENTIC_AI_BACKEND")
    return mode == "session"


def codex_status():
    executable = os.getenv("AGENTIC_CODEX") or shutil.which("codex")
    if not executable:
        return {"available": False, "chatgpt_login": False}
    env = {k: v for k, v in os.environ.items() if k not in {"OPENAI_API_KEY", "CODEX_API_KEY"}}
    try:
        result = subprocess.run([executable, "login", "status"], env=env,
                                capture_output=True, text=True, timeout=15, check=False)
        logged = result.returncode == 0 and "chatgpt" in (result.stdout + result.stderr).lower()
    except (OSError, subprocess.TimeoutExpired):
        logged = False
    return {"available": True, "chatgpt_login": logged}


def subscription_review(packet, images, schema, evidence_names):
    if not codex_status()["chatgpt_login"]:
        raise RuntimeError("Run codex login with your ChatGPT account; API-key login is not accepted")
    executable = os.getenv("AGENTIC_CODEX") or shutil.which("codex")
    # Fresh cwd and conversation, with attached evidence only. No resume/fork.
    work = Path(tempfile.mkdtemp(prefix="awd-review-"))
    schema_path, answer = work / "schema.json", work / "answer.json"
    schema_path.write_text(json.dumps(schema), encoding="utf-8")
    command = [executable, "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
               "--sandbox", "read-only", "-c", 'forced_login_method="chatgpt"',
               "--cd", str(work), "--json", "--output-schema", str(schema_path),
               "--output-last-message", str(answer)]
    for image in images:
        command.extend(["--image", str(image)])
    command.append("-")
    env = {k: v for k, v in os.environ.items() if k not in {"OPENAI_API_KEY", "CODEX_API_KEY", "CONTROL_PLANE_API_KEY"}}
    from harness_review import REVIEW_INSTRUCTIONS
    prompt = (REVIEW_INSTRUCTIONS + " Do not modify files, use network or inspect other conversations.\n" +
              json.dumps(packet, ensure_ascii=False) + "\nExact image evidence labels in attachment order: " + json.dumps(evidence_names))
    process = subprocess.Popen(command, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, text=True, encoding="utf-8")
    try:
        stdout, _ = process.communicate(prompt, timeout=180)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate(timeout=10)
        raise RuntimeError("Codex review timed out; no approval recorded")
    if process.returncode or not answer.is_file():
        raise RuntimeError("Codex review failed; no API fallback or approval")
    events = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    thread = next((e.get("thread_id") for e in events if e.get("type") == "thread.started"), None)
    if not thread or not any(e.get("type") == "turn.completed" for e in events):
        raise ValueError("Codex review lacks completion evidence")
    return {"status": "completed", "id": thread,
            "output": [{"content": [{"type": "output_text", "text": answer.read_text(encoding="utf-8")}]}]}


def native_image_valid(project, event):
    if event.get("tool") != "SESSION_IMAGE_RESULT" or event.get("provenance") != "CLIENT_ATTESTED":
        return False
    try:
        run = json.loads((project.parent / "run.json").read_text(encoding="utf-8"))
        path = (project / event["file"]).resolve()
        if run.get("ai_backend") != "session" or not path.is_relative_to(project.resolve()):
            return False
        from harness_media import inspect_raster
        metadata = inspect_raster(path.read_bytes(), path.suffix)
        return bool(event.get("tool_call_reference")) and metadata["sha256"] == event.get("sha256")
    except (OSError, ValueError, KeyError, TypeError):
        return False


def register_session_image(api, arguments):
    run, active, project = api._project_and_stage(arguments["run_id"])
    if api.load_json(run / "run.json").get("ai_backend") != "session":
        raise ValueError("session image registration requires a session-mode run")
    reference = str(arguments.get("tool_call_reference", "")).strip()
    if not 8 <= len(reference) <= 500:
        raise ValueError("provide the actual native image tool result reference; a prompt is not a result")
    path = api._bounded_project_file(project, arguments["path"])
    from harness_media import inspect_raster
    metadata = inspect_raster(path.read_bytes(), path.suffix)
    result = api.harness.confirm_chat_image(run, path, arguments.get("asset_id"))
    api.harness.append_event(run, {"event": "tool_call", "stage": active["stage"], "agent": active["agent"],
        "tool": "SESSION_IMAGE_RESULT", "target": arguments.get("asset_id"),
        "file": path.relative_to(project).as_posix(), "sha256": metadata["sha256"],
        "tool_call_reference": reference, "provenance": "CLIENT_ATTESTED"})
    return result | {"provenance": "CLIENT_ATTESTED", "generation_observed": False,
                     "instruction": "Physical raster checked. Native tool origin is client-attested, not observed by the server."}
