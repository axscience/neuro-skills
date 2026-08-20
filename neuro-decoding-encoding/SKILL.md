---
name: neuro-decoding-encoding
description: Decoding (predicting stimulus/behavior from neural activity) and encoding models (predicting neural activity from stimulus/task features — TRF/mTRF, representational similarity analysis) using scikit-learn, with cross-validation structured to avoid leakage. Modality-agnostic — operates on any trials x features matrix, whether features come from spikes, ECoG high-gamma, fMRI ROIs, or EEG sensors.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples use scikit-learn 1.3+.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: neuro-decoding-encoding
---

# Neural Decoding and Encoding

## Overview

Decoding asks "can I predict the stimulus/behavior from neural activity?"; encoding asks "can I
predict neural activity from stimulus/task features?" — inverse directions of the same underlying
question about the relationship between neural data and the world. Both are covered here because
they share the same cross-validation infrastructure and the same leakage pitfalls, which matter more
to getting this right than which direction you're modeling.

This skill is deliberately modality-agnostic: the input is always a `(n_trials, n_features)` (or
`(n_trials, n_timepoints, n_features)` for time-resolved analysis) matrix, regardless of whether
those features came from `spike-recording`, `electrophysiology`, `optical-imaging`, or `mri`. For
modern deep-learning approaches to population-level structure specifically (not just
classification/regression), see [references/population-dynamics-deep-learning.md](references/population-dynamics-deep-learning.md).

## When to use this skill

Activate when the request involves:
- Decoding, MVPA, encoding model, TRF, mTRF, representational similarity analysis, RSA
- Terms: cross-validation leakage, GroupKFold, permutation test, temporal response function
- "Decode stimulus/behavior from neural activity," "fit a TRF/encoding model," "run RSA between neural
  and model representations"

## Core usage — decoding

```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, permutation_test_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scores = cross_val_score(clf, X, y, cv=cv)
score, perm_scores, p_value = permutation_test_score(clf, X, y, cv=cv, n_permutations=1000, random_state=42)
```

`make_pipeline` matters, not just for convenience — it fits `StandardScaler` only on each fold's
training data (see Validation & Pitfalls).

### Non-independent trials — group-aware splitting

```python
from sklearn.model_selection import GroupKFold

cv = GroupKFold(n_splits=5)   # groups: e.g. session ID — guarantees no session in both train and test
scores = cross_val_score(clf, X, y, cv=cv, groups=groups)
```

## Core usage — encoding models (TRF/mTRF, RSA)

### Temporal response function — predicting a continuous neural signal from a continuous stimulus feature

```python
from sklearn.linear_model import Ridge
import numpy as np

def build_lagged_design_matrix(stimulus_feature, n_lags, fs):
    """stimulus_feature: (n_timepoints,) e.g. speech envelope. Builds a design
    matrix of time-lagged copies for TRF/mTRF fitting."""
    n_timepoints = len(stimulus_feature)
    X = np.zeros((n_timepoints, n_lags))
    for lag in range(n_lags):
        X[lag:, lag] = stimulus_feature[:n_timepoints - lag]
    return X

X_lagged = build_lagged_design_matrix(speech_envelope, n_lags=25, fs=128)  # e.g. ~200ms of lags
trf_model = Ridge(alpha=1.0).fit(X_lagged, neural_signal)  # neural_signal: e.g. one EEG channel
```

### Representational similarity analysis

```python
from scipy.spatial.distance import pdist, squareform
from scipy.stats import spearmanr

neural_rdm = squareform(pdist(neural_patterns, metric="correlation"))   # neural_patterns: (n_conditions, n_features)
model_rdm = squareform(pdist(model_predictions, metric="correlation"))   # e.g. from a computational model's representations

rsa_correlation, p_value = spearmanr(neural_rdm[np.triu_indices_from(neural_rdm, k=1)],
                                       model_rdm[np.triu_indices_from(model_rdm, k=1)])
```

Deeper cross-validation and leakage guidance for group-structured data is in
[references/leakage_and_splitting.md](references/leakage_and_splitting.md) — it applies identically
to encoding models: fit any preprocessing/regularization choice within a train/test split, never on
the full dataset first.

## Validation & Pitfalls

Canonical references: Quian Quiroga & Panzeri (2009), "Extracting information from neuronal
populations," *Nature Reviews Neuroscience*, for decoding; Varoquaux et al. (2017), "Assessing and
tuning brain decoders," *NeuroImage*, for cross-validation pitfalls; Crosse et al. (2016), "The
multivariate temporal response function (mTRF) toolbox," *Frontiers in Human Neuroscience*, for TRF
methodology; Kriegeskorte, Mur & Bandettini (2008), "Representational similarity analysis," *Frontiers
in Systems Neuroscience*, for RSA.

- **Fitting a scaler/preprocessor on the full dataset before splitting leaks test-set information
  into training** — always fit inside the cross-validation loop (a `Pipeline` does this correctly by
  construction).
- **Trials are often not independent** (slow drift, adaptation, arousal within a session) — a random
  K-fold split can put correlated trials in both train and test. Use `GroupKFold` on session/block ID
  when trials aren't i.i.d.
- **Raw accuracy against an assumed chance level is unreliable under class imbalance** — report
  balanced accuracy or compare against a permutation-test null distribution on the actual label
  distribution.
- **For TRF/mTRF specifically, regularization strength (`alpha`) needs cross-validated tuning, not a
  fixed default** — an under-regularized TRF overfits to noise in the lagged design matrix, which is
  typically high-dimensional and collinear across adjacent lags.
- **RSA results depend heavily on the distance metric and the specific model representations
  compared** — a low RSA correlation doesn't rule out a relationship the chosen metric or model layer
  fails to capture; report the specific choices made, they're not neutral defaults.
- **A high decoding accuracy establishes information is present, not that it causally drives
  behavior** — keep this distinction explicit when writing up results, for both decoding and RSA.
