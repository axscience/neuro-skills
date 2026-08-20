---
name: neuro-figures
description: Publication-quality figure conventions for common neuroscience plot types — raster/PSTH plots, ERP/ERF traces with confidence bands, brain surface/volume overlays, and connectivity matrices/graphs. Use this when the deliverable is a figure, not just an analysis result — correctness of the underlying analysis is covered by the relevant modality skill; this is specifically about clear, honest visual presentation.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples use matplotlib; brain surface/volume plotting additionally uses nilearn.plotting or PySurfer/mne.viz depending on modality.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: neuro-figures
---

# Neuroscience Figures

## Overview

A correct analysis can still be misrepresented by a misleading figure — this skill covers the
conventions specific to common neuroscience plot types that make the difference between a figure
that accurately conveys uncertainty/effect size and one that doesn't, on top of general good
plotting practice.

## When to use this skill

Activate when the request involves:
- Making a publication figure, plot, or visualization from neuroscience analysis results
- Terms: raster plot, PSTH figure, ERP/ERF plot, brain overlay, connectivity matrix plot
- "Make a figure of this result," "plot this ERP with confidence bands," "visualize this connectivity matrix"

## Core usage

### Raster + PSTH combined plot (standard spike-data figure)

```python
import matplotlib.pyplot as plt

fig, (ax_raster, ax_psth) = plt.subplots(2, 1, sharex=True, height_ratios=[3, 1], figsize=(6, 6))
for trial_idx, spikes in enumerate(trial_spike_times):
    ax_raster.vlines(spikes, trial_idx, trial_idx + 0.9, color="black", linewidth=0.5)
ax_raster.set_ylabel("Trial")

ax_psth.plot(bin_centers, firing_rate)
ax_psth.fill_between(bin_centers, firing_rate - sem, firing_rate + sem, alpha=0.3)  # uncertainty, not just the mean
ax_psth.set_xlabel("Time (s)")
ax_psth.set_ylabel("Rate (Hz)")
```

### ERP/ERF with confidence band, not just the mean line

```python
import numpy as np

mean_erp = epochs_data.mean(axis=0)
sem_erp = epochs_data.std(axis=0) / np.sqrt(epochs_data.shape[0])

plt.plot(times, mean_erp)
plt.fill_between(times, mean_erp - sem_erp, mean_erp + sem_erp, alpha=0.3)
plt.axvline(0, color="gray", linestyle="--", linewidth=0.5)   # event onset marker
```

### Brain surface/volume overlay

```python
from nilearn import plotting

plotting.plot_stat_map(
    z_map, threshold=3.1,   # match the threshold actually used for statistical inference — see pitfalls
    display_mode="ortho", colorbar=True,
)
```

### Connectivity matrix / graph

```python
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()
im = ax.imshow(connectivity_matrix, cmap="RdBu_r", vmin=-vmax, vmax=vmax)  # symmetric colormap around zero for signed connectivity
plt.colorbar(im, label="Correlation")
```

## Validation & Pitfalls

- **A statistical map's plotted threshold must match the threshold actually used for inference —
  showing an unthresholded or differently-thresholded map from what the statistics support
  misrepresents the result.** This is the single most common way a technically-correct analysis
  becomes a misleading figure.
- **Signed connectivity/effect data needs a diverging colormap centered at zero (`vmin=-vmax,
  vmax=vmax` above), not a sequential colormap** — a sequential colormap on signed data visually
  implies all values are "more/less of the same thing" rather than showing the sign, which is usually
  the scientifically important part of a connectivity or contrast result.
- **A mean line without an uncertainty band (SEM, CI, or comparable) presents a summary statistic as
  if it were the whole story** — every trial-averaged trace (ERP/ERF, PSTH, any group-average
  timecourse) should show variability, not just the central tendency, matching this repo's broader
  "no number without uncertainty" principle extended to figures.
- **Color scale range choice can visually exaggerate or hide effect size** — a narrow color range
  makes small differences look dramatic; an unnecessarily wide range can wash out a real effect.
  Choose a range justified by the data's actual distribution (e.g. percentile-based), and state it,
  rather than defaulting to whatever a plotting library auto-selects.
- **Simulated/projected results must be visually distinguishable from measured results** — using the
  same visual language (same color scheme, same marker style) for a model projection and an actual
  measurement in the same figure invites a reader to treat them with equal confidence, which they
  don't warrant. Use a distinct visual treatment (dashed lines, hatching, explicit labeling) for
  anything that isn't a direct measurement.
