---
name: neuro-connectivity
description: Cross-modality and effective-connectivity methods — coherence, Granger causality, dynamic causal modeling (DCM), and graph-theory metrics — spanning fMRI, MEG, EEG, and ECoG. Basic same-modality correlation-matrix connectivity (e.g. fMRI ROI-to-ROI correlation) lives in each modality's own reference (mri/references/fmri.md); this skill covers what's shared across modalities and effective (directional) connectivity specifically.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples use MNE-Python's connectivity module for coherence/spectral methods, statsmodels for Granger causality, and networkx for graph-theory metrics.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: neuro-connectivity
---

# Cross-Modality and Effective Connectivity

## Overview

Beyond a same-modality correlation matrix, three questions come up across modalities: is there
frequency-specific coupling between two signals (coherence), does one signal help predict another's
future beyond its own past (Granger causality — a statistical, not necessarily biological, notion of
"causality"), and what's the network topology of a connectivity matrix once computed (graph theory).
Dynamic causal modeling (DCM) goes further, fitting a generative model of how activity in one region
causes activity in another given an explicit biophysical/hemodynamic forward model.

## When to use this skill

Activate when the request involves:
- Coherence, Granger causality, dynamic causal modeling, DCM, graph theory, network topology,
  effective connectivity, cross-modality connectivity
- Terms: mne-connectivity, imaginary coherence, hub nodes, clustering coefficient
- "Compute Granger causality between these regions," "graph-theory metrics on this connectivity matrix,"
  "does X causally influence Y"

## Core usage

### Coherence (frequency-domain functional connectivity)

```python
import mne_connectivity

con = mne_connectivity.spectral_connectivity_epochs(
    epochs, method="coh", mode="multitaper", fmin=8, fmax=12, faverage=True,
)
coherence_matrix = con.get_data(output="dense")[:, :, 0]
```

Works identically on EEG/MEG sensor or source data, or ECoG channels — the method doesn't care about
modality, only that input is (n_epochs, n_channels, n_times).

### Granger causality

```python
from statsmodels.tsa.stattools import grangercausalitytests

# signal_a, signal_b: (n_timepoints,) each, e.g. two ROI/channel timeseries
data = np.column_stack([signal_b, signal_a])  # tests whether signal_a Granger-causes signal_b
results = grangercausalitytests(data, maxlag=10, verbose=False)
```

Granger causality tests statistical predictive precedence, not biological/mechanistic causality —
see Validation below.

### Graph-theory metrics on a connectivity matrix

```python
import networkx as nx
import numpy as np

def connectivity_to_graph(connectivity_matrix, threshold_percentile=90):
    """Threshold to keep only the strongest connections — graph metrics on a
    fully-connected weighted matrix are usually less interpretable than on a
    thresholded/sparsified graph."""
    threshold = np.percentile(np.abs(connectivity_matrix), threshold_percentile)
    adjacency = np.abs(connectivity_matrix) > threshold
    np.fill_diagonal(adjacency, False)
    return nx.from_numpy_array(adjacency)

graph = connectivity_to_graph(connectivity_matrix)
clustering_coefficient = nx.average_clustering(graph)
path_length = nx.average_shortest_path_length(graph)
hub_nodes = sorted(nx.degree_centrality(graph).items(), key=lambda x: -x[1])[:5]
```

## Validation & Pitfalls

Canonical references: Friston, Harrison & Penny (2003), "Dynamic causal modelling," *NeuroImage*, for
DCM; Granger (1969), "Investigating causal relations by econometric models and cross-spectral
methods," *Econometrica*, for the original Granger causality framework; Bullmore & Sporns (2009),
"Complex brain networks: graph theoretical analysis of structural and functional systems," *Nature
Reviews Neuroscience*, for graph metrics in neuroscience specifically.

- **"Granger causality" is a statistical, not a biological, claim — the name is misleading and
  routinely over-interpreted.** It establishes temporal predictive precedence given the specific model
  and lag structure used, not a mechanistic causal pathway; a common confound is a third, unmeasured
  region driving both signals with different lags, which produces apparent Granger causality between
  two effects of a shared cause.
- **Both coherence and Granger causality are sensitive to signal-to-noise ratio differences between
  the two signals being compared, not just their true coupling** — a systematic SNR difference (e.g.
  comparing a superficial ECoG channel to a deeper one) can bias apparent connectivity strength or
  directionality independent of real coupling differences. Check whether SNR is matched or control for
  it before comparing connectivity across regions/conditions with known SNR differences.
- **Graph-theory metrics depend heavily on the thresholding choice** (the `threshold_percentile`
  above) — different thresholds can produce qualitatively different network topology conclusions from
  the same underlying connectivity matrix. Report the threshold used, and ideally check result
  stability across a range of thresholds rather than one arbitrary choice.
- **DCM requires specifying a model space (which regions, which possible connections) in advance —
  results are conditional on that space being reasonable, and DCM cannot discover a causal structure
  outside the specified model space.** A DCM result supports "among the models I specified, this one
  fits best," not "this is the true causal architecture" — state the compared model space explicitly.
- **Volume conduction/field spread (in EEG/MEG especially) can produce spurious zero-lag connectivity
  between nearby sensors that reflects a single source appearing in multiple channels, not real
  connectivity between two separate sources.** Connectivity measures robust to zero-lag artifacts
  (e.g. imaginary coherence) are preferred over plain coherence/correlation specifically for sensor-
  space EEG/MEG connectivity claims.
