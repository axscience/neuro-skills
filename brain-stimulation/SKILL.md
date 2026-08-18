---
name: brain-stimulation
description: Human non-invasive and invasive brain stimulation — TMS-EEG, transcranial electrical stimulation (tDCS/tACS), and clinical stimulation (DBS programming, presurgical mapping). Sibling to optogenetics-chemogenetics (animal circuit-manipulation tools) — this skill is specifically human/clinical.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: References target TESA (TMS-EEG artifact removal, MATLAB/EEGLAB-based) and standard tES dosing conventions.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: brain-stimulation
---

# Brain Stimulation (Human / Clinical)

## Overview

Non-invasive (TMS, tDCS/tACS) and invasive (DBS) stimulation methods let researchers and clinicians
causally perturb human brain activity — for research (testing a region's causal role, probing
cortical excitability) or treatment (depression, Parkinson's, essential tremor). This skill routes to
the specific method; each has a substantially different pipeline.

## When to use this skill

Activate when the request involves:
- TMS, transcranial magnetic stimulation, tDCS, tACS, transcranial electrical stimulation, DBS,
  deep brain stimulation, presurgical mapping, cortical stimulation mapping
- Terms: TESA, coil positioning, current-flow modeling, SimNIBS, Lead-DBS, afterdischarge
- "Design a TMS-EEG study," "plan tDCS montage/dose," "analyze DBS programming outcomes"

**Which reference to read:**

| You have... | Read |
|---|---|
| TMS combined with EEG recording (causal-manipulation research) | [references/tms-eeg.md](references/tms-eeg.md) |
| tDCS/tACS research protocols | [references/tes.md](references/tes.md) |
| Clinical DBS programming or presurgical mapping | [references/clinical-stimulation.md](references/clinical-stimulation.md) |

## Pipeline overview

```
Target/dose selection → Delivery → Effect measurement
  ├─ TMS + concurrent EEG   → pulse-artifact removal → TMS-evoked potential analysis   (references/tms-eeg.md)
  ├─ tDCS/tACS               → current-flow modeling → behavioral/physiological outcome (references/tes.md)
  └─ DBS / cortical mapping → electrode localization → outcome or mapping result       (references/clinical-stimulation.md)
```

## Validation & Pitfalls

- **Stimulation dose (intensity, duration, coil/electrode position) is the primary determinant of
  both effect and safety, and is easy to under-specify in a write-up.** Report exact parameters —
  they're not incidental methods detail; they're often the actual independent variable.
- **Individual variability in response to stimulation is large across all methods covered here** —
  a fixed stimulation protocol does not produce a uniform effect across participants (anatomy,
  baseline cortical excitability, and for TMS specifically, coil-to-cortex distance all vary).
  Account for this in both design (e.g. individualized targeting/dosing where feasible) and
  interpretation (a null group-average effect can still reflect real, heterogeneous individual
  effects).
