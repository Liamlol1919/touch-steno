# Next physical session

Run from the repository root. Do not touch the pad until the startup gate has passed.

## 1. Preconditions

Connect the Wacom tablet. Confirm that its evdev node exists and that evdev lists a Wacom device:

```bash
test -e /dev/input/event19 && grep -i wacom /proc/bus/input/devices
```

`/dev/input/event19` existing is necessary, but not sufficient. The startup smoke below must also pass, including its real device read.

## 2. Startup gate

```bash
python3 scripts/startup_smoke.py
```

- **PASS** — the checked property completed successfully. This is a startup result, not a measurement.
- **FAIL** — the checked property did not complete successfully. Fix it before starting the session.
- **UNVERIFIED** — the property was not exercised; for hardware, no real open/read was proved. It becomes verified only by a first real read, either the smoke's device check or the corresponding instrument's live capture.

There must be no FAIL. With the tablet connected, no hardware path may remain UNVERIFIED at the gate.

## 3. Instruments, in order

### 1. Field gesture control

```bash
python3 scripts/field_gesture_probe.py --device /dev/input/event19 --seconds 4 --reps 3 --out messung/field.jsonl
```

This takes about 2 minutes (30 cues at 4 seconds) plus setup. It captures cued whole-hand shapes, including `STILL` as a null class, and asks whether the field-level classes remain separable. It writes `messung/field.jsonl`, `messung/field.manifest.jsonl`, and prints the frame count and separability report. The earlier run returned **void**; it is a control, not validation of an input concept.

### 2. Hand reshape

```bash
python3 scripts/reshape_probe.py --device /dev/input/event19 --seconds 4 --settle-seconds 2 --reps 2 --out messung/reshape.jsonl
```

This takes about 75 seconds (six postures, twice: 2 seconds settling plus 4 seconds measuring, after a 3-second ready countdown). It writes `messung/reshape.jsonl` and `messung/reshape.manifest.jsonl`, then prints posture-by-posture contact-ambiguity results. It tests only whether deliberately reshaping the hand reduces contact ambiguity. It does **not** validate any input concept.

### 3. Fitts aiming

Capture:

```bash
python3 scripts/fitts_probe.py --mode capture --trials 60 --practice 4 --device /dev/input/event19 --out messung/fitts.jsonl --frames messung/fitts_frames.jsonl
```

Then fit the manifest:

```bash
python3 scripts/fitts_probe.py --mode analyse --in messung/fitts.jsonl
```

Budget roughly 10 minutes for capture. It writes the trial manifest to `messung/fitts.jsonl` and raw frames to `messung/fitts_frames.jsonl`; analysis prints the usable/excluded trials and, only with at least 20 usable trials, the fitted aiming coefficients. This measures movement time between cued small targets only. It must not be used to bound a drawn-path concept.

## 4. Data and void versus failed

All raw captures belong under `messung/`. This is biometric data: keep it local and gitignored. Do not copy it into tracked documents or commit it.

A **void run** completed far enough to produce a result object, but that result contains no usable evidence (for example, an empty capture, too few usable trials, or the earlier gesture result labelled void). A **failed run** did not complete a required open, read, write, or analysis step and reports an error. Neither is a measurement. No result may be claimed from an empty capture. Check frame and usable-sample counts before interpreting any report.

For every figure recorded from this session, preserve its provenance: `n`, operator, session, and whether it is measured, simulated, or assumed.

## 5. Handwritten closing record

Before leaving, write by hand what no instrument captures:

- operator comfort before and after the session;
- any cramp, pain, or fatigue noticed, when it began, and whether it affected a run;
- any interruption, aborted cue, or equipment problem;
- which runs are measured, void, or failed, with the relevant `n` and session date.

Comfort and cramp/fatigue are the only subjective data this project has ever had; an earlier session lost them.

## 6. What this session cannot establish

The project state remains **22 candidates generated, 0 validated, 0 surviving signals**. One session of these instruments does not change that and does not promise that any concept will work. It can produce the first real numbers for three unmeasured quantities: the field-gesture control, contact ambiguity under deliberate hand reshaping, and this thumb's cued-target aiming coefficients. It cannot issue a concept verdict.
