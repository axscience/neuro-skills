---
name: cognitive-computational-modeling
description: Computational models of behavior and decision-making — reinforcement learning, drift-diffusion models, prospect theory, and Bayesian observer models, fit via hierarchical Bayesian methods. This is a category router; each tool ecosystem is a leaf skill loaded on demand. Distinct from computational-modeling (biophysical circuit simulation) — a different modeling tradition despite the shared "computational neuroscience" label.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Category router — see individual leaf skills for per-tool version/environment notes.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: cognitive-computational-modeling
---

# Cognitive Computational Modeling

## Overview

These models formalize a hypothesis about the latent computational process generating observed
choices and reaction times — a reinforcement-learning rule updating values from reward prediction
error, a drift-diffusion process accumulating evidence to a decision bound, a utility function over
prospects. Fitting them (typically hierarchically, pooling information across subjects while
allowing individual variation) yields interpretable parameters that can themselves become the
dependent variable in further analysis — including, in model-based neuroimaging, as trial-by-trial
regressors explaining neural data.

This is a **category** — the three leaf skills correspond to distinct tool ecosystems for the same
broad modeling enterprise. Pick the leaf that matches your task.

## When to use this skill

Activate when the request involves:
- Reinforcement learning models, drift-diffusion model, DDM, prospect theory, Bayesian observer
  model, computational psychiatry
- Terms: hBayesDM, PyMC, Stan, HDDM, PyDDM, hierarchical Bayesian fitting, WAIC/LOO, parameter
  recovery, model-based fMRI/EEG
- "Fit an RL model to choice data," "run a hierarchical DDM," "compare these behavioral models"

## Which leaf skill to load

| You have... | Load |
|---|---|
| A standard task structure (two-armed bandit, Iowa Gambling Task, delay discounting, go/no-go, 2AFC with RT) and want a validated pre-built model | [hbayesdm](hbayesdm/SKILL.md) |
| A drift-diffusion model to fit in Python — standard or non-standard (collapsing bounds, urgency) | [ddm-python](ddm-python/SKILL.md) |
| A custom model (non-standard RL, Bayesian observer, prospect theory variant, or any task structure not covered by hBayesDM's pre-built models) fitted hierarchically in PyMC | [pymc-cognitive](pymc-cognitive/SKILL.md) |

**hBayesDM vs. PyMC:** hBayesDM gives you debugged, pre-validated hierarchical models for
established task structures — faster to set up and less room for error, but inflexible if your task
deviates from the pre-built options. PyMC (via `pymc-cognitive`) lets you write exactly the model
you need, at the cost of doing your own parameter recovery, prior sensitivity, and convergence
validation. Start with hBayesDM if it has your task; reach for PyMC when it doesn't.

**DDM tools:** HDDM provides hierarchical Bayesian DDM in Python (analogous to hBayesDM's DDM but
stays in the Python ecosystem); PyDDM provides flexible model specification (custom drift, bounds,
noise functions) fitted via maximum likelihood. Both are covered in the `ddm-python` leaf.

**Model comparison** (WAIC/LOO via ArviZ) is cross-cutting — covered in both `hbayesdm` and
`pymc-cognitive` since it applies to either's output.

## Validation & Pitfalls

- **Parameter recovery must be verified before trusting fitted parameters, and is often skipped.**
  Simulate data from the model with known parameters, fit the model to the simulated data, and
  check the fit recovers the known parameters — if it doesn't, fitted parameters from real data
  aren't trustworthy either, regardless of how good the model's fit to real behavior looks. This
  applies to every leaf below, regardless of tool.
- **Model comparison via raw likelihood or R-squared always favors more flexible models — use
  WAIC/LOO (or cross-validated held-out likelihood), which penalize complexity.** A model comparison
  that doesn't account for flexibility differences is not a valid comparison.
- **A model that fits behavior well is not validated as the true underlying computation** — multiple
  qualitatively different models can fit choice/RT data comparably well. Model comparison identifies
  the best among the models actually tested, not confirmation of "the" correct model.
- **Model-based neuroimaging regressors are only as good as the behavioral model generating them.**
  A neural result built on a poorly-fit or unvalidated model's trial-by-trial variable inherits
  that model's uncertainty, and this should be reported alongside the neuroimaging result.
