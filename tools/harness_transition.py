"""Recoverable metadata transitions. User assets are never rolled back."""

from contextlib import contextmanager
from pathlib import Path
import base64
import json
import os
import sqlite3


TRANSITION_FILES = (
    "run.json", "events.jsonl", "control/chat-snapshot.json",
    "project/status.json", "project/qa-release.md", "report.json", "report.md",
    "quality-scan.json", "execution-receipt.json",
    "control/design-plans.json",
)


@contextmanager
def server_lock(root: Path):
    """Serialize cooperating server processes, including recovery after a crash."""
    root.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(root / ".runtime-lock.sqlite", timeout=30)
    try:
        connection.execute("BEGIN IMMEDIATE")
        yield
    finally:
        connection.rollback()
        connection.close()


def recover_transition(run_dir: Path):
    root = run_dir.resolve()
    journal = root / "control/transition.json"
    if not journal.exists():
        return
    data = json.loads(journal.read_text(encoding="utf-8"))
    if set(data) not in (set(TRANSITION_FILES), set(TRANSITION_FILES) - {"control/design-plans.json"}):
        raise ValueError("invalid transition journal; manual recovery required")
    # Validate every target and decode every backup before touching any file.
    originals = {}
    for relative, encoded in data.items():
        path = root / relative
        if path.resolve() != path:
            raise ValueError("transition metadata must not traverse links")
        originals[path] = base64.b64decode(encoded, validate=True) if encoded is not None else None
    for path, content in originals.items():
        if content is None:
            if path.is_file():
                path.unlink()
        else:
            path.write_bytes(content)
    journal.unlink()


@contextmanager
def transition_rollback(run_dir: Path):
    root = run_dir.resolve()
    recover_transition(root)
    originals = {}
    for relative in TRANSITION_FILES:
        path = root / relative
        if path.resolve() != path:
            raise ValueError("transition metadata must not traverse links")
        originals[path] = path.read_bytes() if path.is_file() else None
    journal = root / "control/transition.json"
    journal.parent.mkdir(parents=True, exist_ok=True)
    temporary = journal.with_suffix(".tmp")
    data = {path.relative_to(root).as_posix(): base64.b64encode(content).decode("ascii")
            if content is not None else None for path, content in originals.items()}
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(data, stream)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, journal)
    try:
        yield
    except Exception:
        recover_transition(root)
        raise
    else:
        journal.unlink()
