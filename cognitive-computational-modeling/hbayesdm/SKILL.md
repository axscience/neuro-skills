---
name: hbayesdm
description: "Pre-built hierarchical Bayesian models for common decision-making tasks via hBayesDM (R/Stan) — reinforcement learning, drift-diffusion, prospect theory, and delay discounting, with validated implementations for standard task structures. Use when a pre-built model fits your task structure; for custom model specification in Python, use pymc-cognitive."
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: R ≥ 4.0, hBayesDM ≥ 1.2 (Stan backend), rstan ≥ 2.21. Models also accessible via the Python wrapper (pip install hbayesdm).
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: cognitive-computational-modeling
---

# hBayesDM

## Overview

hBayesDM provides ready-to-run hierarchical Bayesian implementations of common cognitive models —
reinforcement learning (Rescorla-Wagner variants), drift-diffusion models for two-alternative
forced-choice, prospect theory, delay discounting, and others — estimated via Stan's NUTS sampler.
Each model is pre-validated for a specific task structure: the user supplies a data table with the
expected columns (subject, trial, choice, RT, outcome, etc.) and gets posterior distributions over
group-level and individual-level parameters. The value is that the model specification and priors are
already debugged and tested; the risk is that the pre-built model must actually match your task
structure, and a mismatch produces plausible but meaningless estimates.

## When to use this skill

Activate when the request involves:
- hBayesDM, hierarchical Bayesian decision modeling, pre-built RL or DDM models
- Standard task structures: two-armed bandit, Iowa Gambling Task, delay discounting, go/no-go,
  two-alternative forced-choice with RT
- "Fit an RL model to this bandit data," "run hBayesDM on my choice data"
- User has a standard behavioral dataset and wants validated hierarchical fitting without writing
  a custom model

## Core usage

### Reinforcement learning — two-armed bandit

```r
library(hBayesDM)

# Data format: subjID, choice (1 or 2), outcome (reward)
output <- bandit2arm_delta(
  data = "my_bandit_data.txt",   # or a data.frame
  niter = 4000,
  nwarmup = 1000,
  nchain = 4,
  ncore = 4
)

# Group-level posteriors
plot(output, type = "trace")  # convergence check: chains should mix
plot(output)                   # posterior density

# Individual-subject parameters (shrunk toward group mean)
output$allIndPars  # columns: subjID, mu_A (learning rate), mu_tau (inverse temp)
```

### Drift-diffusion — two-alternative forced-choice

```r
output <- ddm_hyperbolic(
  data = "my_2afc_data.txt",  # subjID, choice, RT
  niter = 4000,
  nwarmup = 1000,
  nchain = 4
)

# Parameters: drift rate, boundary separation, non-decision time, bias
```

### Model comparison across hBayesDM models

```r
output_model1 <- bandit2arm_delta(data = my_data, ...)
output_model2 <- bandit2arm_delta_alt(data = my_data, ...)  # alternative parameterization

# Extract LOO-IC for each (lower = better predictive accuracy)
# hBayesDM stores the fitted Stan object — use loo::loo() on the log-likelihood
```

### Python wrapper

```python
import hbayesdm

output = hbayesdm.bandit2arm_delta(data="my_bandit_data.txt", niter=4000, nchain=4)
output.plot()
```

## Validation & Pitfalls

Canonical reference: Ahn, Haines & Zhang (2017), "Revealing neurocomputational mechanisms of
reinforcement learning and decision-making with the hBayesDM package," *Computational Psychiatry*.

- **The pre-built model must match your task structure — using the wrong model produces plausible
  but meaningless estimates.** hBayesDM models assume specific trial structures (number of options,
  what feedback is given, timing). If your task differs from the model's assumptions, fit a custom
  model (see `pymc-cognitive`) rather than forcing data into a mismatched pre-built model.
- **Parameter recovery must be verified** — simulate data from the model with known parameters, fit,
  and check recovery. hBayesDM's pre-built models are generally well-validated, but recovery depends
  on your specific trial count and design — fewer trials per subject = worse recovery.
- **Individual-subject parameters are shrunk toward the group mean** — this is a feature
  (stabilizes estimates with limited trials), but means individual parameter values should not be
  over-interpreted as unbiased measurements. Report shrinkage as a property of the method, not as
  an afterthought.
- **Convergence diagnostics are not optional.** Check Rhat < 1.01 for all parameters and visually
  inspect trace plots for chain mixing. hBayesDM runs can silently produce non-converged posteriors,
  especially with complex models or small samples.
