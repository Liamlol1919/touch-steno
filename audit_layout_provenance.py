#!/usr/bin/env python3
"""Audit whether layout.json still corresponds to the current hand profile.

This is a provenance check, not a geometry check. A layout generated from an
older measured profile is not automatically invalid, but it must not be
presented as a current result. Exit 0 = consistent, 2 = stale/provenance
mismatch, 1 = malformed input.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--layout", type=Path, default=Path("layout.json"))
    ap.add_argument("--profile", type=Path, default=Path("hand_profile.json"))
    ap.add_argument("--strict", action="store_true", help="return 2 on mismatch")
    args = ap.parse_args()
    try:
        layout = json.loads(args.layout.read_text())
        profile = json.loads(args.profile.read_text())
    except (OSError, ValueError) as exc:
        raise SystemExit(f"malformed input: {exc}")

    source = layout.get("geometry", {}).get("source")
    status = profile.get("_status", "unknown")
    embedded = layout.get("geometry", {}).get("hand_profile")
    issues = []
    if isinstance(status, str) and status.startswith("REJECTED") and isinstance(source, str) and "measured" in source.lower():
        issues.append("layout.json says 'measured hand profile', but hand_profile.json is REJECTED")
    if embedded is not None and embedded.get("_status") != profile.get("_status"):
        issues.append("embedded profile status differs from current hand_profile.json")
    if embedded is not None and embedded.get("_measured_by") != profile.get("_measured_by"):
        issues.append("embedded profile provenance differs from current hand_profile.json")

    print(f"layout source : {source}")
    print(f"profile status: {status}")
    if issues:
        for issue in issues:
            print(f"PROVENANCE WARNING: {issue}")
        print("Regenerate the layout only with an accepted profile, or label it as historical.")
    else:
        print("provenance consistent")
    if issues and args.strict:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
