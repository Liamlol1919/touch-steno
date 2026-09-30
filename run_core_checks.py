#!/usr/bin/env python3
"""Run the repository's offline core checks.

Exit 0 = all selected checks passed. Exit 1 = a check failed. Exit 2 = stale
layout provenance (unless --allow-stale-layout is explicitly passed).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(name: str, args: list[str]) -> tuple[str, int]:
    print(f"\n== {name} ==", flush=True)
    proc = subprocess.run([sys.executable, *args], cwd=ROOT, text=True)
    return name, proc.returncode


def overall_exit(results: list[tuple[str, int]]) -> int:
    """Technical failures (1) take precedence over stale provenance (2)."""
    if any(code not in (0, 2) for _, code in results):
        return 1
    if any(code == 2 for _, code in results):
        return 2
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-stale-layout", action="store_true",
                    help="treat the known rejected-profile layout mismatch as a warning")
    ap.add_argument("--require-hardware", action="store_true",
                    help="also require a visible Wacom/Intuos input device")
    args = ap.parse_args()
    results = [
        run("layout optimiser offline self-test", ["layout_optimizer.py", "--self-test", "--offline", "--quiet"]),
        run("hand reader synthetic self-test", ["rom_capture.py", "--self-test"]),
    ]
    audit_args = ["audit_layout_provenance.py"]
    if args.allow_stale_layout:
        print("\n== layout provenance (warning allowed) ==", flush=True)
        audit = subprocess.run([sys.executable, *audit_args], cwd=ROOT, text=True)
        results.append(("layout provenance", audit.returncode))
    else:
        results.append(run("layout provenance strict", [*audit_args, "--strict"]))
    if args.require_hardware:
        results.append(run("hardware preflight", ["hardware_preflight.py"]))
    technical_failures = [name for name, code in results if code not in (0, 2)]
    code = overall_exit(results)
    if technical_failures:
        print("\nFAILED: " + ", ".join(technical_failures), file=sys.stderr)
    elif code == 2:
        print("\nStale layout provenance; measurement replacement required.", file=sys.stderr)
    if code:
        return code
    print("\nAll offline core checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
