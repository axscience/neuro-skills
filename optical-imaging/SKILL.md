---
name: optical-imaging
description: Optical recording of neural activity via genetically encoded indicators — calcium imaging (Suite2p, CaImAn), fiber photometry, and voltage imaging. This is a category router; each technique/tool is a leaf skill loaded on demand. Use for any fluorescence-based functional imaging modality.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Category router — see individual leaf skills for per-tool version/environment notes.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: optical-imaging
---

# Optical Imaging

## Overview

Genetically encoded fluorescent indicators (GCaMP for calcium, GEVIs for voltage, dLight/GRAB
sensors for neurotransmitters) let activity be recorded optically rather than electrically. This is
a **category** — it groups several distinct techniques and tools, each documented as its own leaf
skill so an agent loads only the one it needs, not the whole category. Pick the leaf that matches
your recording.

## When to use this skill

Activate when the request involves:
- Calcium imaging, two-photon, widefield, GCaMP, fiber photometry, voltage imaging, GEVI,
  dLight/GRAB sensors, dF/F
- Terms: Suite2p, CaImAn, ROI extraction, neuropil correction, isosbestic correction, CNMF
- "Extract ROIs from this imaging data," "compute dF/F," "process this photometry recording"

## Which leaf skill to load

| You have... | Load |
|---|---|
| Two-photon/widefield calcium imaging, and want the standard suite2p ROI-extraction pipeline | [suite2p](suite2p/SKILL.md) |
| Two-photon/widefield calcium imaging, and want CaImAn's CNMF-based extraction (or a cross-check against suite2p) | [caiman](caiman/SKILL.md) |
| Bulk fiber photometry (one signal per fiber/site, no spatial resolution) — incl. dopamine/neurotransmitter sensors | [fiber-photometry](fiber-photometry/SKILL.md) |
| Voltage imaging (genetically encoded voltage indicators, high-speed) | [voltage-imaging](voltage-imaging/SKILL.md) |

**Suite2p vs. CaImAn:** both do motion correction, ROI detection, and signal extraction for the same
kind of spatially-resolved calcium data, via different algorithms (suite2p's classifier-based
detection vs. CaImAn's constrained non-negative matrix factorization). They are genuine alternatives
— cross-checking a critical result against both is a reasonable robustness check, the same discipline
as cross-checking spike sorters in `spike-recording`.

## Validation & Pitfalls

- **Fluorescence is an indirect, nonlinear proxy for the underlying signal (calcium, voltage,
  neurotransmitter concentration), not a direct measurement.** Every leaf skill below has its own
  specific caveats, but this general point holds across all of them: a fluorescence change is
  evidence of an activity change, not a calibrated measurement of its magnitude, without additional
  validation (e.g. simultaneous electrophysiology in a subset of experiments).
