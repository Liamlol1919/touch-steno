# Raw Frame Schema

Raw contact recordings use JSONL. Each line is one SYN-aligned frame.

## Version 1

```json
{
  "schema": "touchsteno.raw_frame",
  "version": 1,
  "t": 123.456789,
  "c": {
    "17": [12.5, 8.25, 3.0]
  }
}
```

- `t`: monotonic timestamp in seconds.
- `c`: contact map keyed by tracking ID serialized as a string.
- Contact tuple: `[x_mm, y_mm, major_mm]`.
- `major_mm` may be a driver-provided contact-size estimate; it is not a guaranteed pressure value.
- An empty `c` is valid.
- The schema does not contain user identity, text, or decoded labels.

`kinematics._load()` normalizes versioned and legacy unversioned records to the internal
`{"t": ..., "c": ...}` shape before analysis. Unknown schema names and versions fail
closed; they are never silently interpreted as v1.

## Replay contract

A replay must preserve the original JSONL bytes or decode through `raw_schema.decode_record()`.
The analysis pipeline may use the canonical in-memory shape, but it must not rewrite or
discard schema/version metadata when exporting a recording.

`guided_calibration.py --merge` writes labelled frames with the same v1 envelope plus an
optional `task` label. The label is evaluation metadata, not sensor data.

## Compatibility

Legacy files containing only `t` and `c` remain readable. New recordings should always be
written by `kinematics.Recorder`, which emits v1 records. Do not infer pressure, tool type,
or anatomical finger identity from the `major` field without device-specific evidence.
