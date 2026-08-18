---
name: optical-imaging
description: Optical recording of neural activity via genetically encoded indicators — two-photon/widefield calcium imaging, fiber photometry (bulk signal from a single site), and voltage imaging — with references per technique. Use this for any fluorescence-based functional imaging modality.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: References target Suite2p/CaImAn for calcium imaging ROI extraction; GuPPy-style pipelines for photometry.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: optical-imaging
---

# Optical Imaging

## Overview

Genetically encoded fluorescent indicators (GCaMP for calcium, GEVIs for voltage, dLight/GRAB
sensors for neurotransmitters) let activity be recorded optically rather than electrically. This
skill routes to the technique that matches your recording, since the analysis pipelines diverge
substantially even though the underlying biology (fluorescence as an activity proxy) is related.

## When to use this skill

Activate when the request involves:
- Calcium imaging, two-photon, widefield, GCaMP, fiber photometry, voltage imaging, GEVI,
  dLight/GRAB sensors, dF/F
- Terms: Suite2p, CaImAn, ROI extraction, neuropil correction, isosbestic correction
- "Extract ROIs from this imaging data," "compute dF/F," "process this photometry recording"

**Which reference to read:**

| You have... | Read |
|---|---|
| Two-photon or widefield imaging with spatially resolved ROIs (single-cell or population) | [references/calcium-imaging.md](references/calcium-imaging.md) |
| Bulk fiber photometry (one signal per fiber/site, no spatial resolution) — including dopamine/neurotransmitter sensors, not just calcium | [references/fiber-photometry.md](references/fiber-photometry.md) |
| Voltage imaging (genetically encoded voltage indicators, high-speed) | [references/voltage-imaging.md](references/voltage-imaging.md) |

## Pipeline overview

```
Raw movie/photometry signal
  ├─ Spatially resolved (2p/widefield) → motion correction → ROI extraction → dF/F   (references/calcium-imaging.md)
  ├─ Bulk single-site (photometry)      → isosbestic correction → dF/F → event alignment (references/fiber-photometry.md)
  └─ Voltage imaging                    → denoise → spike/event detection            (references/voltage-imaging.md)
```

## Validation & Pitfalls

- **Fluorescence is an indirect, nonlinear proxy for the underlying signal (calcium, voltage,
  neurotransmitter concentration), not a direct measurement.** Every technique below has its own
  specific caveats, but this general point holds across all of them: a fluorescence change is
  evidence of an activity change, not a calibrated measurement of its magnitude, without additional
  validation (e.g. simultaneous electrophysiology in a subset of experiments).
