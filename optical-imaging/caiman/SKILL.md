---
name: caiman
description: "Two-photon/widefield calcium imaging analysis with CaImAn: motion correction (NoRMCorre), source extraction via constrained non-negative matrix factorization (CNMF / CNMF-E for 1-photon/miniscope), component evaluation, and deconvolution. Use for CNMF-based extraction or a cross-check against suite2p; for 1-photon miniscope data specifically, CaImAn's CNMF-E is the standard choice."
license: GPL-2.0-or-later
allowed-tools: Read Write Edit Bash
compatibility: Examples target CaImAn 1.11+. Typically installed via conda/mamba (the maintained path) rather than plain pip.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: optical-imaging
---

# CaImAn

## Overview

CaImAn is the CNMF-based alternative to Suite2p for extracting single-cell activity from calcium
imaging. Its constrained non-negative matrix factorization jointly estimates spatial footprints and
temporal activity, and its CNMF-E variant is the standard choice for 1-photon/miniscope data (where
large out-of-focus background makes suite2p-style ROI detection harder). This leaf covers the CaImAn
workflow; see `suite2p` for the classifier-based alternative and the parent `optical-imaging`
category for when to use which.

## When to use this skill

Activate when the request involves:
- CaImAn specifically, CNMF, CNMF-E, or 1-photon/miniscope calcium imaging
- Terms: NoRMCorre, spatial/temporal components, `estimates`, component evaluation (SNR, r_values),
  deconvolution (OASIS)
- File formats: `.tif`/`.tiff`, `.avi`/`.isxd` (miniscope), CaImAn `.hdf5` outputs
- "Run CNMF on this recording," "extract cells from miniscope data," "cross-check my suite2p ROIs"

## Core usage

### Motion correction and CNMF source extraction

```python
from caiman.source_extraction.cnmf import cnmf as cnmf
from caiman.source_extraction.cnmf.params import CNMFParams
import caiman as cm

# Start a parallel cluster (CaImAn parallelizes heavily)
c, dview, n_processes = cm.cluster.setup_cluster(backend="local", n_processes=None)

opts = CNMFParams(params_dict={
    "fr": 30,                 # frame rate (Hz)
    "decay_time": 0.4,         # transient decay time — indicator-specific
    "p": 1,                     # order of the autoregressive deconvolution model
    "gnb": 2,                    # number of global background components
    "K": 30,                      # expected number of components per patch
    "gSig": [4, 4],                # expected half-size of neurons in pixels
})

cnm = cnmf.CNMF(n_processes, params=opts, dview=dview)
cnm = cnm.fit_file("imaging_session.tif")   # runs motion correction + CNMF
```

### Component evaluation (the CaImAn analog of Suite2p's iscell)

```python
# CaImAn evaluates components on SNR, spatial-footprint consistency (r_values),
# and a CNN classifier — accepted/rejected indices land in estimates.idx_components
cnm.estimates.evaluate_components(images, cnm.params, dview=dview)
good = cnm.estimates.idx_components
traces_dff = cnm.estimates.F_dff        # dF/F for accepted components, if computed
```

## Validation & Pitfalls

Canonical references: Pnevmatikakis et al. (2016), "Simultaneous denoising, deconvolution, and
demixing of calcium imaging data," *Neuron* (CNMF); Giovannucci et al. (2019), "CaImAn: an open
source tool for scalable calcium imaging data analysis," *eLife*.

- **`gSig` (expected neuron size) and `K` (components per patch) strongly shape what CNMF finds** — a
  wrong `gSig` causes systematic over- or under-splitting of cells, and too-small `K` misses real
  components. These are not neutral defaults; set them from the actual imaging resolution and cell
  size, and inspect the extracted footprints before trusting downstream counts.
- **Use CNMF-E, not standard CNMF, for 1-photon/miniscope data** — the large, structured out-of-focus
  background in 1-photon imaging violates standard CNMF's background model; applying plain CNMF to
  miniscope data produces contaminated traces. Match the algorithm variant to the imaging modality.
- **Component evaluation thresholds (SNR, r_values, CNN) are a starting filter, not ground truth** —
  same caveat as suite2p's `iscell`: visually inspect accepted and rejected components, since the
  automated evaluation can systematically mis-rate unusual morphology or imaging conditions.
- **CNMF's deconvolution (`p`, OASIS) infers spike-like events under an autoregressive model whose
  order and decay-time assumptions matter** — inferred "spikes" are model estimates with real
  uncertainty, not measured action potentials; report them as such (the same slow-kinetics caveat as
  in `suite2p`).
- **Cross-checking against suite2p is a genuine robustness check, but the two won't agree perfectly**
  — differences in detected-cell sets are expected given the different algorithms; treat large
  disagreements as a signal to inspect the data/parameters, not as one tool being simply "wrong."
