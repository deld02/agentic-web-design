import hashlib


def add_capability_rows(text, rows):
    marker = "|---|---|---|---|---|"
    pos = text.find(marker, text.find("## Design capability log"))
    payload = "".join(f"\n| {capability} | {mode} | required by registry | applied from routed reference | PASS |" for capability, mode in rows)
    return text[:pos] + marker + payload + text[pos + len(marker):]


def add_content_lock_fixture(text):
    marker = "|---|---|---|---|---|"
    pos = text.find(marker, text.find("## Content lock"))
    rows = (
        "\n| CNT-001 | HERO_THESIS | Invisible expertise, made concrete | REQUIRED | SCN-001 hero |"
        "\n| CNT-002 | PRIMARY_CTA | Request the diagnostic | REQUIRED | SCN-003 action |"
    )
    return text[:pos] + marker + rows + text[pos + len(marker):]


def add_release_integrity_fixture(repo, run):
    site = repo / "site-test"
    if not site.is_dir():
        return
    digest = hashlib.sha256()
    for source in sorted(path for path in site.rglob("*") if path.is_file()):
        relative = source.relative_to(site).as_posix()
        file_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        digest.update(relative.encode("utf-8") + b"\0" + file_hash.encode("ascii") + b"\n")
    source_digest = digest.hexdigest()
    evidence = repo / "projects/test-project/evidence"
    rows = []
    for scene in ("SCN-001", "SCN-002", "SCN-003"):
        for viewport in ("DESKTOP", "MOBILE"):
            name = f"runtime-{scene.lower()}-{viewport.lower()}.png"
            (evidence / name).write_bytes(b"\x89PNG\r\n\x1a\nsynthetic-runtime")
            rows.append(
                f"| {scene} | {viewport} | Scroll through scene boundary | "
                f"Intended state remains legible and causal | Final state observed without clipping | "
                f"evidence/{name} | PASS | sha256:{source_digest} |"
            )
    qa = repo / "projects/test-project/qa-release.md"
    text = qa.read_text(encoding="utf-8")
    marker = "|---|---|---|---|---|---|---|---|"
    pos = text.find(marker, text.find("### Runtime traversal"))
    text = text[:pos] + marker + "\n" + "\n".join(rows) + text[pos + len(marker):]
    qa.write_text(text, encoding="utf-8")
    result = run(
        repo, "tools/validation_release_integrity.py", "--project-dir", "projects/test-project",
        "--implementation-root", "site-test",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
