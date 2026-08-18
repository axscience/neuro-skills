# Two-Photon / Widefield Calcium Imaging

Modality-specific detail for [../SKILL.md](../SKILL.md). Covers motion correction, ROI/cell
extraction, and dF/F computation for spatially resolved calcium imaging (two-photon point-scanning
or widefield mesoscale).

## Motion correction and ROI extraction (Suite2p)

```python
import suite2p

ops = suite2p.default_ops()
ops["fs"] = 30.0             # imaging frame rate
ops["tau"] = 1.0              # GCaMP decay time constant (indicator-specific — check yours)
ops["nonrigid"] = True         # nonrigid motion correction, for tissue with local deformation

db = {"data_path": ["imaging_session"], "save_path0": "suite2p_output"}
output_ops = suite2p.run_s2p(ops=ops, db=db)
```

Suite2p and CaImAn (an alternative with a different underlying algorithm, CNMF) both do motion
correction, ROI detection, and signal extraction — cross-checking a critical result against both is
a reasonable robustness check, similar to cross-checking spike sorters.

## Loading extracted traces and computing dF/F

```python
import numpy as np

F = np.load("suite2p_output/suite2p/plane0/F.npy")          # raw fluorescence, (n_rois, n_frames)
Fneu = np.load("suite2p_output/suite2p/plane0/Fneu.npy")     # neuropil (surrounding tissue) fluorescence
iscell = np.load("suite2p_output/suite2p/plane0/iscell.npy")  # (n_rois, 2) — classifier probability

def compute_dff(F, Fneu, neuropil_coefficient=0.7, baseline_percentile=8, window_frames=300):
    F_corrected = F - neuropil_coefficient * Fneu  # subtract neuropil contamination
    baseline = np.array([
        np.percentile(F_corrected[:, max(0, i - window_frames):i + 1], baseline_percentile, axis=1)
        for i in range(F_corrected.shape[1])
    ]).T
    return (F_corrected - baseline) / baseline
```

## Validation & Pitfalls

Canonical reference: Pnevmatikakis et al. (2016), "Simultaneous denoising, deconvolution, and
demixing of calcium imaging data," *Neuron*, for the CNMF approach underlying CaImAn; Pachitariu et
al. (2017), "Suite2p: beyond 10,000 neurons with standard two-photon microscopy," *bioRxiv*, for
Suite2p.

- **`iscell` classifier output is a starting filter, not ground truth.** Visually spot-check a sample
  of both accepted and rejected ROIs — the classifier is trained on general data and can
  systematically mis-classify unusual cell morphology or imaging conditions in a specific dataset.
- **Neuropil contamination correction (`neuropil_coefficient`) is a real analytic choice that changes
  results, not a fixed constant.** A value too low leaves neuropil signal in the trace (inflating
  apparent activity); too high can over-subtract and produce artifactual negative dF/F. Check that
  the chosen coefficient doesn't produce a large fraction of implausibly negative baseline periods.
- **dF/F baseline window length trades stability against tracking slow drift.** A short window
  tracks slow drift in overall fluorescence (photobleaching, focus drift) but is noisier; a long
  window is more stable but can miss slow real changes in baseline activity. State the window used.
- **Calcium indicator kinetics are slow relative to spiking** (GCaMP6s decay time ~1s; even fast
  variants like GCaMP6f/jGCaMP8 are slower than an action potential) — calcium imaging cannot resolve
  individual spike timing the way electrophysiology can, and inferring exact spike counts from dF/F
  (spike deconvolution) carries real uncertainty that should be reported, not treated as exact.
