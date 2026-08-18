---
name: neuro-stats
description: Statistical methods shared across neuroscience modalities — cluster-based permutation testing, multiple-comparison correction, mixed-effects models, and power analysis. Cross-cutting by design (used across fMRI, MEG/EEG, ECoG, and behavioral data alike) — modality skills should link here rather than restate this content.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples use MNE-Python's cluster-permutation implementation, statsmodels/lme4-equivalent mixed models, and statsmodels' power analysis tools.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: neuro-stats
---

# Neuroscience Statistics

## Overview

Four techniques come up across nearly every modality in this repo, which is exactly why they live
here instead of being restated in each modality skill: cluster-based permutation testing (for
high-dimensional space/time/frequency data), multiple-comparison correction generally, mixed-effects
models (for repeated-measures/nested data — trials within subjects, subjects within groups), and
power analysis. See [references/clinical-stats.md](references/clinical-stats.md) for methods specific
to clinical/longitudinal designs.

## When to use this skill

Activate when the request involves:
- Multiple-comparison correction, cluster permutation, mixed-effects model, power analysis,
  sample size calculation
- Terms: FDR, Benjamini-Hochberg, mixedlm, TTestIndPower, spatiotemporal cluster test
- "Correct for multiple comparisons," "run a mixed model on trial-level data," "how many subjects do I need"

## Core usage

### Cluster-based permutation testing

```python
import mne
import numpy as np

# X: (n_subjects, n_timepoints, n_channels) or similar — any high-dimensional
# space/time/frequency array where you want to test against zero or between conditions
t_obs, clusters, cluster_p_values, H0 = mne.stats.permutation_cluster_1samp_test(
    X, n_permutations=1000, threshold=None, tail=0,
)
significant_clusters = [c for c, p in zip(clusters, cluster_p_values) if p < 0.05]
```

Cluster-based permutation solves the multiple-comparisons problem specifically for spatially/
temporally correlated data by testing whole clusters of contiguous significant points against a
null distribution built from randomly permuting condition labels — appropriate whenever neighboring
points (adjacent timepoints, channels, voxels) are expected to be correlated, which is true of nearly
all neuroscience data.

### Multiple-comparison correction (independent tests — FDR)

```python
from statsmodels.stats.multitest import multipletests

reject, corrected_pvalues, _, _ = multipletests(raw_pvalues, alpha=0.05, method="fdr_bh")
```

Use FDR when tests are independent or only mildly correlated (e.g. many separate ROI-pair
comparisons); use cluster-based permutation instead when strong spatial/temporal correlation exists,
since FDR ignores that structure and is conservative relative to a method that exploits it.

### Mixed-effects models (repeated measures / nested data)

```python
import statsmodels.formula.api as smf

model = smf.mixedlm("outcome ~ condition", data=trial_level_df, groups=trial_level_df["subject"])
result = model.fit()
```

Use a mixed model, not a repeated-measures ANOVA on subject-averaged data, whenever trial-level
(not just subject-level) variability matters, or when the design has unbalanced/missing trials —
averaging to the subject level before analysis discards information a mixed model uses.

### Power analysis

```python
from statsmodels.stats.power import TTestIndPower

analysis = TTestIndPower()
required_n = analysis.solve_power(effect_size=0.5, alpha=0.05, power=0.8)
```

## Validation & Pitfalls

Canonical references: Maris & Oostenveld (2007), "Nonparametric statistical testing of EEG- and
MEG-data," *Journal of Neuroscience Methods*, for cluster-based permutation; Benjamini & Hochberg
(1995) for FDR; Aarts et al. (2014), "A solution to dependency: using multilevel analysis to
accommodate nested data," *Nature Neuroscience*, specifically on the mixed-model-vs-averaging issue.

- **Cluster-based permutation gives a cluster-level p-value, not a p-value for any specific point
  within the cluster.** A significant cluster supports "there is a spatiotemporal effect somewhere in
  this cluster," not "this specific timepoint/channel is significant" — a common overinterpretation.
- **The initial cluster-forming threshold is a free parameter that affects sensitivity to different
  effect sizes/spatial extents, and needs justification, not a silent default.** A very liberal
  threshold merges unrelated effects into one cluster; a very conservative one misses real but
  spatially/temporally limited effects.
- **Averaging trials to the subject level before statistics throws away real information and can
  both underpower a design and, in some cases, produce a different answer than a mixed model on the
  same data** (Aarts et al., above) — use mixed models for trial-level data by default unless there's
  a specific reason not to.
- **Post-hoc power analysis (computing power for an effect size observed in the same data) is not
  meaningful and is a common misuse** — power analysis is for planning a study before data collection,
  using an effect size from prior literature or a pilot, not for justifying an already-collected
  dataset's adequacy after the fact.
- **A pre-registered analysis plan should specify the correction method before seeing results** —
  choosing between FDR, cluster-permutation, or an uncorrected threshold after looking at which
  produces significance is p-hacking, regardless of which specific method is chosen.
