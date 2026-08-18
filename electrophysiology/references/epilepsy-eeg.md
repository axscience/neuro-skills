# Clinical Epilepsy EEG

Distinct from [sleep-eeg's PSG staging](../../sleep-eeg/SKILL.md) — this is interictal epileptiform
discharge (IED) detection and seizure detection/prediction, the core analysis task in epilepsy
monitoring and presurgical evaluation, typically on scalp or intracranial recordings.

## Interictal epileptiform discharge detection — feature-based screening

Automated IED detectors are screening tools, not diagnostic replacements for expert review (see
Validation below). A basic feature-based approach:

```python
import numpy as np
from scipy.signal import find_peaks

def candidate_spike_features(signal, fs, min_amplitude_uv=50):
    """
    Rough candidate detection: sharp, high-amplitude deflections with a
    duration consistent with an epileptiform spike (20-70ms half-wave).
    This is a starting point for feature engineering, not a validated detector —
    see Validation & Pitfalls.
    """
    peaks, properties = find_peaks(
        np.abs(signal), height=min_amplitude_uv, distance=int(0.05 * fs)
    )
    candidates = []
    for p in peaks:
        window = signal[max(0, p - int(0.1 * fs)):p + int(0.1 * fs)]
        candidates.append({
            "sample": p,
            "amplitude": signal[p],
            "sharpness": np.max(np.abs(np.diff(window))),  # steep slope = sharper wave
        })
    return candidates
```

## Seizure onset detection — energy-based approach

```python
def line_length(signal, window_samples):
    """Sum of absolute differences in a sliding window — a simple, standard
    feature that rises sharply at seizure onset due to increased signal complexity."""
    abs_diff = np.abs(np.diff(signal))
    kernel = np.ones(window_samples)
    return np.convolve(abs_diff, kernel, mode="same")
```

Line length and related energy-based features (Shannon entropy, spectral edge frequency) feed
standard seizure-detection pipelines; production-grade seizure detectors (used clinically) are
substantially more sophisticated (deep-learning classifiers trained on large annotated datasets) —
this is the starting feature-engineering point, not a clinical-grade detector.

## Validation & Pitfalls

Canonical reference: Fisher et al. (2005), "Epileptic seizures and epilepsy: definitions proposed by
the International League Against Epilepsy," *Epilepsia*, for clinical definitions; for automated
detection methodology, Baumgartner & Koren (2018), "Seizure detection using scalp-EEG analysis: a
survey," *Seizure*.

- **Automated IED/seizure detectors are screening aids, not diagnostic replacements.** Clinical
  epilepsy diagnosis and surgical decisions require expert electroencephalographer review — a
  detector's output is a starting point for that review, never a substitute for it, and should never
  be represented as one in a research or clinical pipeline.
- **False positive rate matters as much as sensitivity, and the two trade off directly.** A detector
  tuned for high sensitivity on limited data commonly produces an unusable false-positive rate on new
  patients — report both, and validate against out-of-sample patients, not just held-out segments
  from the same patient/dataset the detector was tuned on.
- **Normal EEG variants (benign sharp transients, wicket spikes, POSTS) mimic epileptiform discharges
  in basic amplitude/sharpness features.** A feature-based detector like the one above will flag
  many of these — this is exactly the kind of false positive that requires expert differentiation,
  not a reason to loosen the detector's threshold.
- **Interictal discharge rate varies enormously across patients and recording conditions** (sleep
  state, medication, time since last seizure) — a fixed sensitivity/specificity operating point
  tuned on one dataset does not transfer to another population without re-validation.
