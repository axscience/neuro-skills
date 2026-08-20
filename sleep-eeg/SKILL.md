---
name: sleep-eeg
description: Polysomnography (PSG) processing — AASM-standard sleep stage scoring, and detection of sleep-specific events (spindles, slow oscillations, K-complexes) via YASA. Distinct from clinical epilepsy EEG (electrophysiology/references/epilepsy-eeg.md) — a different clinical discipline with different tooling, despite both being clinical EEG.
license: BSD-3-Clause
allowed-tools: Read Write Edit Bash
compatibility: Examples target YASA 0.6+ (built on MNE-Python).
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: sleep-eeg
---

# Sleep EEG (Polysomnography)

## Overview

Polysomnography combines EEG with EOG, EMG (chin), and often respiratory/cardiac channels to score
sleep stages and detect sleep-specific EEG events. The core scoring task — assigning each 30-second
epoch a stage (Wake, N1, N2, N3, REM) per AASM criteria — and event detection (spindles, slow
oscillations) are both well-served by YASA, which automates what used to be purely manual
expert scoring.

## When to use this skill

Activate when the request involves:
- Polysomnography, PSG, sleep staging, AASM, hypnogram, sleep spindle, slow oscillation, K-complex
- Terms: YASA, N1/N2/N3/REM, sleep architecture
- "Score this overnight EEG," "detect sleep spindles," "stage this PSG recording"

## Core usage

### Automated sleep staging

```python
import yasa
import mne

raw = mne.io.read_raw_edf("psg_recording.edf", preload=True)

sls = yasa.SleepStaging(raw, eeg_name="C3-A2", eog_name="EOG-A1", emg_name="EMG-Chin")
hypnogram = sls.predict()          # per-30s-epoch stage label
confidence = sls.predict_proba()    # per-epoch class probabilities — check before trusting a stage
```

### Sleep spindle detection

```python
spindles = yasa.spindles_detect(raw, ch_names=["C3-A2"], freq_sp=(12, 15))
spindles_df = spindles.summary()   # per-spindle: onset, duration, frequency, amplitude
```

### Slow oscillation detection

```python
slow_osc = yasa.sw_detect(raw, ch_names=["C3-A2"], freq_sw=(0.3, 1.5))
```

### Spindle-slow-oscillation coupling (a common downstream question — memory consolidation research)

```python
coupling = yasa.sw_detect(raw, ch_names=["C3-A2"], coupling=True, freq_sp=(12, 15))
```

## Validation & Pitfalls

Canonical references: Berry et al., *The AASM Manual for the Scoring of Sleep and Associated Events*
(current edition) for scoring standards; Vallat & Walker (2021), "An open-source, high-performance
tool for automated sleep staging," *eLife*, for YASA.

- **Automated staging accuracy (YASA reports ~85-90% agreement with human scorers on typical data)
  is not perfect, and errors aren't uniformly distributed across stages** — N1 in particular is
  poorly classified by both automated and human scorers due to its inherently ambiguous EEG
  signature. Use `predict_proba()` and flag low-confidence epochs for manual review rather than
  trusting every automated label equally.
- **Electrode/channel naming must match exactly what the model expects** (`C3-A2` referencing
  convention, specifically) — a differently-referenced or differently-named channel silently
  produces degraded staging accuracy rather than an error.
- **Spindle/slow-oscillation detection thresholds are tuned on specific populations (typically
  healthy young adults)** — detection sensitivity/specificity can degrade in older adults or clinical
  populations with atypical EEG, where spindle amplitude and slow-oscillation morphology differ from
  the detector's training distribution. Validate detector output against a manually-scored subset
  before trusting it on a population it wasn't validated on.
- **A single-night recording is not necessarily representative of a person's typical sleep** — the
  "first night effect" (disrupted sleep architecture on an unfamiliar recording setup) is
  well-documented; account for this in study design, not just analysis.
