---
name: pymc-cognitive
description: "Custom hierarchical cognitive model specification and fitting in PyMC — reinforcement learning, Bayesian observer models, prospect theory, or any latent-process model that doesn't match a pre-built hBayesDM implementation. Use when you need to write your own model; for standard task structures, hbayesdm's pre-built models are faster and already validated."
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: PyMC ≥ 5.0, ArviZ ≥ 0.15 for diagnostics and model comparison.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: cognitive-computational-modeling
---

# PyMC — Custom Cognitive Models

## Overview

When hBayesDM's pre-built models don't match your task structure — a non-standard RL rule, a
multi-option choice, a custom utility function, a model that conditions on covariates not
anticipated by the pre-built interface — PyMC lets you write the generative model directly in
Python and fit it hierarchically via NUTS. The flexibility is the point: you specify the prior
structure, the trial-by-trial likelihood construction, and the model comparison strategy yourself.
The cost is that the model is your responsibility to validate (parameter recovery, prior
sensitivity, convergence), whereas hBayesDM's models have been pre-validated.

## When to use this skill

Activate when the request involves:
- Custom RL model, Bayesian observer model, prospect theory model in PyMC
- Non-standard task structures that don't fit hBayesDM's pre-built models
- Terms: PyMC, hierarchical Bayesian, Rescorla-Wagner, value-based decision model, NUTS sampler
- "Fit a custom RL model," "hierarchical model for this task," "model with covariates on learning
  rate"
- Model-based neuroimaging: extracting trial-by-trial latent variables (prediction errors, values)
  as regressors for fMRI/EEG

## Core usage

### Reinforcement learning — hierarchical Rescorla-Wagner

```python
import pymc as pm
import numpy as np
import pytensor.tensor as pt

with pm.Model() as rl_model:
    # Group-level priors
    alpha_mu = pm.Beta("alpha_mu", 2, 2)            # learning rate
    alpha_kappa = pm.Gamma("alpha_kappa", 5, 1)      # concentration
    beta_mu = pm.Gamma("beta_mu", 2, 0.5)            # inverse temperature
    beta_sigma = pm.HalfNormal("beta_sigma", 1)

    # Per-subject parameters
    alpha = pm.Beta("alpha", alpha=alpha_mu * alpha_kappa,
                    beta=(1 - alpha_mu) * alpha_kappa, shape=n_subjects)
    beta = pm.Gamma("beta", mu=beta_mu, sigma=beta_sigma, shape=n_subjects)

    # Trial-by-trial value update (task-specific — adapt to your design)
    # Build predicted choice probabilities via a scan or explicit loop
    # over trials, then:
    # choice_prob = pm.math.softmax(beta[subj_idx] * Q_values, axis=-1)
    # pm.Categorical("choices", p=choice_prob, observed=observed_choices)

    trace = pm.sample(2000, tune=1000, chains=4, target_accept=0.9)
```

### Model comparison with ArviZ

```python
import arviz as az

# Compute LOO for each model (requires pointwise log-likelihood storage)
with rl_model:
    pm.compute_log_likelihood(trace)

comparison = az.compare({
    "rescorla_wagner": trace_rw,
    "rescorla_wagner_dual_lr": trace_dual,
    "win_stay_lose_shift": trace_wsls,
})
# Ranks models by ELPD (expected log pointwise predictive density)
# Report ELPD difference and SE — overlapping SE intervals = inconclusive
```

### Extracting trial-by-trial latent variables for model-based neuroimaging

```python
# After fitting, extract the posterior mean of trial-by-trial prediction errors
# (or values, or surprise) — these become parametric regressors in a GLM
# (see mri/references/fmri.md for parametric modulation, or an EEG single-trial
# regression in electrophysiology)
pe_posterior = trace.posterior["prediction_error"].mean(dim=["chain", "draw"])
events_df["pe_regressor"] = pe_posterior.values  # per trial
```

### Prior predictive check

```python
with rl_model:
    prior_pred = pm.sample_prior_predictive(500)

# Verify that priors produce behaviorally plausible choice patterns
# before committing to a long MCMC run — if prior-predicted behavior
# is degenerate (all one choice, or random), the priors need adjustment
```

## Validation & Pitfalls

Canonical reference: Daw (2011), "Trial-by-trial data analysis using computational models," in
*Decision Making, Affect, and Learning*.

- **Parameter recovery is mandatory for custom models.** Simulate data from the model with known
  parameters across a realistic range, fit, and verify recovery. Pre-built hBayesDM models have
  this validation built in; your custom model does not until you do it yourself.
- **Prior sensitivity analysis: re-fit with widened/narrowed priors and check whether posterior
  conclusions change.** If they do, your data aren't strongly informative and the result is
  prior-driven — report that, don't hide it.
- **The softmax inverse-temperature and learning rate can trade off** — high beta compensates for
  low alpha and vice versa. Report joint posteriors (corner plots), not marginals in isolation,
  to expose these correlations.
- **`target_accept=0.9` or higher is often needed for hierarchical cognitive models** — the default
  0.8 produces excessive divergences with the strong correlations typical of these models. Check
  divergence warnings; if present, raise `target_accept` before reparameterizing.
- **Model-based neuroimaging regressors inherit the model's uncertainty.** A neural finding built
  on a poorly-recovered or prior-sensitive model variable is not independently validated by the
  neural data — report the behavioral model's limitations alongside the neuroimaging result.
- **A model that fits behavior well is not the "true" computation** — multiple different models
  can produce equivalent choice/RT predictions. Model comparison identifies the best among those
  tested, not the correct one.
