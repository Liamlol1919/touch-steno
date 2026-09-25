# Next-Generation English Steno Transport

This is a clean-room prototype. It does not import or modify the legacy
compass, sector, intent, or synthetic benchmark decoders.

## Product boundary

```text
anonymous ten-contact observation
        -> Simplex-10 transport decoder
        -> canonical English steno stroke
        -> ordered English steno outline
        -> Plover key-event boundary
```

The physical transport is an affine binary `[10, 5, 4]` codebook:

- 32 nonzero ten-bit contact masks;
- minimum Hamming distance exactly 4;
- one arbitrary contact substitution is corrected;
- ties, distance two, and all unproven patterns return `NACK`;
- no two-error correction is claimed;
- `*` is the English steno undo stroke;
- `#` is the English steno number-bar stroke.

The ten bits are assigned to the ten fingers in `english_steno.py`. The
permutation and codebook are hardcoded and reproducible. They are a transport
profile, not a measured ergonomic optimum.

## English steno profile

The 32-entry profile emits canonical English steno notation and side-specific
Plover key labels. It is intentionally a bounded first profile, not a claim of
complete English vocabulary coverage. Plover receives the key events and owns
translation, formatting, dictionaries, and output.

A larger custom English steno system can replace `STROKE_LIBRARY` without
changing the physical decoder interface. The physical word and the dictionary
stroke must remain separate layers.

## Safety and transaction rules

1. The all-zero observation is not a valid profile word.
2. A decoded stroke is tentative until the contact frame is complete.
3. A one-bit correction is recorded as `corrected=true`; the original mask is
   retained in the event log.
4. A distance-two result is `NACK`; it is never rounded to the nearest stroke.
5. Plover `*` is the committed correction/undo stroke.
6. A partial or interrupted chord never emits a Plover event.
7. Raw contact coordinates remain local and are not part of the Plover payload.

## CLI

```bash
python3 -m nextgen.cli encode 'ST/PH/KW'
python3 -m nextgen.cli decode 0010100010,1001011010
python3 -m nextgen.cli plover-json 'ST/PH'
python3 -m nextgen.cli codebook
```

The CLI output is a transport and Plover boundary artifact. It is not a Plover
installation, English dictionary, hardware driver, WPM claim, or hardware
performance measurement.

## Validation gates

Before any PTH-660 deployment:

1. Exhaustively verify 32 unique nonzero masks, `d_min=4`, all 320
   one-bit corrections, and all radius-two NACKs.
2. Verify every emitted stroke against the pinned Plover English steno system.
3. Test the profile with a separate calibration session and held-out chords.
4. Test left/right ambiguity, ring/little coupling, palm contact, missed
   contacts, and posture drift.
5. Compare text accuracy, correction time, false commits, and fatigue. Never
   infer performance from the codebook's mathematical distance.
