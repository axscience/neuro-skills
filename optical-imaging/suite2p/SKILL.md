---
name: suite2p
description: "Two-photon/widefield calcium imaging analysis with Suite2p: registration (rigid/nonrigid motion correction), ROI/cell detection via the built-in classifier, neuropil correction, and dF/F. Use for spatially-resolved calcium data; for CNMF-based extraction or a cross-check, use caiman. For bulk single-site signals, use fiber-photometry."
license: GPL-3.0-or-later
allowed-tools: Read Write Edit Bash
compatibility: Examples target Suite2p 0.14+. GPU acceleration is optional but substantially faster for registration on large recordings.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: optical-imaging
---

# Suite2p

## Overview

Suite2p is one of the two standard pipelines (with CaImAn) for extracting single-cell activity from
two-photon or widefield calcium imaging: it registers the movie (motion correction), detects ROIs
via a trained classifier, separates neuropil contamination, and produces per-cell fluorescence
traces. This leaf covers the Suite2p-specific workflow; the `caiman` leaf covers the CNMF-based
alternative for the same data, and the parent `optical-imaging` category explains when to reach for
which.

## When to use this skill

Activate when the request involves:
- Suite2p specifically, or two-photon/widefield calcium imaging where classifier-based ROI detection
  is wanted
- Terms: `run_s2p`, `ops`, `iscell`, F/Fneu, nonrigid registration, plane0
- File formats: `.tif`/`.tiff` imaging stacks, ScanImage/Bruker/Prairie outputs, Suite2p `.npy` outputs
- "Run Suite2p on this recording," "extract ROIs and compute dF/F," "why are my Suite2p cells noisy"

## Core usage

### Registration and ROI extraction

```python
import suite2p

ops = suite2p.default_ops()
ops["fs"] = 30.0             # imaging frame rate (Hz) — must match acquisition
ops["tau"] = 1.0              # GCaMP decay time constant (indicator-specific — check yours)
ops["nonrigid"] = True         # nonrigid motion correction, for tissue with local deformation

db = {"data_path": ["imaging_session"], "save_path0": "suite2p_output"}
output_ops = suite2p.run_s2p(ops=ops, db=db)
```

### Loading extracted traces and computing dF/F

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

Canonical reference: Pachitariu et al. (2017), "Suite2p: beyond 10,000 neurons with standard
two-photon microscopy," *bioRxiv*.

- **`iscell` classifier output is a starting filter, not ground truth.** Visually spot-check a sample
  of both accepted and rejected ROIs — the classifier is trained on general data and can
  systematically mis-classify unusual cell morphology or imaging conditions in a specific dataset.
- **Neuropil contamination correction (`neuropil_coefficient`) is a real analytic choice that changes
  results, not a fixed constant.** Too low leaves neuropil signal in the trace (inflating apparent
  activity); too high can over-subtract and produce artifactual negative dF/F. Check that the chosen
  coefficient doesn't produce a large fraction of implausibly negative baseline periods.
- **dF/F baseline window length trades stability against tracking slow drift.** A short window tracks
  slow drift (photobleaching, focus drift) but is noisier; a long window is more stable but can miss
  slow real changes in baseline activity. State the window used.
- **`tau` must match the indicator, and `fs` must match acquisition** — a wrong decay constant
  distorts Suite2p's spike deconvolution, and a wrong frame rate silently misaligns everything
  downstream to the stimulus.
- **Calcium indicator kinetics are slow relative to spiking** (GCaMP6s decay ~1s; even fast variants
  like GCaMP6f/jGCaMP8 are slower than an action potential) — calcium imaging cannot resolve
  individual spike timing the way electrophysiology can, and inferring exact spike counts from dF/F
  (Suite2p's deconvolution) carries real uncertainty that should be reported, not treated as exact.
