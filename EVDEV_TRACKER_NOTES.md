# Evdev Multi-Touch Tracker Notes

## Invariants enforced by `ContactTracker`

1. **One state object per MT slot.** `ABS_MT_SLOT` selects a slot; it never aliases or overwrites another slot.
2. **A sample needs both axes.** X/Y events may arrive in either order. Until both are present, no point, path or span is produced.
3. **Palm rejection uses a true contact span.** The span is computed only after the first complete XY sample; a missing axis is never substituted by zero.
4. **A step boundary closes live contacts.** `flush()` prevents a still-down contact from being attributed to the next cued step.
5. **A late release is idempotent.** After flush, a later `TRACKING_ID = -1` does not emit a duplicate contact.
6. **Legacy and MT modes are separate.** Once MT events are seen, mirrored `ABS_X/ABS_Y` events are ignored.

## Regression matrix

| Case | Expected result |
|---|---|
| slot 0 and slot 1 active simultaneously | two independent live points |
| X before Y, large Y value | no false palm rejection |
| Y before X | same as X before Y |
| contact still down at step end | closed exactly once at flush |
| tracking release after flush | no duplicate contact |
| legacy X/Y only | waits for both axes and emits one point |
| wide span over 30 mm | rejected with palm/forearm reason |
| narrow span | retained |

## Why these cases matter for PTH-660

The pad exposes MT protocol B. Frame ordering and release timing are device/driver properties, not user-interface semantics. Treating the event stream as raw slots and explicit lifecycle events keeps the ROM reader from turning a transport detail into a physical measurement error.

The tests use synthetic evdev codes. They do not establish real contact-area, pressure or hand-identity behaviour; a live PTH-660 capture is still required for those claims.
