#!/usr/bin/env python3
"""Command-line adapter for the evaluation harness library."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import ModuleType


def _parser(event_types: set[str]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run and inspect the Agentic Web Design harness.")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--scenario", required=True)
    init.add_argument("--runs-root", type=Path)
    init.add_argument("--run-id")
    record = sub.add_parser("record")
    record.add_argument("--run-dir", required=True, type=Path)
    record.add_argument("--event", required=True, choices=sorted(event_types))
    record.add_argument("--stage", required=True)
    record.add_argument("--agent", required=True)
    record.add_argument("--tool")
    record.add_argument("--target")
    record.add_argument("--progress-key")
    record.add_argument("--at")
    for command in ("evaluate", "packet", "chat-status", "chat-next"):
        child = sub.add_parser(command)
        child.add_argument("--run-dir", required=True, type=Path)
    capture = sub.add_parser("capture")
    capture.add_argument("--run-dir", required=True, type=Path)
    capture.add_argument("--url", required=True)
    capture.add_argument("--label", default="final")
    execute = sub.add_parser("execute")
    execute.add_argument("--run-dir", required=True, type=Path)
    execute.add_argument("executor", nargs=argparse.REMAINDER)
    active = sub.add_parser("run")
    active.add_argument("--run-dir", required=True, type=Path)
    active.add_argument("--until")
    active.add_argument("executor", nargs=argparse.REMAINDER)
    doctor = sub.add_parser("doctor")
    doctor.add_argument("executor", nargs=argparse.REMAINDER)
    chat_start = sub.add_parser("chat-start")
    source = chat_start.add_mutually_exclusive_group(required=True)
    source.add_argument("--scenario")
    source.add_argument("--brief-file", type=Path)
    chat_start.add_argument("--runs-root", type=Path)
    chat_start.add_argument("--run-id")
    chat_image = sub.add_parser("chat-image")
    chat_image.add_argument("--run-dir", required=True, type=Path)
    chat_image.add_argument("--file", required=True, type=Path)
    return parser


def _executor(args: argparse.Namespace) -> list[str]:
    return args.executor[1:] if args.executor[:1] == ["--"] else args.executor


def run_cli(api: ModuleType) -> int:
    """Parse arguments and dispatch to the supplied harness module."""
    args = _parser(api.EVENT_TYPES).parse_args()
    if args.command == "init":
        print(api.create_run(args.scenario, args.runs_root, args.run_id))
        return 0
    if args.command == "record":
        payload = {
            key: value
            for key, value in {
                "event": args.event,
                "stage": args.stage,
                "agent": args.agent,
                "tool": args.tool,
                "target": args.target,
                "progress_key": args.progress_key,
                "at": args.at,
            }.items()
            if value is not None
        }
        print(json.dumps(api.append_event(args.run_dir, payload), ensure_ascii=False))
        return 0
    if args.command == "evaluate":
        report = api.evaluate(args.run_dir)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["status"] == "PASS" else 1
    if args.command == "capture":
        for output in api.capture(args.run_dir, args.url, args.label):
            print(output)
        return 0
    if args.command == "packet":
        print(api.create_packet(args.run_dir))
        return 0
    if args.command == "doctor":
        report = api.executor_doctor(_executor(args) or None)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["status"] == "READY" else 1
    if args.command == "chat-start":
        brief = args.brief_file.read_text(encoding="utf-8") if args.brief_file else None
        result = api.start_chat_run(args.scenario, args.runs_root, args.run_id, brief)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.command == "chat-status":
        print(json.dumps(api.chat_status(args.run_dir), indent=2, ensure_ascii=False))
        return 0
    if args.command == "chat-image":
        print(json.dumps(api.confirm_chat_image(args.run_dir, args.file), indent=2, ensure_ascii=False))
        return 0
    if args.command == "chat-next":
        result = api.advance_chat_run(args.run_dir)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] != "FAILED" else 1
    if args.command == "run":
        result = api.run_active(args.run_dir, _executor(args), args.until)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] in {"COMPLETE", "PARTIAL", "NEEDS_USER"} else 1
    return api.execute(args.run_dir, _executor(args))
