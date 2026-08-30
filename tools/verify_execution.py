#!/usr/bin/env python3
"""Verify that a delivered landing belongs to a complete managed harness run."""

from pathlib import Path
import argparse

from project_validation import ROOT
from validation_execution_receipt import execution_receipt_errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify an Agentic Web Design execution receipt.")
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    errors = execution_receipt_errors(args.receipt, ROOT)
    if errors:
        print("FAIL — unmanaged, incomplete or stale execution")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS — managed execution, 13/13 stages, G0-G5 approved, delivery digest matches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
