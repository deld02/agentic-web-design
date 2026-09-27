"""Opt-in npm exports: isolated Docker or explicitly approved trusted local builds."""

import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tarfile
from uuid import uuid4

from validation_release_integrity import implementation_digest
from harness_local_build import local_capability, run_local


def build_capability():
    backend = os.getenv("AGENTIC_BUILD_BACKEND", "docker")
    if backend == "local":
        return local_capability()
    if backend != "docker":
        return {"available": False, "limitation": "Unknown build backend"}
    image = os.getenv("AGENTIC_BUILD_IMAGE", "")
    enabled = os.getenv("AGENTIC_ENABLE_BUILDS") == "1"
    docker = shutil.which("docker")
    valid = bool(re.fullmatch(r"[a-zA-Z0-9./:_-]+@sha256:[a-f0-9]{64}", image))
    available = False
    if enabled and docker and valid:
        try:
            available = subprocess.run([docker, "image", "inspect", image], capture_output=True,
                                       timeout=10, check=False).returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            pass
    return {"profile":"npm-static-export", "available":available,
            "enabled":enabled, "docker_available":bool(docker), "pinned_image":valid,
            "limitation":"Requires operator-provisioned Linux Node/npm image. No SSR, backend or deployment support."}


def checked_files(root):
    if not root.is_dir():
        raise ValueError("build source/export directory is missing")
    if root.is_symlink() or getattr(root.lstat(), "st_file_attributes", 0) & 1024:
        raise ValueError("linked build root is forbidden")
    files, total = [], 0
    for path in root.rglob("*"):
        info = path.lstat()
        if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
            raise ValueError("non-regular build files are forbidden")
        if path.is_symlink() or getattr(info, "st_file_attributes", 0) & 1024:
            raise ValueError("links/reparse points are forbidden in build files")
        if path.name.startswith(".env") or path.name in {".git", ".npmrc", "node_modules"}:
            raise ValueError("source/export contains secrets, configuration or dependency directories")
        if path.is_file():
            total += info.st_size
            files.append(path)
            if len(files) > 10000 or total > 150 * 1024 * 1024:
                raise ValueError("source/export exceeds file or byte budget")
    return files


def validate_source(source):
    files = checked_files(source)
    runtime = json.loads((source / "runtime.json").read_text(encoding="utf-8"))
    if runtime != {"target":"static", "external_services":[]}:
        raise ValueError("this adapter supports static output without required external services only")
    if any((source / name).exists() for name in ("dist", "out", ".next")):
        raise ValueError("frontend must contain source only, not previous build output")
    package = json.loads((source / "package.json").read_text(encoding="utf-8"))
    lock = json.loads((source / "package-lock.json").read_text(encoding="utf-8"))
    if not package.get("scripts", {}).get("build") or lock.get("lockfileVersion") not in {2, 3}:
        raise ValueError("requires build script and npm lockfile v2/v3")
    for item in lock.get("packages", {}).values():
        resolved = item.get("resolved", "")
        if item.get("link") or resolved and not resolved.startswith("https://registry.npmjs.org/"):
            raise ValueError("only public npm registry lock entries are supported")
    return files


def container_command(image, name, workspace, command, network):
    return [shutil.which("docker"), "run", "--detach", "--name", name, "--pull=never", "--read-only",
            "--user", "1000:1000", "--cap-drop=ALL", "--security-opt=no-new-privileges",
            "--memory=2g", "--memory-swap=2g", "--cpus=2", "--pids-limit=128",
            "--network", network, "--tmpfs", "/tmp:rw,nosuid,size=256m",
            "--tmpfs", "/work:rw,nosuid,size=1g,mode=1777",
            "--mount", f"type=bind,source={workspace},target=/source,readonly", "--workdir=/work",
            "--env", "HOME=/tmp", "--env", "NEXT_TELEMETRY_DISABLED=1",
            "--env", "CI=1", image, *command]


def run_container(command, name, log):
    # Output is discarded to avoid unbounded disk/log growth from project code.
    # Save the command's exit status, not arbitrary potentially sensitive output.
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            timeout=180, check=False)
    log.write_text(json.dumps({"exit_code":result.returncode, "container":name}), encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"container command failed ({result.returncode}); see {log.name}")


def copy_export(docker, name, output, destination):
    """Stream files only; never extract archive links or unbounded archive payloads."""
    import threading
    process = subprocess.Popen([docker, "cp", f"{name}:/work/{output}/.", "-"],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    timer = threading.Timer(30, process.kill)
    timer.start()
    total = count = 0
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|*") as archive:
            for item in archive:
                count += 1
                target = (destination / item.name).resolve()
                if ":" in item.name or "\\" in item.name or not target.is_relative_to(destination) or not (item.isfile() or item.isdir()):
                    raise ValueError("invalid export archive entry")
                total += item.size
                if count > 10000 or total > 150 * 1024 * 1024:
                    raise ValueError("export archive exceeds budget")
                if item.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open("xb") as stream:
                        shutil.copyfileobj(archive.extractfile(item), stream)
        if process.wait(timeout=5):
            raise RuntimeError("export copy failed")
    finally:
        timer.cancel()
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)
        process.stdout.close()


