# Simultaneous EEG-fMRI

Concurrent EEG-fMRI needs artifact correction neither modality's standalone pipeline covers: the
scanner introduces a large, structured gradient artifact into the EEG, and the MR environment's
static field plus pulsatile blood flow introduces a ballistocardiogram (BCG) artifact synchronized to
the cardiac cycle.

## Gradient artifact removal (average artifact subtraction)

The gradient artifact is large (often >100x the EEG signal) but highly repeatable across each fMRI
volume acquisition, which is what makes template-based subtraction effective:

```python
import numpy as np

def average_artifact_subtraction(eeg_data, slice_trigger_samples, artifact_window_samples):
    """
    eeg_data: (n_channels, n_timepoints)
    slice_trigger_samples: sample indices where each MRI slice/volume acquisition starts
                            (from a recorded trigger channel — required, not inferred)
    """
    n_channels = eeg_data.shape[0]
    template = np.zeros((n_channels, artifact_window_samples))
    n_valid = 0
    for trigger in slice_trigger_samples:
        if trigger + artifact_window_samples <= eeg_data.shape[1]:
            template += eeg_data[:, trigger:trigger + artifact_window_samples]
            n_valid += 1
    template /= n_valid

    corrected = eeg_data.copy()
    for trigger in slice_trigger_samples:
        if trigger + artifact_window_samples <= eeg_data.shape[1]:
            corrected[:, trigger:trigger + artifact_window_samples] -= template
    return corrected
```

This requires an accurate scanner slice/volume trigger recorded alongside the EEG — without precise
trigger timing, the artifact template misaligns and subtraction fails to remove (or actively adds)
artifact.

## Ballistocardiogram artifact removal

BCG correction typically combines an ECG-synchronized average-subtraction approach (same principle as
gradient artifact removal, keyed to detected heartbeats instead of scanner triggers) with ICA to
remove residual components correlated with the cardiac cycle:

```python
import mne

ica = mne.preprocessing.ICA(n_components=20, method="fastica", random_state=42)
ica.fit(raw_gradient_corrected)
ecg_indices, ecg_scores = ica.find_bads_ecg(raw_gradient_corrected)
ica.exclude = ecg_indices
raw_clean = ica.apply(raw_gradient_corrected.copy())
```

## Validation & Pitfalls

Canonical reference: Allen et al. (2000), "A method for removing imaging artifact from continuous
EEG recorded during functional MRI," *NeuroImage*, for gradient artifact correction; Allen et al.
(1998), "Identification of EEG events in the MR scanner: the problem of pulse artifact and a method
for removing it," *NeuroImage*, for BCG correction.

- **Gradient artifact subtraction requires precise trigger timing — a few samples of jitter degrades
  correction substantially.** Verify the trigger channel's timing accuracy against the scanner's
  actual acquisition parameters before trusting correction quality; don't assume a trigger channel is
  correctly configured just because it's present.
- **Residual gradient artifact after subtraction is common at higher frequencies and can masquerade
  as high-frequency neural signal (e.g. gamma-band activity).** Any gamma-band result from
  simultaneous EEG-fMRI data needs specific scrutiny for residual scanner artifact, more so than
  EEG-alone gamma results.
- **BCG artifact is irregular — it varies with each heartbeat, not perfectly periodic — so average
  subtraction alone leaves residual artifact that ICA is needed to clean up.** Don't skip the ICA step
  even after average-subtraction-based correction.
- **EEG quality inside the scanner is inherently worse than outside it** (thermal noise from
  induction in the leads, RF interference) — don't expect EEG-fMRI EEG data to match the SNR of a
  standalone EEG recording, and calibrate expectations for what effects are detectable accordingly.
