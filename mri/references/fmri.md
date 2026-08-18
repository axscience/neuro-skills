# Functional MRI — Preprocessing, GLM, and Connectivity

Modality-specific detail for [../SKILL.md](../SKILL.md). Covers the three stages almost every fMRI
project needs: preprocessing (fMRIPrep), task-based GLM analysis, and functional connectivity —
all with nilearn/Python tooling downstream of preprocessing.

## 1. Preprocessing with fMRIPrep

fMRIPrep is a containerized BIDS-App (Docker/Singularity), not a Python library — it's invoked as a
command-line tool, not imported.

```bash
docker run -ti --rm \
  -v /path/to/bids_dataset:/data:ro \
  -v /path/to/output:/out \
  -v /path/to/freesurfer_license.txt:/opt/freesurfer/license.txt:ro \
  nipreps/fmriprep:23.2.0 \
  /data /out participant \
  --participant-label 01 \
  --output-spaces MNI152NLin2009cAsym:res-2 \
  --fs-license-file /opt/freesurfer/license.txt \
  --nthreads 4 --omp-nthreads 4
```

A FreeSurfer license file is required (free registration) — fMRIPrep uses FreeSurfer internally even
for volumetric-only output.

### Loading output and confounds

```python
import pandas as pd
import nibabel as nib

bold_img = nib.load("out/sub-01/func/sub-01_task-pixar_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz")
confounds = pd.read_csv("out/sub-01/func/sub-01_task-pixar_desc-confounds_timeseries.tsv", sep="\t")
```

### Motion QC before anything downstream

```python
def motion_summary(confounds_path, fd_threshold=0.5):
    confounds = pd.read_csv(confounds_path, sep="\t")
    fd = confounds["framewise_displacement"].fillna(0)
    return {
        "mean_fd": fd.mean(), "max_fd": fd.max(),
        "pct_high_motion_volumes": (fd > fd_threshold).mean() * 100,
    }
```

Always review the per-subject HTML report fMRIPrep generates — registration failures and severe
artifacts can occur without the pipeline erroring out.

## 2. Task-based GLM (nilearn)

```python
from nilearn.glm.first_level import FirstLevelModel

motion_confounds = confounds[[c for c in confounds.columns if c.startswith(("trans_", "rot_"))]].fillna(0)

model = FirstLevelModel(t_r=2.0, hrf_model="spm", drift_model="cosine", high_pass=0.01)
model = model.fit(bold_img, events=events_df, confounds=motion_confounds)

z_map = model.compute_contrast("condition_a - condition_b", output_type="z_score")
```

### Group-level (second-level)

```python
from nilearn.glm.second_level import SecondLevelModel
import pandas as pd

design_matrix = pd.DataFrame({"intercept": [1] * len(z_maps)})  # one-sample group test
second_level_model = SecondLevelModel().fit(z_maps, design_matrix=design_matrix)
group_z_map = second_level_model.compute_contrast(second_level_stat_type="t")
```

### Multiple-comparison correction (required — see pitfalls)

```python
from nilearn.glm import threshold_stats_img

thresholded_map, threshold = threshold_stats_img(
    group_z_map, alpha=0.05, height_control="fdr", cluster_threshold=10
)
```

## 3. Functional connectivity

```python
from nilearn.maskers import NiftiLabelsMasker
from nilearn.datasets import fetch_atlas_schaefer_2018
from nilearn.connectome import ConnectivityMeasure

atlas = fetch_atlas_schaefer_2018(n_rois=200)
masker = NiftiLabelsMasker(
    labels_img=atlas.maps, standardize="zscore_sample",
    low_pass=0.1, high_pass=0.01, t_r=2.0,
)
roi_timeseries = masker.fit_transform(bold_img, confounds=confounds_path)

connectivity_matrix = ConnectivityMeasure(kind="correlation").fit_transform([roi_timeseries])[0]
```

Partial correlation (`kind="partial correlation"`) controls for indirect paths through other ROIs,
at the cost of requiring `n_timepoints > n_rois` to estimate reliably. For effective connectivity
(Granger, DCM) or graph-theoretic metrics on this matrix, see the `neuro-connectivity` skill.

## Validation & Pitfalls

Canonical references: Esteban et al. (2019), "fMRIPrep: a robust preprocessing pipeline for
functional MRI," *Nature Methods*; Friston et al. (1994), "Statistical parametric maps in functional
imaging: a general linear approach," *Human Brain Mapping*, for the GLM; Biswal et al. (1995) and
Varoquaux & Craddock (2013), "Learning and comparing functional connectomes across subjects,"
*NeuroImage*, for connectivity methodology.

- **Uncorrected voxel-wise or edge-wise p-values produce massive false-positive rates at whole-brain
  scale** — tens of thousands of voxels (GLM) or thousands of edges (connectivity). Always correct
  (FDR, cluster-based permutation, or network-based statistics); an uncorrected map is not a
  trustworthy result regardless of analysis type.
- **`t_r` must exactly match acquisition, not a rounded value** — a wrong `t_r` desynchronizes the
  modeled HRF (GLM) or the bandpass filter (connectivity) from the actual data, silently reducing
  sensitivity.
- **Confound selection is a real analytic choice.** More aggressive regression (full aCompCor, global
  signal regression) removes more noise but also more signal, and for connectivity specifically, GSR
  mechanically pushes the correlation distribution toward including negative values — state
  explicitly whether it was used, don't treat it as a neutral default.
- **High motion degrades GLM and connectivity results in different but equally serious ways** —
  reduced GLM sensitivity vs. systematically inflated short-range / suppressed long-range
  connectivity. Check `framewise_displacement` before analysis in both cases, not after an odd result
  prompts a second look.
- **A subject's preprocessing succeeding (fMRIPrep exit code 0) doesn't mean it's usable** — review
  the HTML QC report per subject; registration failures don't necessarily error out.
