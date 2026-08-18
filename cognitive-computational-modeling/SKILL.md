---
name: cognitive-computational-modeling
description: Computational models of behavior and decision-making — reinforcement learning models, drift-diffusion models, prospect theory/utility models, and Bayesian observer models, fit via hierarchical Bayesian methods (hBayesDM/Stan/PyMC) with formal model comparison. Includes bridge notes for model-based neuroimaging/EEG (using trial-by-trial model variables as regressors). Distinct from computational-modeling (biophysical circuit simulation) — a different modeling tradition despite the shared "computational neuroscience" label.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples target PyMC 5.x and the hBayesDM package (R/Stan) for hierarchical Bayesian fitting.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: cognitive-computational-modeling
---

# Cognitive Computational Modeling

## Overview

These models formalize a hypothesis about the latent computational process generating observed
choices/reaction times — a reinforcement-learning rule updating values from reward prediction error,
a drift-diffusion process accumulating evidence to a decision bound, a utility function over
prospects. Fitting them (typically hierarchically, pooling information across subjects while
allowing individual variation) yields interpretable parameters that can themselves become the
dependent variable in further analysis — including, in model-based neuroimaging, as trial-by-trial
regressors explaining neural data.

## When to use this skill

Activate when the request involves:
- Reinforcement learning models, drift-diffusion model, DDM, prospect theory, Bayesian observer model,
  computational psychiatry
- Terms: hBayesDM, PyMC, Stan, hierarchical Bayesian fitting, WAIC/LOO, parameter recovery,
  model-based fMRI/EEG
- "Fit an RL model to choice data," "run a hierarchical DDM," "compare these behavioral models"

## Core usage

### Reinforcement learning model (Rescorla-Wagner) — hierarchical fit with PyMC

```python
import pymc as pm
import numpy as np

with pm.Model() as rl_model:
    alpha_mean = pm.Beta("alpha_mean", 2, 2)       # group-level learning rate
    alpha_sd = pm.HalfNormal("alpha_sd", 0.2)
    alpha = pm.Beta("alpha", mu=alpha_mean, sigma=alpha_sd, shape=n_subjects)  # per-subject

    beta_mean = pm.Gamma("beta_mean", 2, 0.5)       # group-level inverse temperature
    beta = pm.Gamma("beta", mu=beta_mean, sigma=1, shape=n_subjects)

    # Trial-by-trial value updating and choice likelihood construction depends on
    # the specific task structure — typically implemented via a scan/loop building
    # predicted choice probabilities per trial, then a Bernoulli/Categorical likelihood
    # against observed choices. See hBayesDM's pre-built RL models for validated
    # reference implementations across common task structures.

    trace = pm.sample(2000, tune=1000, chains=4)
```

### Drift-diffusion model

```python
# hBayesDM (R) provides validated, pre-built hierarchical DDM implementations
# for common two-alternative forced-choice task structures:
# library(hBayesDM)
# output <- dd_hyperbolic("example", niter=4000, nwarmup=1000, nchain=4)
#
# Python alternatives (PyDDM, HDDM) provide equivalent hierarchical DDM fitting
# within the Python ecosystem if keeping the full pipeline in Python matters.
```

### Model comparison

```python
import arviz as az

model_comparison = az.compare({"rl_model": trace_rl, "wsls_model": trace_wsls})  # win-stay-lose-shift as an alternative
# Compares via WAIC/LOO (approximations to out-of-sample predictive accuracy) — 
# not raw likelihood, which always favors the more flexible model regardless of
# whether the extra flexibility is warranted.
```

### Model-based neuroimaging bridge

```python
# Once a model is fit, its trial-by-trial latent variable (e.g. reward prediction
# error from the RL model above) becomes a parametric regressor in a GLM
# (see mri/references/fmri.md's parametric modulation, or an EEG single-trial
# regression) — testing where/when neural activity tracks the model-derived
# quantity rather than the raw stimulus/outcome.
events_with_modulation = events_df.copy()
events_with_modulation["modulation"] = trial_prediction_errors  # from the fitted model, per trial
```

## Validation & Pitfalls

Canonical references: Daw (2011), "Trial-by-trial data analysis using computational models," in
*Decision Making, Affect, and Learning*, for the general framework; Ahn, Haines & Zhang (2017),
"Revealing neurocomputational mechanisms of reinforcement learning and decision-making with the
hBayesDM package," *Computational Psychiatry*, for hierarchical fitting practice; Wagenmakers et al.
(2004) for DDM-specific considerations.

- **Parameter recovery must be verified before trusting fitted parameters, and is often skipped.**
  Simulate data from the model with known parameters, fit the model to the simulated data, and check
  the fit recovers the known parameters — if it doesn't, fitted parameters from real data aren't
  trustworthy either, regardless of how good the model's fit to real behavior looks.
- **Model comparison via raw likelihood or R² always favors more flexible models — use WAIC/LOO (or
  cross-validated held-out likelihood), which penalize complexity, not raw fit quality.** A model
  comparison that doesn't account for flexibility differences is not a valid comparison.
- **Hierarchical (partial-pooling) fits are the standard, not individual-subject fits, specifically
  because individual-subject fits with limited trials per subject are unstable** — but hierarchical
  fitting introduces its own consideration: group-level priors shrink individual estimates toward the
  group mean, which is appropriate for stabilizing estimates but means individual-subject parameter
  values shouldn't be over-interpreted as unshrunk measurements.
- **A model that fits behavior well is not thereby validated as the *true* underlying computation** —
  multiple qualitatively different models can fit choice/RT data comparably well (this is the same
  underdetermination problem as in `computational-modeling`). Model comparison identifies the best
  among the models actually tested, not confirmation of "the" correct model.
- **Model-based neuroimaging regressors are only as good as the behavioral model generating them** —
  a neural result built on a poorly-fit or unvalidated (no parameter recovery check) model's
  trial-by-trial variable inherits that model's uncertainty, and this should be reported as part of
  the neuroimaging result's own limitations, not treated as an independently validated input.
