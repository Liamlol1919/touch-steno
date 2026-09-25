# Measured rejection

## 1. Headline: the contract rejected 100 percent of real trials

**The contract rejected 100 percent of the real trials in the same capture:** an offline replay of the authoritative process-local contract over `s12.jsonl` produced 24 trials, **0 key events**, and 24 NACK events, every one with the closed reason `ambiguous_attribution`, for a coverage fraction of **0.0**. This is a strict-attribution result, not a text-recognition result: the contract could not assign a captured contact field to a steno key and therefore emitted no key attribution. It is consistent with, but independent of, the separate geometric field-descriptor measurement on this capture, whose class-mean top-1 was **0.4583** against **0.1250** chance and whose upper 95% bound was **0.6212**. Together they say that the capture contains identity-free compass-class signal but no identity-free route to a trustworthy key attribution under the frozen contract.

## 2. Two independent measurements, one capture

| Measurement | Result | n | Operator | Session | Class count | Caveat |
|---|---:|---:|---:|---:|---:|---|
| Permutation-invariant field descriptor | class-mean top-1 **0.4583**; upper 95% **0.6212**; chance **0.1250** | **24 cued trials**, 3 per class; `n=63` strokes | 1 | 1 | 8 thumb-compass classes | One capture, one operator, one session; thumb-compass labels; **no error bars** |
| Authoritative process-local contract replay | **0 key events / 24 trials**; **24 NACKs** with `ambiguous_attribution`; coverage **0.0** | **24 cued trials** | 1 | 1 | Same 8 cue classes in the capture; the contract itself does not perform class classification | Same capture and capture limitations; **no error bars** |

These measurements are **independent**. The descriptor tolerates unknown contact identity and tests whole-field class separability. The contract refuses attribution and counts accepted key events; it does not classify a field and does not derive its result from the descriptor's score. They share `s12.jsonl` and its thumb-compass trial structure, so they are not independent capture samples.

## 3. Existing gate measurements and provenance

`BINDING_CONSTRAINT.md`, section 8, records the ambiguity lower bounds **U = 0.9491** for `s12.jsonl` and **U = 0.9980** for `tempo.jsonl`, against the observability requirement **U <= 0.10**. The same section records only **0.5 mm** of major-axis dynamic range across the entire capture. U is a **lower bound on ambiguity**: because the capture has no slot identity, every frame with two or more contacts is counted as having more than one plausible thumb. The separate per-contact wrong-key rate **e remains unmeasured**; **e must not be equated with U**, because U concerns contact ambiguity while e would concern whether an emitted key was wrong.

## 4. What this kills

The 0.0 contract coverage closes every recorded concept family whose primitive requires assigning a captured contact to a finger, a key, or a direction. It closes the **direction-quantisation family** (ten variants, recorded at **10–21/50**) and the **space-time lattice** (**25/50**). It closes **FCPT — Fitts-Cost Phoneme Targets** and **GAEC — Guarded Affine Envelope Chords**, because each needs a thumb to be a selectable target-array element or a distinguishable left/right thumb; their proposal and kill tests are recorded in `BINDING_CONSTRAINT.md`, section 2. It closes **Thread-Rosette** (**36/50 sponsor**, **11/50 across five adversarial critics**), because its thumb sweep through named steno anchors requires a primary identifiable contact. The exact scores, proposals, and earlier verdicts remain in `BINDING_CONSTRAINT.md`, sections 2, 3.2, 5, 6, and 10.1, and the measured field result is detailed in `models_confusion_analysis.md`. These are measurement-backed closures of the attribution premise, not claims about every imaginable input method.

## 5. The one thing this does not kill

The result does **not** kill a permutation-invariant **field descriptor**. With no contact identity assigned, that descriptor still separated the eight compass classes at class-mean top-1 **0.4583**, against **0.1250** chance, with upper 95% **0.6212**. The signal is nevertheless **unconfirmed**: the labels came from one operator performing **thumb-compass cues** in one session, so the descriptor may be detecting a thumb-shaped deformation rather than a controllable field gesture. The control experiment comparing the thumb-compass condition with a genuine whole-hand field gesture **has never been run**. The result therefore warrants the control, not an input, text-recognition, or hardware-performance claim.

## 6. Scope of the kill: the capture and the device as used

The zero coverage is a property of **this capture and this device as used**. It does **not** prove that a ten-contact digitiser cannot support steno. If the ten-contact condition is an artifact of resting a whole hand flat rather than something inherent to the digitiser, the supported conclusion is that a steno input method on this device must either **avoid simultaneous contact** or **deliberately reshape the hand**. That is the physical reframing the evidence supports: treat the operative object as a ten-contact field shaped for the intended input, not as a collection of independently assignable fingers or keys.

## 7. The single operator measurement

With both hands resting on the pad, run this one command:

```sh
python3 scripts/field_gesture_probe.py
```
