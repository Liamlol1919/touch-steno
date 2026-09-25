# Measured rejection

## 1. Headline: the contract rejected 100 percent of real trials

**The contract rejected 100 percent of the real trials in the same capture:** an offline replay of the authoritative process-local contract over `s12.jsonl` produced **24 measured cued trials**, **0 key events**, and **24 NACK events**, every one with the closed reason `ambiguous_attribution`, for a coverage fraction of **0.0**. This is a strict-attribution result, not a text-recognition result: the contract could not assign a captured contact field to a steno key and therefore emitted no key attribution. The separate geometric field-descriptor measurement on this capture previously reported class-mean top-1 **0.4583** against **0.1250** chance with upper 95% **0.6212**; that number is now **withdrawn** by the ninth retraction. The permutation null test used **1000 permutations** with **seed 20260925**, a **57-dimensional descriptor**, **24 measured cued trials** in **8 compass classes** (**3 per class**), **one operator**, **one session**, and **n=63 strokes**. Its observed class-mean top-1 was **0.4583**, below the null mean **0.5685**; the null median was **0.5833**, the null 95th percentile **0.7083**, and the one-sided p-value **0.9460**. Under the pre-specified decision rule, p >= 0.05 withdraws the number as evidence. Together they say that the capture contains no identity-free compass-class signal supported by this descriptor and no identity-free route to a trustworthy key attribution under the frozen contract.

## 2. Two independent measurements, one capture

| Measurement | Result | n | Operator | Session | Class count | Caveat |
|---|---:|---:|---:|---:|---:|---|
| Permutation-invariant field descriptor (withdrawn) | observed class-mean top-1 **0.4583**, below null mean **0.5685**; null median **0.5833**; null 95th percentile **0.7083**; one-sided p **0.9460**; **1000 permutations**, **seed 20260925**, **descriptor dimension 57** | **24 measured cued trials**, **8 compass classes**, **3 per class**; **n=63 strokes** | **1** | **1** | **8 thumb-compass classes** | **one operator**, **one session**; **thumb-compass labels**; **no error bars**; ninth retraction |
| Authoritative process-local contract replay | **0 key events / 24 trials**; **24 NACKs** with `ambiguous_attribution`; coverage **0.0** | **24 cued trials** | 1 | 1 | Same 8 cue classes in the capture; the contract itself does not perform class classification | Same capture and capture limitations; **no error bars** |

These measurements are **independent**. The descriptor tolerates unknown contact identity and tests whole-field class separability. The contract refuses attribution and counts accepted key events; it does not classify a field and does not derive its result from the descriptor's score. They share `s12.jsonl` and its thumb-compass trial structure, so they are not independent capture samples.

## 3. Existing gate measurements and provenance

`BINDING_CONSTRAINT.md`, section 8, records the ambiguity lower bounds **U = 0.9491** for `s12.jsonl` and **U = 0.9980** for `tempo.jsonl`, against the observability requirement **U <= 0.10**. The same section records only **0.5 mm** of major-axis dynamic range across the entire capture. U is a **lower bound on ambiguity**: because the capture has no slot identity, every frame with two or more contacts is counted as having more than one plausible thumb. The separate per-contact wrong-key rate **e remains unmeasured**; **e must not be equated with U**, because U concerns contact ambiguity while e would concern whether an emitted key was wrong. The ninth-retraction null test used **1000 permutations**, **seed 20260925**, and **descriptor dimension 57** on **24 measured cued trials**, **8 compass classes**, **3 per class**, from **one operator**, **one session**, with **n=63 strokes**, **thumb-compass labels**, and **no error bars**.

## 4. What this kills

The 0.0 contract coverage closes every recorded concept family whose primitive requires assigning a captured contact to a finger, a key, or a direction. It closes the **direction-quantisation family** (ten variants, recorded at **10–21/50**) and the **space-time lattice** (**25/50**). It closes **FCPT — Fitts-Cost Phoneme Targets** and **GAEC — Guarded Affine Envelope Chords**, because each needs a thumb to be a selectable target-array element or a distinguishable left/right thumb; their proposal and kill tests are recorded in `BINDING_CONSTRAINT.md`, section 2. It closes **Thread-Rosette** (**36/50 sponsor**, **11/50 across five adversarial critics**), because its thumb sweep through named steno anchors requires a primary identifiable contact. The ninth retraction also withdraws the final positive descriptor result: the resting-hand condition blocks every recorded concept, including the identity-free one, under this measurement. The exact scores, proposals, and earlier verdicts remain in `BINDING_CONSTRAINT.md`, sections 2, 3.2, 5, 6, and 10.1. These are measurement-backed closures of the attribution premise, not claims about every imaginable input method.

## 5. What this does not kill

The ninth retraction withdraws the permutation-invariant field descriptor's previously reported class-mean top-1 **0.4583** as evidence. The number existed in the measurement record, but the permutation null test decisively rejected it: **1000 permutations**, **seed 20260925**, **descriptor dimension 57**, **24 measured cued trials**, **8 compass classes**, **3 per class**, **one operator**, **one session**, and **n=63 strokes**; **thumb-compass labels**, **no error bars**. The observed value **0.4583** was below the null mean **0.5685** (null median **0.5833**, null 95th percentile **0.7083**, one-sided p **0.9460**), so the pre-specified p >= 0.05 rule withdraws it. This is the ninth retraction and removes the project's last positive result. The control experiment comparing the thumb-compass condition with a genuine whole-hand field gesture has never been run; it does not rescue the withdrawn number or establish a new one.

## 6. Scope of the kill: the capture and the device as used

The zero coverage and the withdrawn descriptor result are properties of **this capture and this device as used**. They do **not** prove that a ten-contact digitiser cannot support steno. If the ten-contact condition is an artifact of resting a whole hand flat rather than something inherent to the digitiser, the supported conclusion is that a steno input method on this device must either **avoid simultaneous contact** or **deliberately reshape the hand**. That is the physical reframing the evidence supports: treat the operative object as a ten-contact field shaped for the intended input, not as a collection of independently assignable fingers or keys.

## 7. The single operator measurement

With both hands resting on the pad, run this one command:

```sh
python3 scripts/field_gesture_probe.py
```
