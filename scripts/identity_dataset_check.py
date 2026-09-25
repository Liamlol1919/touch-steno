#!/usr/bin/env python3
"""Validate a finger-identity capture before it is used to train anything.

`guided_calibration.py --task identity` asks the operator to lift and replace one finger per
cue, which is what produces the (contact-id, anatomical label) pairs that make calibration
portable across sessions (issue #9). The manifest label is only a cue: it does not prove which
tracking ID belonged to that anatomical finger. This validator therefore requires an explicit
operator-confirmed mapping before a cue can pass as VALID.

This validates each cue against the recorded stream and reports:
  VALID        the cued contact disappeared and returned; every other contact persisted
  PARTIAL      the cued contact moved but never fully lifted (shallow lift)
  AMBIGUOUS    more than one contact was absent, so the label cannot be attributed
  MISSING      the cued contact never disappeared
  CONTAMINATED another contact was absent while the cued one was down
  UNVERIFIED   a unique lift was observed but no explicit contact-to-finger mapping was supplied

Exit status is 0 only if every cue is VALID, so a capture can gate a pipeline step.

Usage:
    python3 scripts/identity_dataset_check.py capture.jsonl
    python3 scripts/identity_dataset_check.py --json capture.jsonl
    python3 scripts/identity_dataset_check.py --mapping identity-map.json capture.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics  # noqa: E402
import session_manifest  # noqa: E402


def load_mapping(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("identity mapping must be a JSON object")
    return {str(finger): str(tid) for finger, tid in data.items()}




def load_manifest(path: Path) -> list[dict]:
    m = path.with_suffix(".manifest.jsonl")
    if not m.exists():
        raise SystemExit(f"manifest missing: {m}")
    return session_manifest.load(m)


def _normalise_mapping(mapping: dict | None) -> dict[str, str]:
    return {str(finger): str(tid) for finger, tid in (mapping or {}).items()}


def check(path: Path, contact_map: dict | None = None) -> dict:
    payload = kinematics._strip_uninit_leads(kinematics._load(path))
    manifest = load_manifest(path)
    mapping = _normalise_mapping(contact_map)

    cues = []
    for rec in manifest:
        label = rec.get("label", "")
        if not label.startswith("identity_"):
            continue
        finger = rec.get("finger", label.split("_", 1)[-1])
        t0, t1 = rec["t_start"], rec["t_end"]
        at_start = {str(tid) for fr in payload
                    if abs(float(fr["t"]) - t0) < 0.02 for tid in fr["c"]}

        def gap_frames(tid: str) -> int:
            run = best = 0
            for fr in payload:
                t = float(fr["t"])
                if t0 <= t <= t1:
                    run = 0 if str(tid) in fr["c"] else run + 1
                    best = max(best, run)
            return best

        lift_gap = 5
        absent = [tid for tid in at_start if gap_frames(tid) >= lift_gap]
        present_at_end = {str(tid) for fr in payload
                          if abs(float(fr["t"]) - t1) < 0.02 for tid in fr["c"]}
        returned = [tid for tid in at_start if tid in present_at_end]
        observed_tid = absent[0] if len(absent) == 1 else None
        attributed_tid = mapping.get(str(finger))
        reason = None

        if not at_start:
            status = "MISSING"
            reason = "no contact present at cue start"
        elif not absent:
            status = "MISSING"
            reason = "no contact lifted for the minimum gap"
        elif len(absent) > 1:
            status = "AMBIGUOUS"
            reason = "more than one contact was absent"
        elif attributed_tid is None:
            status = "UNVERIFIED"
            reason = "no explicit operator-confirmed finger-to-tracking-ID mapping"
        elif attributed_tid not in at_start:
            status = "MISSING"
            reason = "attributed contact was not present at cue start"
        elif observed_tid != attributed_tid:
            status = "CONTAMINATED"
            reason = "a different contact lifted than the attributed finger"
        elif observed_tid in returned:
            status = "VALID"
        else:
            status = "PARTIAL"
            reason = "attributed contact did not return before cue end"
        cues.append({"label": label, "finger": finger, "status": status,
                     "contacts_at_start": sorted(at_start), "absent": sorted(absent),
                     "returned": sorted(returned), "observed_tid": observed_tid,
                     "attributed_tid": attributed_tid, "reason": reason})

    counts: dict[str, int] = {}
    for cue in cues:
        counts[cue["status"]] = counts.get(cue["status"], 0) + 1
    return {"session": path.name, "frames": len(payload), "cues": len(cues),
            "mapping_provided": bool(mapping), "counts": counts,
            "all_valid": bool(cues) and counts.get("VALID", 0) == len(cues),
            "detail": cues}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("capture", type=Path)
    ap.add_argument("--mapping", type=Path,
                    help="operator-confirmed JSON object: finger name -> tracking ID")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    mapping = load_mapping(args.mapping) if args.mapping else None
    rep = check(args.capture, mapping)
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        print(f"## {rep['session']}  frames {rep['frames']}  cues {rep['cues']}")
        print(f"  mapping supplied: {rep['mapping_provided']}")
        print(f"  status: {rep['counts']}")
        print(f"  all valid: {rep['all_valid']}")
        for cue in rep["detail"]:
            if cue["status"] != "VALID":
                print(f"  {cue['status']:<11} {cue['label']:<16} "
                      f"observed={cue['observed_tid']} "
                      f"attributed={cue['attributed_tid']} reason={cue['reason']}")
    return 0 if rep["all_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
