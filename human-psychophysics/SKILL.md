---
name: human-psychophysics
description: Psychophysical methods for human behavioral data — adaptive staircase procedures, signal detection theory (d'/criterion), psychometric function fitting, and reaction-time/accuracy analysis. Use this for human perceptual/decision behavioral tasks; for animal behavior, use animal-behavior-tracking instead.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples use numpy/scipy; psychometric fitting shown via scipy.optimize (a full-featured alternative is the `psignifit` package for more robust Bayesian threshold estimation).
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: human-psychophysics
---

# Human Psychophysics

## Overview

Psychophysics quantifies the relationship between a stimulus parameter and a perceptual/behavioral
response — a detection threshold, a discrimination sensitivity, a decision criterion. This skill
covers the standard toolkit: adaptive staircases for efficient threshold estimation, signal detection
theory for separating sensitivity from response bias, psychometric function fitting, and basic
reaction-time/accuracy analysis. Task delivery itself (stimulus presentation, timing) is covered in
`experimental-design`; this skill is about analyzing what comes back.

## When to use this skill

Activate when the request involves:
- Psychophysics, staircase, signal detection theory, d-prime, criterion, psychometric function,
  detection/discrimination threshold, reaction time
- Terms: 2AFC, up-down staircase, lapse rate, ex-Gaussian, speed-accuracy tradeoff
- "Fit a psychometric function," "compute d' from this task," "analyze RT and accuracy"

## Core usage

### Signal detection theory — d' and criterion

```python
import numpy as np
from scipy.stats import norm

def dprime_and_criterion(hit_rate, false_alarm_rate):
    """Standard SDT measures. Clip to avoid infinite z-scores at 0/1 rates."""
    hit_rate = np.clip(hit_rate, 0.01, 0.99)
    false_alarm_rate = np.clip(false_alarm_rate, 0.01, 0.99)
    d_prime = norm.ppf(hit_rate) - norm.ppf(false_alarm_rate)
    criterion = -0.5 * (norm.ppf(hit_rate) + norm.ppf(false_alarm_rate))
    return d_prime, criterion
```

d' measures sensitivity (ability to discriminate signal from noise); criterion measures response
bias (tendency to say "yes" regardless of sensitivity) — two participants can have identical accuracy
with very different d'/criterion combinations, and accuracy alone conflates the two.

### Adaptive staircase (simple up-down)

```python
def staircase_step(current_level, correct, step_size, n_down=2, n_up=1, consecutive_correct=0):
    """2-down-1-up: two consecutive correct responses to decrease difficulty (increase
    level toward threshold from the easy side), one incorrect to increase it —
    converges to ~70.7% correct on the psychometric function."""
    if correct:
        consecutive_correct += 1
        if consecutive_correct >= n_down:
            current_level -= step_size
            consecutive_correct = 0
    else:
        current_level += step_size
        consecutive_correct = 0
    return current_level, consecutive_correct
```

### Psychometric function fitting

```python
from scipy.optimize import curve_fit
from scipy.stats import norm

def psychometric_function(x, threshold, slope, guess_rate=0.5, lapse_rate=0.02):
    """Cumulative Gaussian psychometric function with guess and lapse asymptotes."""
    return guess_rate + (1 - guess_rate - lapse_rate) * norm.cdf(x, loc=threshold, scale=slope)

popt, _ = curve_fit(
    lambda x, t, s: psychometric_function(x, t, s),
    stimulus_levels, proportion_correct, p0=[np.median(stimulus_levels), 1.0],
)
threshold, slope = popt
```

### Reaction time analysis

```python
def clean_rt(rt_array, min_rt=0.15, max_rt=3.0):
    """Exclude implausibly fast (anticipatory/motor-only) and slow (attention lapse)
    responses before computing summary statistics — see pitfalls on why mean RT alone is risky."""
    return rt_array[(rt_array >= min_rt) & (rt_array <= max_rt)]
```

## Validation & Pitfalls

Canonical references: Green & Swets (1966), *Signal Detection Theory and Psychophysics* for SDT;
Kingdom & Prins, *Psychophysics: A Practical Introduction* (2nd ed.) for staircase and psychometric
methods generally.

- **Accuracy alone conflates sensitivity and bias — always report d'/criterion (or an equivalent)
  when comparing conditions or groups on a detection/discrimination task**, not raw accuracy, unless
  bias is independently known to be matched.
- **Staircase step size and up-down rule determine what percentage-correct point is actually being
  estimated** — a 2-down-1-up staircase converges to ~70.7% correct, not 50% or 75%; using the wrong
  assumed convergence point when reporting a "threshold" misrepresents what was measured.
- **A psychometric function's lapse rate must be fit or fixed to a reasonable value, not ignored.**
  Fitting without a lapse-rate parameter (assuming performance approaches 100% at extreme stimulus
  values) causes the fitted threshold/slope to be biased by inattention lapses that have nothing to
  do with perceptual sensitivity — this is a well-documented source of threshold estimation bias.
- **Mean reaction time is sensitive to outliers and the RT distribution's well-known right skew** —
  median RT or a fitted ex-Gaussian model is more robust; report which was used, and always report
  the exclusion criteria applied (like `clean_rt` above) since they materially affect the result.
- **Speed-accuracy tradeoff means RT and accuracy shouldn't be interpreted independently** — a
  condition with faster RT and lower accuracy isn't necessarily "worse performance," it may reflect a
  different point on the same tradeoff curve. A joint measure (e.g. drift-diffusion modeling — see
  `cognitive-computational-modeling`) is more defensible than treating RT and accuracy as
  independent, unrelated outcomes.
