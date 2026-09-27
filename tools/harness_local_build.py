"""Explicitly trusted host builds. This is NOT an isolation boundary."""
import os
from pathlib import Path
import shutil
import subprocess


def local_capability():
    node = os.getenv("AGENTIC_NODE") or shutil.which("node")
    cli = os.getenv("AGENTIC_NPM_CLI")
    if not cli and node:
        cli = str(Path(node).parent / "node_modules/npm/bin/npm-cli.js")
    enabled = os.getenv("AGENTIC_ENABLE_BUILDS") == "1"
    return {"profile": "npm-static-export", "backend": "local", "enabled": enabled,
            "available": bool(enabled and node and cli and Path(node).is_file() and Path(cli).is_file()),
            "node": node, "npm_cli": cli,
            "limitation": "Trusted host execution, not sandboxed. Each source digest requires operator approval. Static export only."}


def run_local(work, source_hash):
    if os.getenv("AGENTIC_LOCAL_APPROVED_SHA256") != source_hash:
        raise ValueError("local build needs operator approval: AGENTIC_LOCAL_APPROVED_SHA256=" + source_hash)
    capability = local_capability()
    if not capability["available"]:
        raise ValueError("local Node/npm runtime unavailable")
    home = work / ".build-home"
    home.mkdir()
    # Do not inherit provider credentials or the user's npm configuration.
    env = {key: value for key, value in os.environ.items()
           if key.upper() in {"SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT"}}
    env.update(PATH=str(Path(capability["node"]).parent) + os.pathsep + os.defpath,
               HOME=str(home), USERPROFILE=str(home), TEMP=str(home), TMP=str(home),
               CI="1", NEXT_TELEMETRY_DISABLED="1", npm_config_cache=str(home / "cache"),
               npm_config_userconfig=str(home / "npmrc"), npm_config_globalconfig=str(home / "global-npmrc"))
    for arguments in (["ci", "--ignore-scripts", "--no-audit", "--no-fund"],
                      ["--ignore-scripts", "run", "build"]):
        process = subprocess.Popen([capability["node"], capability["npm_cli"], *arguments],
                                   cwd=work, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            code = process.wait(timeout=180)
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                subprocess.run([str(Path(os.environ["SYSTEMROOT"]) / "System32/taskkill.exe"),
                                "/PID", str(process.pid), "/T", "/F"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15, check=False)
            process.kill()
            process.wait(timeout=10)
            raise RuntimeError("local build timed out; inspect residual processes before retrying")
        if code:
            raise RuntimeError(f"local npm command failed ({code}); work preserved at {work}")
