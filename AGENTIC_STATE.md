# Agentic State Ledger

**Loop:** 10× autonomous product-engineering meta-plan  
**Current phase:** 1 — Contract and archive  
**Evidence class of current product slice:** IMPLEMENTED  
**Active candidate:** Clean English steno transport prototype  
**Last promoted candidate:** English steno transport in `nextgen/`  
**Last rejected candidate:** Legacy sector-fitting as the product core  
**Open falsification test:** Real PTH-660 anatomy, identity, and false-commit study  
**Next executable action:** Define and red-team the versioned, process-local, side-specific English steno key/NACK event contract; do not add runtime integration yet

## Decisions

- English steno is the product language.
- German steno is out of scope.
- Prior experiments are archived and not used to fit the new product.
- The coordinator may publish ordinary code/docs/issues autonomously.
- Hardware, consent, privacy, destructive operations, and unsupported performance claims require explicit human intervention.

## Evidence boundary

The current `nextgen/` code proves a ten-bit transport, one-bit correction contract, canonical English steno stroke profile, and Plover JSON boundary. It does not prove Plover runtime translation, hardware usability, WPM, correction time, or complete English vocabulary coverage.

## Reference integration targets

- **touch-steno** — <https://github.com/Liamlol1919/touch-steno>; `REFERENCE_ONLY` dated
  snapshot evidence. It owns PTH-660 capture, segmentation, `[10,5,4]` decoding, English
  steno profile mapping, NACK, sequencing, and local replay.
- **commindv2** — <https://github.com/Liamlol1919/commindv2>; `REFERENCE_ONLY`. It is the
  eventual application consumer for connection negotiation, deduplication, translation/action
  policy, UI state, and graph mutation.
- **commind** — <https://github.com/Liamlol1919/commind>; `REFERENCE_ONLY`. It is a
  documentation/concept canon and future semantic/graph reference, not a runtime authority.

The ownership boundary is one-way and process-local: touch-steno is the sole PTH-660
capture/decoder owner and emits only versioned, side-specific English steno key/NACK events.
Raw contacts never leave touch-steno. commindv2 must not open the same evdev device or run a
second decoder. The archived `input_zones.json` is historical evidence, not a layout
authority or compatibility shim. The next integration action is contract design and red-team
review only; no external repository or runtime path is implemented by this state update.
