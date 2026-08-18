---
name: clinical-biomarkers-ml
description: Diagnostic/prognostic classification from neuroscience data (imaging, EEG, or multimodal features) — handling class imbalance, external validation, and interpretability for models intended to support a clinical claim. Use this whenever a classification/prediction model's output is meant to inform diagnosis, prognosis, or treatment response, not just a basic-research decoding question (see neuro-decoding-encoding for that).
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples use scikit-learn; interpretability examples use SHAP.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  modality: clinical-biomarkers-ml
---

# Clinical Biomarkers and Diagnostic ML

## Overview

A classification model predicting diagnosis, prognosis, or treatment response from neural/clinical
data carries a substantially higher evidentiary bar than a basic-research decoding result — it's
implicitly (or explicitly) making a claim someone might act on. This skill covers the three practices
that most distinguish a trustworthy clinical-ML result from an overstated one: class-imbalance
handling, external (not just cross-validated) validation, and interpretability. See
[references/clinical-assessment.md](references/clinical-assessment.md) for using structured clinical
scales as labels or covariates.

## When to use this skill

Activate when the request involves:
- Diagnostic classification, prognostic model, clinical biomarker, disease prediction
- Terms: class imbalance, external validation, AUROC, AUPRC, SHAP, calibration, sensitivity/specificity
- "Build a diagnostic classifier," "validate this biomarker model," "explain what drives this prediction"

## Core usage

### Class imbalance (clinical datasets are rarely balanced)

```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, roc_auc_score, average_precision_score

clf = LogisticRegression(class_weight="balanced", max_iter=1000)
clf.fit(X_train, y_train)

# Report metrics robust to imbalance, not raw accuracy
balanced_acc = balanced_accuracy_score(y_test, clf.predict(X_test))
auroc = roc_auc_score(y_test, clf.predict_proba(X_test)[:, 1])
auprc = average_precision_score(y_test, clf.predict_proba(X_test)[:, 1])  # more informative than AUROC under severe imbalance
```

### External validation (the real bar, beyond cross-validation)

```python
# Cross-validation within one dataset/site estimates in-distribution generalization.
# External validation — a held-out dataset from a different site, scanner, or
# population entirely — estimates what actually matters for clinical utility:
# generalization to a genuinely new population.
clf.fit(X_development_site, y_development_site)
external_auroc = roc_auc_score(y_external_site, clf.predict_proba(X_external_site)[:, 1])
```

### Interpretability

```python
import shap

explainer = shap.Explainer(clf, X_train)
shap_values = explainer(X_test)
shap.summary_plot(shap_values, X_test)   # which features drive predictions, and in which direction
```

## Validation & Pitfalls

Canonical references: Poldrack, Huckins & Varoquaux (2020), "Establishment of best practices for
evidence for prediction: a review," *JAMA Psychiatry*, specifically on the gap between cross-validated
and externally-validated performance claims in neuroimaging-based prediction; Chekroud et al. (2021),
"The promise of machine learning in predicting treatment outcomes in psychiatry," *World Psychiatry*,
for a field-specific critical assessment.

- **Cross-validated performance within one dataset systematically overstates real-world
  generalization — this is one of the most consistently documented problems in clinical neuroimaging
  ML.** Site, scanner, and population-specific artifacts get learned as if they were signal; an
  external validation set from a genuinely different source is the actual test of clinical utility,
  not an in-dataset cross-validation fold, no matter how careful the fold structure.
- **Feature selection or hyperparameter tuning performed on the full dataset before cross-validation
  leaks information the same way scaling does (see `neuro-decoding-encoding`)** — and clinical
  datasets with many more features than subjects make this an especially severe risk; a "significant"
  result from tuning-then-cross-validating on the same data can be almost entirely an artifact of the
  leak.
- **AUROC alone hides severe imbalance-related weaknesses; report AUPRC alongside it when the
  positive class (typically the diagnosis of interest) is rare** — a model with strong AUROC can still
  have poor precision at any clinically usable operating threshold under severe imbalance.
- **Interpretability output (SHAP or similar) describes what the model learned to rely on, not
  necessarily a causal or even a robust biological signal** — a feature with high SHAP importance in
  one dataset can reflect a dataset-specific confound (e.g. scanner-correlated feature) rather than a
  generalizable biomarker; cross-check important features' stability across the external validation
  set, not just report them from the development set.
- **A model achieving statistical significance is not the same as a model with clinical utility** —
  report calibration and a clinically meaningful operating point (sensitivity/specificity at a
  plausible decision threshold), not just an omnibus metric like AUROC, when the claim is about
  clinical usefulness specifically.
