---
name: electrophysiology
description: Preprocessing and analysis of scalp EEG, MEG, and intracranial (ECoG/sEEG/DBS-LFP) field-potential recordings — montages, filtering, artifact rejection, epoching, and ERP/ERF analysis, with references for modality-specific and technique-specific depth. Use this for any recording of electrical brain activity at scalp, cortical-surface, or depth-electrode scale. For single/multi-unit spike recording, use spike-recording instead — that's a different signal class (action potentials, not field potentials) with different tooling.
license: BSD-3-Clause
allowed-tools: Read Write Edit Bash
compatibility: Examples target MNE-Python 1.7+, the shared toolkit across EEG/MEG/intracranial workflows in this skill.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: electrophysiology
---

# Electrophysiology (EEG / MEG / Intracranial)

## Overview

Scalp EEG, MEG, and intracranial recordings (ECoG grids/strips, stereo-EEG depth electrodes, DBS
local field potentials) all measure electrical field potentials, and share a substantial amount of
preprocessing and analysis tooling — primarily MNE-Python. This skill covers what's common across
all three (montages/channel geometry, filtering, artifact rejection, epoching around events, and
ERP/ERF averaging), and routes to modality- and technique-specific references for everything that
isn't shared.

## When to use this skill

Activate when the request involves:
- EEG, MEG, ECoG, sEEG, stereo-EEG, intracranial recording, or DBS local field potentials
- File formats: `.fif`, `.edf`, `.bdf`, `.vhdr`/`.vmrk`/`.eeg` (BrainVision), `.set` (EEGLAB), `.cnt`
- Terms: montage, referencing, ICA, artifact rejection, epoching, ERP, ERF, evoked response,
  source localization, MNE, MNE-Python
- "Preprocess my EEG/MEG recording," "clean this ICA," "compute an ERP," "localize the source of..."

**Which reference to read:**

| You have... | Read |
|---|---|
| Scalp EEG | [references/eeg.md](references/eeg.md) |
| MEG | [references/meg.md](references/meg.md) |
| ECoG, sEEG, or DBS-LFP | [references/intracranial.md](references/intracranial.md) |
| A question about oscillatory power, phase, or connectivity (any of the above) | [references/time-frequency-analysis.md](references/time-frequency-analysis.md) |
| Clinical epilepsy EEG (interictal discharges, seizure detection) | [references/epilepsy-eeg.md](references/epilepsy-eeg.md) |
| Simultaneous EEG-fMRI | [references/eeg-fmri-simultaneous.md](references/eeg-fmri-simultaneous.md) |

For fNIRS or sleep PSG — both scalp-electrode-or-optode-adjacent but genuinely different workflows
and libraries — see the separate `fnirs` and `sleep-eeg` skills instead of looking for them here.

## Pipeline overview

```
Raw → Mark bad channels → Filter → Notch (line noise) → [ICA, EEG/MEG] → Re-reference
  → Epochs → Evoked (ERP/ERF)
  → [Time-frequency]            (references/time-frequency-analysis.md)
  → [Source localization, MEG/EEG]   (references/meg.md)
  → [High-gamma, intracranial]    (references/intracranial.md)
```

## Core usage — shared across EEG/MEG/intracranial

### Filtering (do this before epoching, not after — see Validation & Pitfalls)

```python
import mne

raw = mne.io.read_raw_fif("recording_raw.fif", preload=True)
raw.filter(l_freq=1.0, h_freq=40.0, fir_design="firwin")
raw.notch_filter(freqs=60)  # or 50, depending on line frequency
```

### Epoching around events

```python
events = mne.find_events(raw, stim_channel="STI 014")
epochs = mne.Epochs(
    raw, events, event_id={"stimulus_onset": 1},
    tmin=-0.2, tmax=1.0, baseline=(-0.2, 0),
    reject=dict(eeg=150e-6),  # amplitude-based rejection; tune per recording, see pitfalls
    preload=True,
)
```

### ERP/ERF — trial-averaged response

```python
evoked = epochs["stimulus_onset"].average()
evoked.plot()
```

Everything modality-specific — referencing conventions, artifact types, source localization,
electrode/sensor layouts — is in the references above.

## Validation & Pitfalls

Canonical reference: Gramfort et al. (2013), "MEG and EEG data analysis with MNE-Python," *Frontiers
in Neuroscience*.

- **Filter the continuous signal before epoching, not the epochs afterward.** Filtering short epochs
  directly introduces edge distortion at epoch boundaries that a full-length filter avoids.
- **A fixed amplitude-rejection threshold is not portable across recordings.** A `150e-6` V threshold
  tuned for one amplifier/montage can silently reject the majority of epochs on another with
  different gain. Check the rejected-epoch fraction after applying a threshold, every time.
- **"The pipeline ran without error" is not validation.** Visually inspect at least a sample of raw
  traces and the ERP/ERF grand average before trusting downstream statistics — a wrong channel
  montage, a flipped polarity, or a missed bad channel all run cleanly and produce a wrong result.
