# Clinical Assessment Scales as Labels/Covariates

Modality-specific detail for [../SKILL.md](../SKILL.md). Structured clinical instruments (cognitive
screens like MMSE/MoCA, psychiatric symptom scales) are commonly used as the outcome a model
predicts, or as a covariate controlling for symptom severity — both uses have specific pitfalls
distinct from using a purely behavioral or physiological measure.

## Common instruments and what they actually measure

| Instrument | Domain | Range/interpretation notes |
|---|---|---|
| MMSE (Mini-Mental State Examination) | General cognitive screening | 0-30; ceiling effects in high-functioning populations, insensitive to mild impairment |
| MoCA (Montreal Cognitive Assessment) | General cognitive screening | 0-30; more sensitive than MMSE to mild cognitive impairment, less ceiling-limited |
| PHQ-9 | Depression symptom severity | 0-27; self-report, screening tool — not a diagnostic instrument on its own |
| PANSS | Psychotic symptom severity | Structured clinician-rated interview; requires trained rater, not self-report |

## Using a clinical score as a regression/classification label

```python
import pandas as pd

# Treating MMSE/MoCA as a continuous outcome assumes equal intervals between
# score points, which the instrument's construction doesn't strictly guarantee
# (see pitfalls) — for many analyses, a validated cutoff-based categorical
# outcome is more defensible than treating the raw score as interval data.
df["impairment_category"] = pd.cut(
    df["moca_score"], bins=[-1, 17, 25, 30], labels=["severe", "mild", "normal"]
)
```

## Using a clinical score as a covariate

```python
import statsmodels.formula.api as smf

# Controlling for baseline symptom severity when testing a neural predictor
model = smf.ols("outcome ~ neural_feature + baseline_phq9_score", data=df).fit()
```

## Validation & Pitfalls

Canonical references: Nasreddine et al. (2005), "The Montreal Cognitive Assessment, MoCA: a brief
screening tool for mild cognitive impairment," *Journal of the American Geriatrics Society*; Kroenke,
Spitzer & Williams (2001), "The PHQ-9: validity of a brief depression severity measure," *Journal of
General Internal Medicine*.

- **A screening instrument (MMSE, MoCA, PHQ-9) is not a diagnostic instrument, and using it as a
  ground-truth diagnostic label overstates what it measures.** MMSE/MoCA screen for cognitive
  impairment; they don't diagnose a specific etiology. PHQ-9 screens for depressive symptoms; it
  doesn't establish a clinical depression diagnosis, which requires a structured clinical interview.
  State explicitly that a screening score is being used as a proxy label, with the limitations that
  implies.
- **These scores are ordinal, not strictly interval — treating a 2-point MMSE difference as
  equivalent at every point on the scale is a modeling assumption, not a property of the
  instrument.** This matters most for standard linear-model statistics (mean differences, linear
  regression); rank-based or ordinal-regression approaches are more defensible when the assumption is
  questionable for the specific claim.
- **Self-report instruments (PHQ-9) and clinician-rated instruments (PANSS) have different sources of
  measurement error and different biases** — self-report is subject to insight/reporting biases;
  clinician ratings are subject to inter-rater reliability issues. Don't treat scores from different
  instrument types as directly comparable or interchangeable across studies without accounting for
  this.
- **Practice effects and regression to the mean affect repeated administration** (e.g. a cognitive
  screen given at multiple longitudinal timepoints) — an apparent improvement between administrations
  can reflect familiarity with the test rather than genuine cognitive change; account for this in
  longitudinal designs (e.g. alternate forms, or explicit practice-effect modeling), not just assume
  raw score change reflects the underlying construct.
- **Ceiling and floor effects limit sensitivity in specific populations** (MMSE's ceiling effect in
  high-functioning samples, noted in the table above) — check the score distribution in the actual
  sample before using an instrument known to have limited range/sensitivity for that population as an
  outcome or covariate.
