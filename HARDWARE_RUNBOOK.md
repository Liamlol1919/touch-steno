# PTH-660 ROM Runbook

This is the next blocking experiment. It has not been executed in the current environment because no Wacom USB device is connected.

## Preconditions

- PTH-660 connected over USB; Bluetooth is a separate comparison run.
- Use a stable desk surface and the same right hand throughout.
- Heel of the hand stays off the pad.
- Do not run the optimiser until the profile is `ACCEPTED`.
- Record the exact command and UTC/local timestamp.

## Identify the device

```bash
python3 hardware_preflight.py
lsusb | grep -i -E 'wacom|056a'
python3 rom_capture.py --self-test   # synthetic; does not open the device
python3 - <<'PY'
from evdev import InputDevice, list_devices
for node in list_devices():
    if "wacom" in InputDevice(node).name.lower():
        print(node, InputDevice(node).name)
PY
```

The `--self-test` uses synthetic events and does not validate the physical pad.
Confirm the live node with `evtest` or a short Python `InputDevice` capability
dump before starting the guided sequence.

## Run the guided capture

```bash
python3 rom_capture.py --device /dev/input/eventN --out-dir messung/rom
```

The reader will ask for Enter before each cue. The heel remains in the air; only
the thumb or index touches the pad. The reader records raw per-contact JSONL
before analysis, so a failed analysis does not destroy the raw evidence.

## Acceptance gates

Do not accept the profile unless all are true:

1. `rom_capture.py --self-test` passes.
2. The still-phase stray is far below the cued-phase spread.
3. The hand has no accidental palm/forearm contact.
4. The thumb-only and index phases are distinguishable.
5. The generated JSON contains `_status: ACCEPTED` or
   `ACCEPTED_WITH_DECLARED_FALLBACKS`.
6. `audit_layout_provenance.py --strict` passes after a new layout is generated.

## If a capture is rejected

Retain the raw JSONL and the rejection reason. Do not delete the rejected
profile; move it to an archive name and start a new capture. The optimiser
refuses `REJECTED` profiles by default and requires an explicit diagnostic
source label for any temporary run.

## After acceptance

```bash
python3 layout_optimizer.py --hand-profile messung/rom/hand_profile.json \
  --out layout-candidate.json
python3 audit_layout_provenance.py \
  --layout layout-candidate.json \
  --profile messung/rom/hand_profile.json --strict
# only after the strict audit returns 0:
cp layout-candidate.json layout.json
python3 run_core_checks.py
```

Generate a candidate first; do not overwrite `layout.json` before the strict audit
succeeds. Only the last command returning 0 means the offline core gates are green. WPM
values remain model outputs until a separate typing session measures them.
