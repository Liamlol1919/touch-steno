# Upstream Snapshot — 2026-09-25

The following repositories were cloned locally with shallow history for source inspection. They are **not copied into this repository**; each retains its own Git history and license. Pin the SHA before reuse.

| Local path | Upstream | Commit | Important inspected files |
|---|---|---|---|
| `references/plover` | [opensteno/plover](https://github.com/opensteno/plover) | `cf61e73a907fd49714029726486cb99eaeb53fa9` | `plover/steno.py`, `plover/translation.py`, `plover/steno_dictionary.py`, `plover/formatting.py`, `plover/machine/keyboard.py`, `plover/oslayer/linux/keyboardcontrol_uinput.py` |
| `references/8VIM` | [8VIM/8VIM](https://github.com/8VIM/8VIM) | `03214b7c33a6e06c22ad0be43286d5e6c438fdd6` | Android IME implementation, gesture/editor sources; inspect exact paths in the clone before copying |
| `references/DasherCore` | [dasher-project/DasherCore](https://github.com/dasher-project/DasherCore) | `74814dce9185329789076fff48c2e43a6aa0e78e` | `src/dasher.h`, C API, `Data/alphabets/`, `Data/training/` |
| `references/input-wacom` | [linuxwacom/input-wacom](https://github.com/linuxwacom/input-wacom) | `2d14d8d0143d71b9cdfe6931d88b5ada10378f16` | kernel Wacom driver, 4.18 compatibility tree, touch arbitration |
| `references/python-evdev` | [gvalkov/python-evdev](https://github.com/gvalkov/python-evdev) | `9508e5239ac50cd2ea9099519b3f17c9e3fc154d` | `src/evdev/device.py`, `src/evdev/uinput.py`, examples |
| `references/kanata` | [jtroo/kanata](https://github.com/jtroo/kanata) | `3aa9fa535ead451d5fb04c6e8dbd48532250c3ec` | Rust input remapping, keyberon/layout handling |

## Verified source observations

### Plover keyboard machine

`plover/machine/keyboard.py` exposes two useful policies:

- `first_up_chord_send=True`: send at the first key release; low latency but rolling chords can be truncated.
- `first_up_chord_send=False`: collect the complete stroke until all keys are released; more robust for arpeggiated input.

The code uses `_down_keys`, `_stroke_keys`, `_chord_already_sent`, `KeyboardCapture`, suppression and an `ACTIONS` configuration. A 0G adapter should not blindly enable first-up mode; it should reproduce both policies in a replayable test harness.

### Plover stroke model

`plover/steno.py` delegates to `plover_stroke.BaseStroke` and exposes `from_steno`, `from_keys`, `from_integer`, `rtfcre`, `steno_keys`, correction and sorting helpers. This is the correct normalization boundary for a custom touch stroke source.

### DasherCore

`src/dasher.h` provides a C API around the C++ zooming predictive engine: context creation, screen size, movement, frame, output callbacks, locale/training data and draw commands. The API comments explicitly warn that a context is not thread-safe. This makes it suitable as a separate engine process/thread with a single owner.

### python-evdev

`src/evdev/uinput.py` implements `UInput`, `UInput.from_device`, capability merging and filtered `EV_SYN`/`EV_FF`. Use the installed system package if possible; avoid vendoring C extension code without a build and licensing review.

## Reproduction commands

```bash
for d in references/plover references/8VIM references/DasherCore \
         references/input-wacom references/python-evdev references/kanata; do
  git -C "$d" log -1 --format='%H %cI %s'
done

git -C references/plover grep -n 'first_up_chord_send'
git -C references/plover grep -n 'def translate_stroke'
git -C references/DasherCore grep -n 'dasher_frame'
```

## Hardware status on the local machine

At `2026-09-25T05:12:29+02:00`, the local `/dev/input` enumeration did not show a Wacom PTH-660 device. The audit script therefore validated its enumeration path, but no PTH-660 event stream was available and no hardware performance number was fabricated.
