# Structural MRI — Morphometry and Lesion Mapping

Modality-specific detail for [../SKILL.md](../SKILL.md). Covers cortical/subcortical morphometry
(volume, thickness, surface area) and, for clinical/stroke research, lesion-symptom mapping.

## Cortical reconstruction and morphometry

FreeSurfer (or FastSurfer, a deep-learning-based faster alternative with comparable output) produces
the standard structural derivatives most downstream analysis assumes:

```bash
recon-all -s sub-01 -i sub-01_T1w.nii.gz -all
```

```python
import pandas as pd

# FreeSurfer's aparc.stats / aseg.stats give per-region cortical thickness, surface
# area, and subcortical volume — read via a parser rather than hand-parsing the text output
from nipype.interfaces.freesurfer import ParseDICOMDir  # or use nibabel/freesurfer-stats packages
```

### Voxel-based morphometry (VBM) — whole-brain, unbiased-region gray matter comparison

```python
# After SPM/CAT12 or FSL-VBM segmentation and normalization, VBM reduces to a
# GLM on smoothed, normalized gray-matter density maps — the same GLM machinery
# as fMRI (see ../fmri.md), applied to a single structural image per subject
# instead of a timeseries.
```

## Lesion-symptom mapping (VLSM)

Voxel-based lesion-symptom mapping relates lesion location (typically from stroke) to a behavioral
or cognitive deficit score, testing at each voxel whether lesion presence/absence predicts the
outcome:

```python
import numpy as np
from scipy import stats

def vlsm_voxelwise(lesion_masks, behavioral_scores, min_lesion_n=5):
    """
    lesion_masks: (n_subjects, n_voxels) boolean array — lesion presence per subject per voxel
    behavioral_scores: (n_subjects,) continuous deficit score
    min_lesion_n: skip voxels lesioned in too few subjects to test reliably
    """
    n_voxels = lesion_masks.shape[1]
    t_stats = np.full(n_voxels, np.nan)
    for v in range(n_voxels):
        lesioned = lesion_masks[:, v]
        if lesioned.sum() < min_lesion_n or (~lesioned).sum() < min_lesion_n:
            continue
        t_stats[v], _ = stats.ttest_ind(behavioral_scores[lesioned], behavioral_scores[~lesioned])
    return t_stats
```

## Validation & Pitfalls

Canonical references: Fischl (2012), "FreeSurfer," *NeuroImage*, for cortical reconstruction;
Bates et al. (2003), "Voxel-based lesion-symptom mapping," *Nature Neuroscience*, for VLSM
methodology.

- **FreeSurfer/FastSurfer reconstruction quality varies and needs visual QC per subject** —
  segmentation errors (white-matter surface bleeding into dura, pial surface cutting into skull) are
  common enough that skipping visual review is a real risk, not a formality, especially in patient
  populations with atrophy or lesions where the algorithm's assumptions are more likely to break.
- **VLSM statistical power is voxel-dependent, not uniform across the brain** — voxels lesioned in
  very few or nearly all subjects can't be tested reliably (the `min_lesion_n` check above), meaning
  power differs systematically by lesion location, typically following vascular territory patterns.
  This needs to be reported, not just the significant voxels.
- **VLSM at the voxel level has the same multiple-comparisons problem as fMRI** — thousands of voxels
  tested. Cluster-based or permutation correction is required, and lesion-based analyses have
  additional spatial-autocorrelation structure (lesions cluster along vascular territories) that a
  naive permutation test can underestimate — use a method designed for lesion data specifically
  (e.g. cluster-based permutation respecting lesion structure), not a generic voxel-wise FDR without
  considering this.
- **Template space mismatches are especially costly for lesion work** — registering a lesioned brain
  to a standard template is harder and more error-prone than a healthy brain (the lesion itself
  distorts normal anatomy the registration algorithm expects); visually check registration quality
  per subject rather than trusting default parameters.
