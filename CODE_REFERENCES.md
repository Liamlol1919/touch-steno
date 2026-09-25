# Curated Code References

> Repository links are starting points. Before reuse, pin a commit SHA, read the license, and verify the active maintenance branch. GitHub source may be unavailable or change.

## Highest-value building blocks

| Repository | What to reuse | Why it matters | License / caution |
|---|---|---|---|
| [opensteno/plover](https://github.com/opensteno/plover) | `plover/` dictionary, stroke, formatting, translation and output architecture; `linux/` and `plover/` machine/backend modules | Most mature open-source stenography engine. A custom touch source can feed the engine without reimplementing dictionaries. | GPL-2.0; linking/distribution obligations must be reviewed. |
| [8VIM/8VIM](https://github.com/8VIM/8VIM) | sector/branch gesture model, gesture recognition, editor integration | Concrete open-source 8pen-inspired implementation; Android-specific but useful as a reference layout and state machine. | Apache-2.0 according to repository; verify all submodules/assets. |
| [dasher-project/dasher](https://github.com/dasher-project/dasher) | language model, word/character prediction, continuous gesture rendering | Good fallback/editor and accessibility reference; separates prediction engine from input device. | Classic repo advertises GPL; inspect exact files and modern forks before reuse. |
| [dasher-project/DasherCore](https://github.com/dasher-project/DasherCore) | modern C++ prediction engine, alphabet/language data | Cleaner modern separation for a future core/frontend split; verify URL and commit because search results can show mirrors. | MIT stated in current project listing; verify repository license and transitive assets. |
| [linuxwacom/input-wacom](https://github.com/linuxwacom/input-wacom) | Linux device driver, touch arbitration and event semantics | Needed to understand why PTH-660 events may be suppressed or reorganized. | GPL-2.0; avoid copying kernel code into a differently licensed userspace component without review. |
| [linuxwacom/libwacom](https://github.com/linuxwacom/libwacom) | device capability/tablet database | Useful for identifying touch-capable PTH-660 configurations. | component license; check selected version. |
| [wayland.freedesktop.org/libinput](https://gitlab.freedesktop.org/libinput/libinput) | event normalization, touch arbitration, debug tooling | First stop for a Linux implementation; libinput is not a text decoder. | MIT-style project; use system library, not copied code where possible. |
| [Wacom-Developer/wacom-device-kit-macos-multi-touch](https://github.com/Wacom-Developer/wacom-device-kit-macos-multi-touch) | API sample patterns for multi-touch callbacks and data model | Official sample is valuable for understanding confidence, palm rejection and contact data on supported OS/API. | Wacom API/driver license; do not redistribute SDK binaries casually. |

## Useful but narrower references

| Repository / resource | Reusable idea |
|---|---|
| [luileito/tinyqwerty](https://github.com/luileito/tinyqwerty) | browser experiment harness for text-entry prototypes and URL-parameterized studies |
| [pentamassiv/keyboard](https://github.com/pentamassiv/keyboard) | Wayland virtual keyboard plumbing, separate from gesture recognition |
| [rdubois440/8Pen_Nunchuck_Leonardo](https://github.com/rdubois440/8Pen_Nunchuck_Leonardo) | 8pen sector/branch interaction description; treat as implementation inspiration, not authoritative spec |
| [input-wacom source](https://github.com/linuxwacom/input-wacom) | inspect touch event reports and palm arbitration behavior for the exact kernel version |
| [libwacom database](https://github.com/linuxwacom/libwacom/blob/master/data) | device capability lookup; do not infer all features from product name alone |

## Plover integration sketch

The stable boundary should be a source abstraction, not direct coupling to a Wacom SDK:

```python
# conceptual adapter, not a claim about Plover's public API
class TouchStenoSource:
    def events(self):
        # yield press/release/hold events with:
        # source_time, stroke_time, key_name, confidence, contact_id
        ...

class PloverStrokeAdapter:
    def feed(self, touch_event):
        # normalize candidates and emit a Plover-compatible stroke
        # reject low-confidence events; keep reversible candidate state
        ...
```

The actual integration should use Plover's documented machine/plugin API where possible. The sketch shows the desired separation, not an API that may be pasted into production unchanged.

## Gesture recognizer design

A small, auditable recognizer is preferable to a black-box model for the first prototype:

1. resample trajectory to fixed arc length;
2. translate by calibrated neutral point;
3. rotate only if user-specific orientation is stable;
4. derive sector/branch sequence;
5. match against a trie of allowed word prefixes;
6. return top-k candidates with confidence;
7. require explicit commit or high-confidence auto-commit;
8. append raw trajectory and candidate list to telemetry.

For character/word gestures, language model scoring can be:

\[
\log P(w \mid g) = \lambda_g \log P(g \mid w)
                   + \lambda_{hist}\log P(w \mid \text{history})
                   + \lambda_L \log P(w \mid \text{dictionary})
\]

The weights must be learned or tuned on a corpus; a large LM cannot compensate for a broken contact model.

## Licensing and reproducibility checklist

- [ ] pin repository commit SHA;
- [ ] copy license text into `references/THIRD_PARTY_LICENSES/`;
- [ ] list transitive dependencies and assets;
- [ ] distinguish concepts from copied source;
- [ ] check whether a layout or dictionary has separate terms;
- [ ] preserve NOTICE files;
- [ ] make raw sensor data opt-in and redact identifiers;
- [ ] record hardware/OS/driver versions in experiment logs.
