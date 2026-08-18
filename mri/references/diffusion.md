# Diffusion MRI — Tractography and White Matter Microstructure

Modality-specific detail for [../SKILL.md](../SKILL.md). Diffusion-weighted imaging measures water
diffusion direction/magnitude per voxel, from which white-matter fiber orientation and connectivity
between regions can be estimated.

## Preprocessing

```bash
# dwifslpreproc wraps FSL's eddy/topup for motion, eddy-current, and susceptibility
# distortion correction — the diffusion-specific preprocessing step analogous to
# fMRIPrep's role for BOLD data.
dwifslpreproc dwi.mif dwi_preprocessed.mif -rpe_header -eddy_options " --slm=linear"
```

## Fitting a diffusion model

```python
import dipy.reconst.dti as dti
from dipy.io.image import load_nifti
from dipy.io.gradients import read_bvals_bvecs
from dipy.core.gradients import gradient_table

data, affine = load_nifti("dwi_preprocessed.nii.gz")
bvals, bvecs = read_bvals_bvecs("dwi.bval", "dwi.bvec")
gtab = gradient_table(bvals, bvecs)

tensor_model = dti.TensorModel(gtab)
tensor_fit = tensor_model.fit(data)

fa = tensor_fit.fa   # fractional anisotropy — one common (if limited) microstructure measure
md = tensor_fit.md   # mean diffusivity
```

The single tensor model (DTI) is the simplest and most common starting point, but cannot resolve
crossing fibers within a voxel — constrained spherical deconvolution (CSD) is the standard choice
when tractography quality through crossing-fiber regions matters.

## Tractography

```python
from dipy.tracking.local_tracking import LocalTracking
from dipy.tracking.stopping_criterion import ThresholdStoppingCriterion
from dipy.direction import peaks_from_model

stopping_criterion = ThresholdStoppingCriterion(fa, 0.2)
# seeds, direction_getter set up from a fitted model (DTI or CSD) — see dipy tutorials
# for the full seeding/tracking call; abbreviated here for the core concept
streamlines = LocalTracking(direction_getter, stopping_criterion, seeds, affine, step_size=0.5)
```

## Validation & Pitfalls

Canonical reference: Jones, Knösche & Turner (2013), "White matter integrity, fiber count, and other
fallacies: the do's and don'ts of diffusion MRI," *NeuroImage* — a methods paper specifically about
the failure modes below, not just the technique.

- **Streamline count is not a valid measure of connection strength, and treating it as one is one of
  the most common errors in the field.** Tractography algorithms are biased toward longer, straighter
  tracts and against crossing-fiber regions in ways unrelated to true axonal connectivity — "more
  streamlines" means "the algorithm found this path more easily," not "this connection is stronger."
- **Single-tensor (DTI) fitting fails in crossing-fiber voxels — roughly a third of white matter
  voxels by some estimates.** FA/MD values and tractography results through these regions from a
  single-tensor model are unreliable; use CSD or another crossing-fiber-capable model when
  tractography traverses regions like the centrum semiovale.
- **Tractography produces anatomically plausible-looking but definitively false streamlines
  ("false positives") at a high rate** — this is a well-documented, algorithm-inherent limitation,
  not a sign of a specific pipeline error. Don't present a tractography result as ground-truth
  anatomical connectivity without acknowledging this.
- **FA is not a specific measure of "white matter integrity" or "myelination"** despite common
  informal usage — it's sensitive to fiber coherence, crossing fibers, edema, and other factors
  simultaneously. A group difference in FA supports "something about this white matter region
  differs," not a specific mechanistic claim, without additional evidence.
