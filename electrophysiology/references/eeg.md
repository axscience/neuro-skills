# Scalp EEG

Modality-specific detail for [../SKILL.md](../SKILL.md)'s shared filtering/epoching pipeline. This
covers what's EEG-specific: re-referencing and ICA-based artifact removal.

## Re-referencing

```python
raw.set_eeg_reference(ref_channels="average")
```

## ICA-based artifact removal

```python
ica = mne.preprocessing.ICA(n_components=20, method="fastica", random_state=42)
ica.fit(raw)

eog_indices, eog_scores = ica.find_bads_eog(raw)
ica.exclude = eog_indices
raw_clean = ica.apply(raw.copy())
```

### What the common artifact components look like

| Artifact | Topography | Time course | Frequency content |
|---|---|---|---|
| Eye blinks (EOG) | Strong frontal, symmetric | Large, sparse, sharp deflections | Low-frequency, broadband spike |
| Eye movements (saccades) | Frontal, lateralized (opposite sign left/right) | Step-like, sustained | Low-frequency |
| Muscle (EMG) | Peripheral/temporal, focal | Continuous, high-amplitude bursts | High-frequency (>20 Hz), broadband |
| Heartbeat (ECG) | Diffuse, often stronger one side | Regular, ~1 Hz periodic spikes | Narrowband around heart rate |

### Before excluding a component, look at it

```python
ica.plot_properties(raw, picks=[0, 1, 2])  # topography, time course, spectrum, per component
```

`find_bads_eog`/`find_bads_ecg` are correlation-based heuristics against a reference channel, not
ground truth. In a recording with a weak or noisy EOG channel they can miss a real blink component
(false negative, artifact stays in the data) or flag a mostly-brain component that happens to
correlate with the reference (false positive, real data gets discarded). A 30-second visual check
per flagged component is the difference between "the pipeline ran" and "the pipeline is trustworthy."

## Validation & Pitfalls (EEG-specific, in addition to ../SKILL.md's shared list)

- **ICA component count is not free.** Too many overfits noise as "artifact"; too few
  under-separates real artifacts from brain signal. ~15-25 components for a 32-64 channel cap is
  typical — don't default to using every channel as a component.
- **Average referencing changes every channel's values, including ones already marked bad.** If bad
  channels were flagged before re-referencing, re-check after — the assessment may no longer hold.
- **A published-looking `n_components`/threshold from one study doesn't transfer to another
  recording's amplifier gain, electrode count, or impedance without re-checking.**
