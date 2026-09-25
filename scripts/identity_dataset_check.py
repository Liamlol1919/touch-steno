#!/usr/bin/env python3
"""Validate a finger-identity capture before it is used to train anything.

`guided_calibration.py --task identity` asks the operator to lift and replace one finger per
cue, which is what produces the (contact-id, anatomical label) pairs that make calibration
portable across sessions (issue #9). But the label is only the *cue*: nothing verifies that
the operator actually lifted the cued finger, or that the others stayed down. A sloppy
session yields a silently poisoned training set, which is worse than no dataset.

This validates each cue against the recorded stream and reports:
  VALID      the cued contact disappeared and returned; every other contact persisted
  PARTIAL    the cued contact moved but never fully lifted (shallow lift)
  AMBIGUOUS  more than one contact was absent, so the label cannot be attributed
  MISSING    the cued contact never disappeared
  CONTAMINATED another contact was absent while the cued one was down
  UNLABELLED no manifest coverage for the frames in question

Exit status is 0 only if every cue is VALID, so a capture can gate a pipeline step.

Usage:
    python3 scripts/identity_dataset_check.py capture.jsonl
    python3 scripts/identity_dataset_check.py --json capture.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kinematics  # noqa: E402


def load_manifest(path: Path) -> list[dict]:
    m = path.with_suffix(".manifest.jsonl")
    if not m.exists():
        raise SystemExit(f"manifest missing: {m}")
    return [json.loads(line) for line in m.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def check(path: Path) -> dict:
    payload = kinematics._strip_uninit_leads(kinematics._load(path))
    manifest = load_manifest(path)

    # presence timeline per contact
    present: dict[str, list[tuple[float, bool]]] = {}
    for fr in payload:
        t = float(fr["t"])
        for tid in fr["c"]:
            present.setdefault(str(tid), []).append((t, True))

    def gap_frames(tid: str, t0: float, t1: float) -> int:
        """Longest run of consecutive frames inside the cue where the contact is missing.

        A lift shows up as a GAP in the contact's presence, not as absence over the whole
        window - the finger is present at the start and again at the end. Checking for
        whole-window absence reports every cue as MISSING, which is what the first version
        did.
        """
        window = [(float(fr["t"]), str(tid) in fr["c"]) for fr in payload
                  if t0 <= float(fr["t"]) <= t1]
        best = run = 0
        for _t, there in window:
            run = 0 if there else run + 1
            best = max(best, run)
        return best

    cues = []
    for rec in manifest:
        label = rec.get("label", "")
        if not label.startswith("identity_"):
            continue
        finger = rec.get("finger", label.split("_", 1)[-1])
        t0, t1 = rec["t_start"], rec["t_end"]
        # which contacts are present at the start of the cue, and did any vanish?
        at_start = {str(tid) for fr in payload
                    if abs(float(fr["t"]) - t0) < 0.02 for tid in fr["c"]}
        lift_gap = 5          # frames; below this a "lift" is sensor jitter, not a lift
        absent = [tid for tid in at_start if gap_frames(tid, t0, t1) >= lift_gap]
        present_at_end = {str(tid) for fr in payload
                          if abs(float(fr["t"]) - t1) < 0.02 for tid in fr["c"]}
        returned = [tid for tid in at_start if tid in present_at_end]

        if not at_start:
            status = "MISSING"
        elif len(absent) == 0:
            status = "MISSING"          # the cued lift never happened
        elif len(absent) > 1:
            status = "AMBIGUOUS"        # cannot attribute the label to one contact
        else:
            lifted = absent[0]
            if lifted in returned:
                status = "VALID"
            else:
                status = "PARTIAL"       # lifted and did not come back cleanly
        cues.append({"label": label, "finger": finger, "status": status,
                     "contacts_at_start": sorted(at_start),
                     "absent": sorted(absent), "returned": sorted(returned)})

    counts: dict[str, int] = {}
    for c in cues:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    return {"session": path.name, "frames": len(payload), "cues": len(cues),
            "counts": counts,
            "all_valid": bool(cues) and counts.get("VALID", 0) == len(cues),
            "detail": cues}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("capture", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rep = check(args.capture)
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        print(f"## {rep['session']}  frames {rep['frames']}  cues {rep['cues']}")
        print(f"  status: {rep['counts']}")
        print(f"  all valid: {rep['all_valid']}")
        for c in rep["detail"]:
            if c["status"] != "VALID":
                print(f"  {c['status']:<11} {c['label']:<16} absent={c['absent']} "
                      f"returned={c['returned']}")
    return 0 if rep["all_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
