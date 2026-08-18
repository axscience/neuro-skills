---
name: pet-imaging
description: Positron emission tomography analysis — tracer kinetic modeling, standardized uptake value ratio (SUVR) computation, partial volume correction, and PET-MRI coregistration. Cross-references mri for the coregistration/normalization infrastructure rather than duplicating it.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples use nibabel/nipype-adjacent tooling; several steps (partial volume correction, full kinetic modeling) commonly use dedicated packages like PETPVC or turku PET Centre tools not covered in depth here.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: pet-imaging
---

# PET Imaging

## Overview

PET measures the spatial distribution of a radioactive tracer over time, used in neuroscience for
amyloid/tau imaging (Alzheimer's research), dopamine system imaging, glucose metabolism (FDG-PET),
and receptor occupancy studies. Unlike MRI, PET's core analytic unit is tracer kinetics — how tracer
concentration in a region changes over the scan — not a single static image, though a static SUVR
image is the most common simplified output for cross-sectional comparison.

## When to use this skill

Activate when the request involves:
- PET, positron emission tomography, tracer, SUVR, amyloid, tau, FDG-PET, receptor occupancy,
  binding potential
- Terms: partial volume correction, kinetic modeling, reference tissue model, PET-MRI coregistration
- "Compute SUVR for this PET scan," "correct for partial volume effects," "coregister PET to MRI"

## Core usage

### Standardized uptake value ratio (SUVR) — the common simplified static measure

```python
import nibabel as nib
import numpy as np

pet_img = nib.load("pet_static.nii.gz").get_fdata()
reference_region_mask = nib.load("cerebellum_mask.nii.gz").get_fdata().astype(bool)

reference_uptake = pet_img[reference_region_mask].mean()
suvr_img = pet_img / reference_uptake   # tracer uptake relative to a reference region assumed tracer-free/stable
```

Reference region choice (cerebellar gray matter for amyloid tracers, e.g.) is tracer-specific and a
real methodological decision — see Validation below.

### Full kinetic modeling (when a dynamic scan, not just a static SUVR, is available)

```python
# Simplified reference tissue model (SRTM) is standard for receptor-binding tracers
# with a suitable reference region — full implementation is substantial; conceptually:
# fit each voxel/ROI's time-activity curve against the reference region's time-activity
# curve to estimate binding potential (BPnd), a more quantitative measure than SUVR.
# See dedicated kinetic modeling packages (e.g. PMOD, or open kinetic-modeling toolboxes)
# for validated implementations rather than a from-scratch fit for anything beyond exploration.
```

### Partial volume correction

```python
# PET's spatial resolution (~4-8mm) is coarse relative to cortical thickness (~2-4mm),
# causing signal from adjacent tissue (gray matter, white matter, CSF) to blend —
# "partial volume effect." Correction (e.g. via PETPVC, using a co-registered
# structural MRI segmentation) is standard practice for regional quantification,
# especially in atrophied brains where the effect is worse.
```

### PET-MRI coregistration (cross-references `mri`)

```python
# Rigid-body coregistration of PET to a subject's structural MRI, then applying the
# same MRI-to-template normalization already computed for the structural scan
# (see mri/references/structural.md) — don't independently normalize PET to a
# template; register it to the subject's own MRI first, then reuse that MRI's
# established transform to template space.
```

## Validation & Pitfalls

Canonical reference: Innis et al. (2007), "Consensus nomenclature for in vivo imaging of
reversibly binding radioligands," *Journal of Cerebral Blood Flow & Metabolism*, for kinetic modeling
terminology and standards.

- **Reference region choice is tracer-specific and changes results substantially — there's no
  universal reference region.** Cerebellar gray matter is standard for amyloid tracers assuming
  amyloid-free cerebellum, but that assumption itself can fail in some disease stages/populations.
  State and justify the reference region for the specific tracer, don't default to a region used in
  an unrelated tracer's literature.
- **SUVR is a simplified proxy for a true kinetic parameter (binding potential), not equivalent to
  it** — SUVR can be biased by blood flow changes independent of the actual binding target, especially
  in studies comparing groups where blood flow itself might differ (e.g. disease vs. healthy control).
  A full kinetic model, when a dynamic scan is available, is more robust to this.
- **Partial volume correction is often skipped, and skipping it is not a neutral choice** — it
  systematically biases regional values toward whatever adjacent tissue's uptake is (typically
  underestimating gray matter values due to blending with lower-uptake white matter/CSF), and this
  bias gets worse in atrophied brains — exactly the populations most PET studies (Alzheimer's, aging)
  focus on. State explicitly whether PVC was applied.
- **Radiotracer half-life and injection-to-scan timing must be accounted for and are easy to get
  wrong across a multi-subject/multi-site study** — inconsistent timing introduces uptake variability
  unrelated to the biology being studied. Confirm timing protocol consistency before pooling data
  across subjects or sites.
