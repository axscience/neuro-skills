# Intracranial (ECoG / sEEG / DBS-LFP)

Modality-specific detail for [../SKILL.md](../SKILL.md). Intracranial recordings — ECoG grids/strips,
stereo-EEG depth electrodes, and DBS local field potentials — need referencing and band-power
extraction approaches that differ from scalp EEG, plus clinical-context handling scalp recordings
don't require.

## High-gamma extraction (the standard intracranial task-activity measure)

High-gamma power (~70-150 Hz) correlates closely with local population firing rate, making it one of
the most reliable task-related signals available from human intracranial recordings.

### Referencing

```python
import numpy as np

def common_average_reference(data, bad_channels=None):
    """data: (n_channels, n_timepoints)"""
    good_mask = np.ones(data.shape[0], dtype=bool)
    if bad_channels is not None:
        good_mask[bad_channels] = False
    return data[good_mask] - data[good_mask].mean(axis=0), good_mask

def bipolar_reference(data, adjacent_pairs):
    """adjacent_pairs: list of (i, j) index pairs of physically adjacent electrodes"""
    return np.array([data[i] - data[j] for i, j in adjacent_pairs])
```

| | Common average reference | Bipolar reference |
|---|---|---|
| Assumption | Noise is shared across most electrodes | Adjacent electrodes share local noise |
| Fails when | Widespread task response (real signal leaks into the "common" average and gets subtracted from every channel) | Electrode geometry doesn't support meaningful adjacent pairs |
| Typical use | Sparse/localized task responses | Widespread responses, or local spatial specificity matters |

### Band-limited Hilbert envelope

```python
from scipy.signal import butter, sosfiltfilt, hilbert

def high_gamma_envelope(data, fs, band=(70, 150), n_subbands=8):
    """Averages narrow sub-bands rather than one wide filter, avoiding amplitude
    bias toward the lower end of a single wide passband."""
    edges = np.linspace(band[0], band[1], n_subbands + 1)
    envelopes = [
        np.abs(hilbert(sosfiltfilt(butter(4, [lo, hi], btype="bandpass", fs=fs, output="sos"), data, axis=-1), axis=-1))
        for lo, hi in zip(edges[:-1], edges[1:])
    ]
    return np.mean(envelopes, axis=0)

def zscore_to_baseline(envelope, baseline_mask):
    baseline_mean = envelope[:, baseline_mask].mean(axis=1, keepdims=True)
    baseline_std = envelope[:, baseline_mask].std(axis=1, keepdims=True)
    return (envelope - baseline_mean) / baseline_std
```

## Clinical context: excluding pathological electrodes

In clinical ECoG (electrodes placed for seizure localization, used secondarily for research), some
electrodes are over tissue later identified as the seizure onset zone or showing frequent interictal
discharges — their activity reflects pathology, not normal cortical processing.

```python
def exclude_pathological_electrodes(data, electrode_names, seizure_onset_zone, ied_channels):
    exclude = set(seizure_onset_zone) | set(ied_channels)  # from clinical review, not inferred from signal
    keep_mask = np.array([name not in exclude for name in electrode_names])
    return data[keep_mask], [n for n in electrode_names if n not in exclude]
```

Get this from the epilepsy monitoring team's clinical annotation — don't infer pathological
electrodes from high-gamma activity levels itself, which conflates the exclusion criterion with the
thing being measured. For clinical epilepsy analysis specifically (interictal discharge/seizure
detection as the primary output, not an exclusion step), see
[epilepsy-eeg.md](epilepsy-eeg.md).

## Validation & Pitfalls (intracranial-specific, in addition to ../SKILL.md's shared list)

Canonical reference: Crone et al. (1998), "Functional mapping of human sensorimotor cortex with
electrocorticographic spectral analysis," *Brain*.

- **Line noise harmonics can fall inside the high-gamma range** (e.g. 60 Hz's second harmonic at 120
  Hz lands inside 70-150 Hz). Notch-filter before extraction and check the spectrum for residual
  peaks.
- **A single wide bandpass filter biases the envelope toward whichever frequencies have more power
  in that specific recording** — averaging narrow sub-bands (above) avoids this.
- **Common average referencing assumes the average is mostly noise — this breaks down with
  widespread task-responsive cortex,** since real signal then gets subtracted from every channel via
  the "common" average. Switch to bipolar referencing when task responses are widespread.
