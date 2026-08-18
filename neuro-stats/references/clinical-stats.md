# Clinical and Longitudinal Statistics

Modality-specific detail for [../SKILL.md](../SKILL.md). Clinical neuroscience studies commonly add
three needs the core cross-cutting methods don't cover: time-to-event outcomes, longitudinal
disease-progression trajectories, and combining data collected across multiple sites/scanners.

## Survival analysis (time-to-event outcomes)

```python
from lifelines import CoxPHFitter, KaplanMeierFitter

kmf = KaplanMeierFitter()
kmf.fit(durations=time_to_event, event_observed=event_occurred)
kmf.plot_survival_function()

cph = CoxPHFitter()
cph.fit(clinical_df, duration_col="time_to_event", event_col="event_occurred")
cph.print_summary()  # hazard ratios per covariate
```

## Longitudinal disease-progression models

```python
import statsmodels.formula.api as smf

# Random-slope mixed model: each subject gets their own trajectory (intercept +
# slope over time), while estimating a population-average trajectory
model = smf.mixedlm(
    "biomarker ~ time_since_baseline * diagnosis_group",
    data=longitudinal_df, groups=longitudinal_df["subject"],
    re_formula="~time_since_baseline",
)
result = model.fit()
```

## Site/scanner harmonization (ComBat)

Multi-site imaging data has systematic scanner/site effects that can dominate or masquerade as a
biological effect of interest — ComBat, originally developed for genomics batch effects, is the
standard neuroimaging harmonization approach:

```python
from neuroCombat import neuroCombat

harmonized = neuroCombat(
    dat=imaging_features,       # (n_features, n_subjects)
    covars=covariates_df,        # must include a 'site' column
    batch_col="site",
    categorical_cols=["diagnosis"],   # biological variables to explicitly preserve, not remove
    continuous_cols=["age"],
)
```

## Validation & Pitfalls

Canonical references: Fortin et al. (2018), "Harmonization of cortical thickness measurements across
scanners and sites," *NeuroImage*, for ComBat in neuroimaging specifically; Laird & Ware (1982),
"Random-effects models for longitudinal data," *Biometrics*, for the mixed-model foundation of
longitudinal analysis.

- **ComBat must be told which variables are biological (to preserve) vs. which is the batch/site
  effect (to remove) — get this wrong and it will remove real biological signal along with the
  scanner effect, or fail to remove the scanner effect at all.** The `categorical_cols`/
  `continuous_cols` specification above is not incidental configuration; it's the core of what the
  method does.
- **Harmonizing across sites assumes the biological effect of interest has a consistent relationship
  with the measured features across sites — this can fail if disease/diagnosis is confounded with
  site** (e.g. all patients scanned at one site, all controls at another). ComBat cannot separate a
  true site effect from a true group effect when they're perfectly confounded; this needs to be
  addressed in study design, not fixed by harmonization after the fact.
- **Survival analysis's proportional hazards assumption (in Cox models) needs to be checked, not
  assumed** — a covariate whose effect on hazard changes over time violates this assumption and
  requires a different model (e.g. time-varying coefficients) or stratification.
- **Longitudinal random-slope models require enough repeated measurements per subject to estimate an
  individual slope reliably** — two timepoints per subject cannot support a random-slope model's
  individual-trajectory-shape claims the way three or more can; check that the design has enough
  timepoints for the specific longitudinal claim being made.
- **Attrition/dropout in longitudinal clinical studies is rarely random** (participants who decline
  most are often the ones lost to follow-up) — a complete-case analysis ignoring this is a real bias
  risk; consider whether the dropout pattern needs explicit modeling (e.g. joint modeling of dropout
  and outcome) rather than assuming missing-at-random.
