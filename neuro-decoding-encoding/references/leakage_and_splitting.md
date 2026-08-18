# Non-Independent Trials — Session- and Block-Aware Splitting

Deeper detail for [../SKILL.md](../SKILL.md). Plain `StratifiedKFold` assumes trials are
exchangeable. When they're not — slow drift within a session, or multiple sessions/subjects pooled
into one dataset — a random split can put correlated trials in both train and test, inflating
apparent accuracy for decoding, or apparent fit quality for an encoding model.

## Symptom: results that seem too good, or that collapse on new sessions

If decoding accuracy (or TRF/RSA fit) is far higher than a sanity check suggests — compared to
related published work, or compared to performance on a truly held-out session — leakage from
correlated trials is a common cause. The model may be partly capturing "when in the session this
trial happened" rather than the variable of interest.

## Group-aware cross-validation

```python
from sklearn.model_selection import GroupKFold, cross_val_score

cv = GroupKFold(n_splits=5)   # groups: e.g. session ID for each trial
scores = cross_val_score(clf, X, y, cv=cv, groups=groups)
```

This guarantees no session appears in both train and test for any fold — the reported result
reflects generalization to a *new* session, which is usually the claim actually being made.

## Block-structured splitting within a single session

```python
from sklearn.model_selection import TimeSeriesSplit

cv = TimeSeriesSplit(n_splits=5)   # always trains on earlier trials, tests on later ones
```

This changes what's being tested — appropriate when generalizing forward in time is specifically the
question (e.g. a within-session encoding model expected to be stationary), and the wrong choice when
trial order is arbitrary (pre-randomized presentation), where a shuffled `GroupKFold` on
session/block ID is usually more appropriate.

## Applies to encoding models too

For a TRF/mTRF fit across multiple recording sessions or subjects, the same principle holds: fit
the regularization parameter and evaluate generalization with `GroupKFold` on subject/session, not a
plain K-fold that could place the same subject's data in both train and test folds.

## Validation & Pitfalls

Canonical reference: Varoquaux et al. (2017), "Assessing and tuning brain decoders: cross-validation,
caveats, and guidelines," *NeuroImage*.

- **The failure is silent — a leaky split doesn't error, it just reports an inflated number.** There
  is no automated check that catches this after the fact; it has to be prevented at split-design
  time by knowing which trials are correlated (same session, same subject, adjacent in time) and
  grouping accordingly.
- **`GroupKFold` and `TimeSeriesSplit` test different generalization claims — picking the wrong one
  for the actual scientific question is itself a form of this same error**, even though neither
  leaks in the technical sense. Match the splitting strategy to what the result is meant to
  demonstrate (generalization to a new session/subject vs. forward-in-time prediction), not to
  whichever produces the better-looking number.
