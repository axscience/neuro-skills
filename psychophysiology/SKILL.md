---
name: psychophysiology
description: Peripheral autonomic and neuromuscular measures — skin conductance response (SCR/EDA), heart-rate variability (HRV), and respiration. See references/emg.md for electromyography specifically. Use this for peripheral physiological measures accompanying a neuroscience study, distinct from central nervous system recording.
license: MIT
allowed-tools: Read Write Edit Bash
compatibility: Examples use numpy/scipy/neurokit2. NeuroKit2 covers most of this skill's core signal types with a consistent API.
metadata:
  version: "1.0"
  skill-author: neuro-skills contributors
  category: psychophysiology
---

# Psychophysiology

## Overview

Peripheral physiological signals — skin conductance, heart rate/HRV, respiration — index autonomic
nervous system activity, commonly recorded alongside central measures (EEG, fMRI) as an index of
arousal, emotional response, or stress. NeuroKit2 provides a consistent processing API across most of
these signal types. See [references/emg.md](references/emg.md) for electromyography, which is
grouped here as another peripheral electrophysiological signal but has distinct analysis goals
(muscle activity/motor control, not autonomic state).

## When to use this skill

Activate when the request involves:
- Skin conductance, SCR, EDA, GSR, heart-rate variability, HRV, respiration, autonomic measures
- Terms: NeuroKit2, tonic/phasic, RMSSD, SDNN, LF/HF power, R-peak
- "Process this EDA/GSR signal," "compute HRV from ECG," "analyze event-related SCR"

## Core usage

### Skin conductance response (SCR/EDA)

```python
import neurokit2 as nk

eda_signals, info = nk.eda_process(eda_raw, sampling_rate=1000)
# eda_signals includes tonic (slow, baseline arousal) and phasic (fast, event-related) components
scr_amplitude = eda_signals["EDA_Phasic"]
scr_peaks = info["SCR_Peaks"]  # detected discrete response onsets
```

### Heart-rate variability

```python
ecg_signals, info = nk.ecg_process(ecg_raw, sampling_rate=1000)
hrv_indices = nk.hrv(info["ECG_R_Peaks"], sampling_rate=1000)
# hrv_indices includes time-domain (RMSSD, SDNN) and frequency-domain (LF/HF power) measures
```

### Respiration

```python
rsp_signals, info = nk.rsp_process(rsp_raw, sampling_rate=1000)
breathing_rate = rsp_signals["RSP_Rate"]
```

### Event-related analysis (common pattern across all three signal types)

```python
epochs = nk.epochs_create(eda_signals, events=event_onsets, sampling_rate=1000, epochs_start=-1, epochs_end=5)
scr_results = nk.eda_eventrelated(epochs)
```

## Validation & Pitfalls

Canonical reference: Boucsein, *Electrodermal Activity* (2nd ed., 2012), for EDA methodology;
Shaffer & Ginsberg (2017), "An overview of heart rate variability metrics and norms," *Frontiers in
Public Health*, for HRV.

- **SCR onset latency after a stimulus is slow (~1-3 seconds) relative to neural response latencies**
  — event-related SCR analysis windows must account for this lag; a window matched to a neural
  event-related response's typical timing will miss the SCR entirely.
- **HRV frequency-domain measures (LF/HF ratio specifically) have a contested interpretation in the
  literature** — the once-common claim that LF/HF directly indexes sympathovagal balance has been
  substantially challenged; report the specific measure computed rather than an interpretive label
  ("sympathetic activity") the measure doesn't unambiguously support on its own.
- **Movement artifacts affect all three signal types, through different mechanisms** — EDA electrodes
  can shift and introduce motion artifact resembling a phasic response; ECG can pick up motion-related
  baseline wander; respiration belts are directly displaced by posture change. Screen for movement
  artifact before treating any signal's peaks/events as physiological.
- **Recording sampling rate must be adequate for the signal's actual frequency content** — HRV
  frequency-domain measures specifically need sufficient recording duration and R-peak detection
  precision; a short recording or low ECG sampling rate produces unreliable frequency-domain HRV
  estimates even when time-domain measures (RMSSD) remain reasonable.
