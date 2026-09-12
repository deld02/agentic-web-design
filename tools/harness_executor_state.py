"""Validate executor output without delegating official state ownership."""

from stage_orchestrator import complete_stage_status


def validate_executor_state(run_dir, stage, original, code, stdout, stderr, changed, validate):
    state = run_dir / "project/status.json"
    if not state.is_file() or state.read_bytes() != original:
        state.write_bytes(original)
        return ["executor modified official state; only the harness may transition it"]
    if code != 0:
        return [f"executor exited {code}: {(stderr or stdout).strip()[:1000]}"]
    accepted = False
    try:
        complete_stage_status(run_dir / "project", stage, changed)
        errors = validate()
        accepted = not errors
        return errors
    except ValueError as exc:
        return [str(exc)]
    finally:
        if not accepted:
            state.write_bytes(original)
