"""Render a static/exported landing without running project shell commands."""

from __future__ import annotations

from pathlib import Path
import json
import os
import shutil
import subprocess
from uuid import uuid4
from hashlib import sha256

from validation_release_integrity import implementation_digest


def render_static(project: Path, implementation: Path, entry: str, scenes: list[str], actions: list[dict] | None = None) -> dict:
    actions = actions or []
    if len(actions) > 12 or any(action.get("type") not in {"click", "hover", "tab", "reduced-motion"} for action in actions):
        raise ValueError("provide at most 12 supported interactions")
    if any(action["type"] in {"click","hover"} and (not isinstance(action.get("selector"), str) or not 1 <= len(action["selector"]) <= 200) for action in actions):
        raise ValueError("click/hover require a bounded selector")
    target = (implementation / entry).resolve()
    if not target.is_file() or target.suffix.lower() != ".html" or not target.is_relative_to(implementation):
        raise ValueError("render entry must be physical HTML inside implementation")
    output = project / "evidence" / f"render-{uuid4().hex[:12]}"
    output.mkdir(parents=True)
    before = implementation_digest(implementation)
    request = {"root": str(implementation), "entry": target.relative_to(implementation).as_posix(),
               "output": str(output), "scenes": scenes, "actions":actions}
    # Do not pass API credentials or arbitrary environment variables to Node or
    # browser subprocesses. No npm install/build/script from project is executed.
    env = {key: os.environ[key] for key in ("SystemRoot", "WINDIR", "TEMP", "TMP", "PATH", "ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA",
           "NODE_PATH", "PLAYWRIGHT_BROWSERS_PATH", "AGENTIC_BROWSER_CHANNEL") if key in os.environ}
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js is required for managed rendering")
    result = subprocess.run([node, str(Path(__file__).with_name("render_landing.cjs"))],
        input=json.dumps(request), capture_output=True, text=True, encoding="utf-8", env=env, timeout=90, check=False)
    if result.returncode:
        raise RuntimeError("Render failed: " + result.stderr[:2000])
    report = json.loads(result.stdout)
    if before != implementation_digest(implementation):
        raise ValueError("implementation changed during capture; render is stale")
    for capture in report["captures"]:
        capture["file"] = Path(capture["file"]).relative_to(project).as_posix()
    report["image_sha256"] = {capture["file"]:sha256((project / capture["file"]).read_bytes()).hexdigest() for capture in report["captures"]}
    report["source_sha256"] = before
    report["entry"] = entry
    (output / "capture.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
