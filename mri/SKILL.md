---
name: mri
description: Structural, functional (fMRI), and diffusion MRI processing and analysis — preprocessing, GLM/connectivity analysis, morphometry, and tractography, with references per sub-modality. Use this for any MRI-derived brain data. For PET, use pet-imaging instead (cross-references this skill for coregistration).
license: BSD-3-Clause
allowed-tools: Read Write Edit Bash
compatibility: References target fMRIPrep 23.x, nilearn 0.10+, and FSL/MRtrix3 for diffusion — check each reference's specific version notes.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: mri
---

# MRI (Structural / Functional / Diffusion)

## Overview

MRI covers three substantially different analysis workflows sharing a common data format (NIfTI,
usually organized as BIDS) and often a common preprocessing entry point (fMRIPrep, which also runs
FreeSurfer-based structural processing). This skill routes to the sub-modality that matches your
question rather than trying to cover all three in one place.

## When to use this skill

Activate when the request involves:
- MRI, fMRI, BOLD, structural MRI, T1w/T2w, diffusion MRI, DTI, tractography, VBM, cortical thickness
- File formats: `.nii`/`.nii.gz` (NIfTI), BIDS-organized MRI datasets
- Terms: fMRIPrep, FreeSurfer, nilearn, GLM, first-level/second-level analysis, functional connectivity,
  lesion-symptom mapping
- "Preprocess this fMRI scan," "run a GLM on this task data," "compute cortical thickness"

**Which reference to read:**

| You have... | Read |
|---|---|
| Task or resting-state BOLD fMRI (preprocessing, GLM, or connectivity) | [references/fmri.md](references/fmri.md) |
| Structural/anatomical MRI (morphometry, cortical thickness, lesion mapping) | [references/structural.md](references/structural.md) |
| Diffusion-weighted MRI (tractography, white matter microstructure) | [references/diffusion.md](references/diffusion.md) |
| A question about combining results across published fMRI studies | [references/meta-analysis.md](references/meta-analysis.md) |

**Ownership note for connectivity specifically:** basic within-modality correlation-matrix
connectivity (atlas timeseries → correlation) lives in `references/fmri.md`. Cross-modality,
effective-connectivity (Granger causality, DCM), or graph-theoretic methods live in the cross-cutting
`neuro-connectivity` skill — don't duplicate that content here.

## Pipeline overview

```
Raw NIfTI/BIDS
  ├─ fMRI      → fMRIPrep (motion, normalization, confounds) → GLM or connectivity   (references/fmri.md)
  ├─ Structural → FreeSurfer/FastSurfer → morphometry, lesion mapping                (references/structural.md)
  └─ Diffusion  → eddy/topup correction → tensor/CSD fit → tractography              (references/diffusion.md)
```

## Validation & Pitfalls

Canonical reference: Poldrack, Mumford & Nichols (2011), *Handbook of Functional MRI Data Analysis*,
Cambridge University Press, for methodology spanning all three sub-modalities below.

- **Output/template space must match across every tool in a pipeline.** `MNI152NLin2009cAsym` and
  `MNI152NLin6Asym` are both "MNI space" but not voxel-for-voxel identical — an atlas or mask from one
  won't align correctly with data in the other. This is the single most common source of a silently
  wrong result across all three sub-modalities.
- **Motion is the dominant confound across structural, functional, and diffusion MRI alike** —
  though it manifests differently in each (BOLD signal disruption in fMRI, blurred cortical
  boundaries in structural, spurious tractography in diffusion). Check and report motion metrics for
  whichever sub-modality you're using; don't treat it as an fMRI-only concern.