def build_export(project, output):
    if output not in {"dist", "out"}:
        raise ValueError("export directory must be dist or out")
    if not build_capability()["available"]:
        raise ValueError("build runtime unavailable: configure an explicit local or Docker backend")
    source = project / "frontend"
    files = validate_source(source)
    source_hash = implementation_digest(source)
    local = os.getenv("AGENTIC_BUILD_BACKEND", "docker") == "local"
    if local and os.getenv("AGENTIC_LOCAL_APPROVED_SHA256") != source_hash:
        raise ValueError("operator approval required: AGENTIC_LOCAL_APPROVED_SHA256=" + source_hash)
    attempts = project / "evidence/frontend-build-attempts.json"
    attempts.parent.mkdir(exist_ok=True)
    used = json.loads(attempts.read_text()).get("count", 0) if attempts.exists() else 0
    if used >= 4:
        raise ValueError("build budget exhausted: operator intervention required")
    attempts.write_text(json.dumps({"count":used + 1}), encoding="utf-8")
    attempt = uuid4().hex
    work = project.parent / "build-work" / attempt
    work.mkdir(parents=True)
    for path in files:
        target = work / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    image = None if local else os.environ["AGENTIC_BUILD_IMAGE"]
    docker, name = shutil.which("docker"), f"awd-{attempt}"
    exported = work.parent / f"{attempt}-export"
    exported.mkdir()
    if local:
        run_local(work, source_hash)
        for path in checked_files(work / output):
            target = exported / path.relative_to(work / output)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    else:
        docker_export(image, name, work, docker, attempt, output, exported)
    return install_export(project, source, source_hash, attempt, work, image, output, exported, local)


def docker_export(image, name, work, docker, attempt, output, exported):
    try:
        commands = [
            container_command(image, name, work, ["sleep", "600"], "bridge"),
            [docker, "exec", name, "sh", "-c", "cp -R /source/. /work/ && npm ci --ignore-scripts --no-audit --no-fund"],
            [docker, "network", "disconnect", "bridge", name],
            [docker, "exec", name, "npm", "--ignore-scripts", "run", "build"],
        ]
        for index, command in enumerate(commands):
            run_container(command, name, work.parent / f"{attempt}-{index}.json")
        copy_export(docker, name, output, exported)
    finally:
        stopped = subprocess.run([docker, "rm", "--force", name], capture_output=True, timeout=15, check=False)
        if stopped.returncode:
            raise RuntimeError(f"container cleanup failed: operator must inspect {name}")


def install_export(project, source, source_hash, attempt, work, image, output, exported, local):
    exported_files = checked_files(exported)
    if not (exported / "index.html").is_file():
        raise ValueError("build did not produce a static index.html; SSR is not supported")
    if implementation_digest(source) != source_hash:
        raise ValueError("source changed during build")
    # Preserve prior implementation and failed work; never recursively delete user files.
    destination = project / "implementation"
    if destination.exists():
        checked_files(destination)
    staged = project / f".export-{attempt}"
    staged.mkdir()
    for path in exported_files:
        target = staged / path.relative_to(exported)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    from harness_blender import preserve_blender_assets
    preserve_blender_assets(project, staged)
    backup = project / f".implementation-before-{attempt}"
    if destination.exists():
        destination.rename(backup)
    try:
        staged.rename(destination)
    except Exception:
        if backup.exists():
            backup.rename(destination)
        raise
    record = {"profile":"npm-static-export", "source_sha256":source_hash,
              "backend": "local" if local else "docker", "isolated": not local,
              "export_sha256":implementation_digest(destination), "image":image,
              "output":output, "work":str(work), "previous_export":str(backup) if backup.exists() else None}
    evidence = project / "evidence"
    evidence.mkdir(exist_ok=True)
    (evidence / "frontend-build.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


def build_freshness_errors(project):
    source = project / "frontend"
    if not source.exists():
        return []
    receipt = project / "evidence/frontend-build.json"
    if not receipt.is_file():
        return ["frontend source requires a successful managed build before advancing"]
    record = json.loads(receipt.read_text(encoding="utf-8"))
    if record.get("source_sha256") != implementation_digest(source):
        return ["frontend source changed: rebuild before advancing"]
    return []


def technology_execution_errors(project):
    text = (project / "technology-decision.md").read_text(encoding="utf-8")
    def field(name):
        values = re.findall(rf"^{name}:\s*([^\r\n]*)$", text, re.MULTILINE)
        return values[0].strip() if len(values) == 1 else ""
    profile = field("EXECUTION_PROFILE")
    if profile not in {"static-html", "npm-static-export"}:
        return ["select a supported EXECUTION_PROFILE; SSR requires a separate verified adapter"]
    if field("REQUIRED_EXTERNAL_SERVICES") != "NONE":
        return ["required external services need a verified adapter; do not silently substitute static output"]
    if profile == "npm-static-export":
        if not (project / "frontend").is_dir():
            return ["npm-static-export requires frontend source and managed build evidence"]
        return build_freshness_errors(project)
    if (project / "frontend").exists():
        return ["frontend source requires npm-static-export profile"]
    if not (project / "implementation/index.html").is_file():
        return ["static-html requires physical implementation/index.html"]
    return []
