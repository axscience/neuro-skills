---
name: ddm-python
description: "Drift-diffusion modeling in Python — HDDM for hierarchical Bayesian DDM fitting and PyDDM for flexible model specification with custom drift/bound functions. Use for DDM fitting within a Python workflow; for pre-built R/Stan models (including DDM), see hbayesdm."
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: "PyDDM ≥ 0.7 (pip install pyddm); HDDM ≥ 0.9 (pip install hddm — note: HDDM has known compatibility issues with Python ≥ 3.10 and some dependency conflicts; check current installation docs). Both target two-alternative forced-choice RT data."
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: cognitive-computational-modeling
---

# DDM — Python

## Overview

The drift-diffusion model (DDM) formalizes two-alternative forced-choice decisions as noisy evidence
accumulation from a starting point toward one of two boundaries, producing joint predictions for
choice and reaction time. Two Python packages serve different use cases:

- **HDDM** — hierarchical Bayesian DDM estimation via Markov chain Monte Carlo. Analogous to
  hBayesDM's DDM models but stays in Python. Best for: standard DDM with condition effects on
  parameters, hierarchical estimation across subjects.
- **PyDDM** — a flexible DDM framework where drift rate, noise, bounds, and non-decision time can
  each be arbitrary user-defined functions (e.g. collapsing bounds, time-varying drift, urgency
  signals). Fits via likelihood optimization, not MCMC. Best for: non-standard DDM variants that
  go beyond the textbook model.

They solve different problems: HDDM gives you hierarchical Bayesian inference on the standard model;
PyDDM gives you the freedom to specify non-standard models. For the standard hierarchical DDM case,
hBayesDM (R/Stan) is a third alternative with a larger library of validated pre-built models.

## When to use this skill

Activate when the request involves:
- Drift-diffusion model, DDM, evidence accumulation, HDDM, PyDDM
- Terms: drift rate, boundary separation, non-decision time, starting point bias, collapsing bounds
- "Fit a DDM to this RT data," "hierarchical DDM in Python," "DDM with collapsing bounds"
- Two-alternative forced-choice tasks with reaction time data

## Core usage

### HDDM — hierarchical Bayesian DDM

```python
import hddm

data = hddm.load_csv("my_2afc_data.csv")
# Required columns: subj_idx, response (0/1), rt (seconds)

# Condition effect on drift rate
model = hddm.HDDM(data, depends_on={"v": "condition"})
model.find_starting_values()
model.sample(5000, burn=1000, dbname="traces.db", db="pickle")

# Convergence check
models = [hddm.HDDM(data, depends_on={"v": "condition"}) for _ in range(3)]
for m in models:
    m.find_starting_values()
    m.sample(5000, burn=1000)
hddm.analyze.gelman_rubin(models)  # R-hat for each parameter

# Posterior analysis
model.plot_posteriors()
v_condition1 = model.nodes_db.node[["v(condition1)"]]
```

### PyDDM — flexible model specification

```python
import pyddm

# Standard DDM
model = pyddm.Model(
    drift=pyddm.DriftConstant(drift=pyddm.Fittable(minval=0, maxval=4)),
    noise=pyddm.NoiseConstant(noise=1),  # fix noise, fit drift (standard convention)
    bound=pyddm.BoundConstant(B=pyddm.Fittable(minval=0.5, maxval=3)),
    nondecision=pyddm.OverlayNonDecision(nondectime=pyddm.Fittable(minval=0, maxval=0.5)),
)

sample = pyddm.Sample.from_pandas(df, rt_column_name="rt", correct_column_name="correct")
pyddm.fit_adjust_model(sample=sample, model=model)

# Collapsing bounds (non-standard)
model_collapsing = pyddm.Model(
    drift=pyddm.DriftConstant(drift=pyddm.Fittable(minval=0, maxval=4)),
    bound=pyddm.BoundCollapsingLinear(
        B=pyddm.Fittable(minval=0.5, maxval=3),
        t=pyddm.Fittable(minval=0, maxval=2)
    ),
    # ...
)
```

### Model comparison

```python
# PyDDM: compare via BIC/AIC
loss_standard = model_standard.get_fit_result().value()
loss_collapsing = model_collapsing.get_fit_result().value()
# Lower loss = better fit (penalized by complexity via BIC)

# HDDM: compare via DIC (deviance information criterion)
# printed automatically in model summary
```

## Validation & Pitfalls

Canonical references: Ratcliff & McKoon (2008) for the DDM itself; Wiecki, Sofer & Frank (2013)
for HDDM; Shinn, Lam & Murray (2020) for PyDDM.

- **HDDM has known installation and compatibility issues with recent Python versions (≥ 3.10).**
  Check the current HDDM GitHub for the latest installation instructions; consider using a
  dedicated conda environment. If installation is blocked, PyDDM or hBayesDM's R DDM are
  alternatives for the standard model.
- **RT data must be in seconds, not milliseconds — a factor-of-1000 error produces fits that
  converge but with meaningless parameter values.** Both HDDM and PyDDM expect seconds.
- **Non-decision time absorbs fast contaminants.** If non-decision time estimates are suspiciously
  high (> 40-50% of mean RT), check for fast guesses or data-coding errors — the model is absorbing
  them into the non-decision component rather than fitting meaningful drift/bound parameters.
- **Collapsing bounds and urgency signals can trade off with drift rate changes.** If fitting a
  non-standard model with PyDDM, verify parameter recovery (simulate and re-fit) to confirm your
  data can distinguish the model components — flexible specification makes identifiability problems
  more likely, not less.
- **HDDM's MCMC convergence is not guaranteed.** Always run multiple chains and check Gelman-Rubin
  R-hat (< 1.01); single-chain runs with no convergence diagnostic are untrustworthy.
